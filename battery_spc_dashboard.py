import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


# ========== 1. 数据生成层（模拟10个反应釜，7天数据） ==========
def generate_batch_data(n_batches=100, seed=42):
    """
    生成模拟工艺数据：
    - 批次ID
    - 反应温度 (°C, 目标850±20)
    - 反应压力 (MPa, 目标2.5±0.3)
    - 保温时间 (min)
    - 合格率 (%)
    """
    rng = np.random.default_rng(seed)
    start_time = datetime.now() - timedelta(days=7)

    batch_ids = [f"BATCH_{i:03d}" for i in range(1, n_batches + 1)]
    reactor_ids = [f"R{(i % 10) + 1:02d}" for i in range(n_batches)]
    timestamps = [start_time + timedelta(minutes=100 * i) for i in range(n_batches)]

    temperatures = rng.normal(850, 15, n_batches)
    temp_anomaly_mask = rng.random(n_batches) < 0.08
    temperatures[temp_anomaly_mask] = rng.normal(900, 5, temp_anomaly_mask.sum())

    pressures = rng.normal(2.5, 0.2, n_batches)
    hold_time = rng.normal(180, 18, n_batches)

    temp_penalty = np.abs(temperatures - 850) * 0.85
    pressure_penalty = np.abs(pressures - 2.5) * 24
    hold_penalty = np.abs(hold_time - 180) * 0.12
    noise = rng.normal(0, 2.5, n_batches)

    yield_rate = 96 - temp_penalty - pressure_penalty - hold_penalty + noise
    yield_rate = np.clip(yield_rate, 70, 99.5)

    df = pd.DataFrame(
        {
            "batch_id": batch_ids,
            "reactor_id": reactor_ids,
            "timestamp": pd.to_datetime(timestamps),
            "temperature": np.round(temperatures, 2),
            "pressure": np.round(pressures, 3),
            "hold_time": np.round(hold_time, 1),
            "yield_rate": np.round(yield_rate, 2),
        }
    )
    return df


# ========== 2. 数据处理层（计算SPC指标） ==========
def calculate_spc(df):
    """
    计算关键指标的：
    - 均值、标准差
    - Cp, Cpk（过程能力指数）
    - 标红异常批次（温度超出控制限）
    """
    specs = {
        "temperature": {"target": 850, "lsl": 830, "usl": 870},
        "pressure": {"target": 2.5, "lsl": 2.2, "usl": 2.8},
        "yield_rate": {"target": 95, "lsl": 85, "usl": 100},
    }

    summary = {}
    for column, limits in specs.items():
        mean = float(df[column].mean())
        std = float(df[column].std(ddof=1))

        if std == 0 or np.isnan(std):
            cp = np.nan
            cpk = np.nan
        else:
            cp = (limits["usl"] - limits["lsl"]) / (6 * std)
            cpk = min(
                (limits["usl"] - mean) / (3 * std),
                (mean - limits["lsl"]) / (3 * std),
            )

        summary[column] = {
            "mean": round(mean, 4),
            "std": round(std, 4),
            "cp": round(cp, 4) if not np.isnan(cp) else np.nan,
            "cpk": round(cpk, 4) if not np.isnan(cpk) else np.nan,
            "target": limits["target"],
            "lsl": limits["lsl"],
            "usl": limits["usl"],
        }

    temp_mean = float(df["temperature"].mean())
    temp_std = float(df["temperature"].std(ddof=1))
    ucl = temp_mean + 3 * temp_std
    lcl = temp_mean - 3 * temp_std

    abnormal_mask = (df["temperature"] > ucl) | (df["temperature"] < lcl)
    abnormal_batches = df.loc[
        abnormal_mask, ["batch_id", "reactor_id", "timestamp", "temperature", "yield_rate"]
    ].copy()

    return {
        "summary": summary,
        "temperature_control_limits": {
            "center": round(temp_mean, 4),
            "ucl": round(ucl, 4),
            "lcl": round(lcl, 4),
        },
        "abnormal_batches": abnormal_batches,
    }


# ========== 3. 可视化层（Matplotlib静态图） ==========
def draw_dashboard(df, spc_result):
    """
    画出3个子图：
    - 温度趋势 + 控制线
    - 压力趋势
    - 合格率趋势 + 标红异常点
    """
    df_plot = df.sort_values("timestamp").reset_index(drop=True)
    abnormal_ids = set(spc_result["abnormal_batches"]["batch_id"])
    abnormal_yield = df_plot["batch_id"].isin(abnormal_ids)
    temp_limits = spc_result["temperature_control_limits"]

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    fig.suptitle("锂电池硅碳负极材料生产 SPC 看板", fontsize=16)

    axes[0].plot(df_plot["timestamp"], df_plot["temperature"], color="#d95f02", linewidth=1.6)
    axes[0].axhline(temp_limits["center"], color="#1b9e77", linestyle="--", label="中心线")
    axes[0].axhline(temp_limits["ucl"], color="#e7298a", linestyle="--", label="UCL")
    axes[0].axhline(temp_limits["lcl"], color="#e7298a", linestyle="--", label="LCL")
    axes[0].scatter(
        df_plot.loc[abnormal_yield, "timestamp"],
        df_plot.loc[abnormal_yield, "temperature"],
        color="red",
        s=40,
        label="异常批次",
        zorder=3,
    )
    axes[0].set_ylabel("温度 (°C)")
    axes[0].set_title("反应温度趋势")
    axes[0].grid(alpha=0.3)
    axes[0].legend(loc="upper right")

    axes[1].plot(df_plot["timestamp"], df_plot["pressure"], color="#7570b3", linewidth=1.6)
    axes[1].axhline(2.5, color="#1b9e77", linestyle="--", label="目标值")
    axes[1].axhline(2.8, color="#666666", linestyle=":", label="USL/LSL")
    axes[1].axhline(2.2, color="#666666", linestyle=":")
    axes[1].set_ylabel("压力 (MPa)")
    axes[1].set_title("反应压力趋势")
    axes[1].grid(alpha=0.3)
    axes[1].legend(loc="upper right")

    axes[2].plot(df_plot["timestamp"], df_plot["yield_rate"], color="#1f78b4", linewidth=1.6)
    axes[2].scatter(
        df_plot.loc[abnormal_yield, "timestamp"],
        df_plot.loc[abnormal_yield, "yield_rate"],
        color="red",
        s=40,
        label="异常批次",
        zorder=3,
    )
    axes[2].axhline(95, color="#1b9e77", linestyle="--", label="目标值")
    axes[2].set_ylabel("合格率 (%)")
    axes[2].set_title("合格率趋势")
    axes[2].grid(alpha=0.3)
    axes[2].legend(loc="lower right")
    axes[2].set_xlabel("时间")

    summary = spc_result["summary"]["temperature"]
    fig.text(
        0.02,
        0.02,
        (
            f"温度均值: {summary['mean']}°C   "
            f"标准差: {summary['std']}   "
            f"Cp: {summary['cp']}   "
            f"Cpk: {summary['cpk']}"
        ),
        fontsize=10,
    )

    plt.tight_layout(rect=[0, 0.04, 1, 0.97])

    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "spc_dashboard.png"
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


# ========== 主流程 ==========
if __name__ == "__main__":
    df = generate_batch_data()
    spc = calculate_spc(df)
    chart_path = draw_dashboard(df, spc)
    print("看板已生成")
    print(chart_path)
