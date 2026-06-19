from __future__ import annotations

from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from battery_spc_dashboard import generate_batch_data


st.set_page_config(page_title="锂电池 SPC 交互看板", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Azeret+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

        :root {
            --bg-1: #f3f5f7;
            --bg-2: #e8edf1;
            --ink-1: #13212b;
            --ink-2: #5f6e78;
            --line: rgba(19, 33, 43, 0.08);
            --card: rgba(255, 255, 255, 0.72);
            --card-strong: rgba(255, 255, 255, 0.86);
            --shadow: 0 18px 40px rgba(17, 28, 38, 0.08);
            --accent: #0f766e;
            --accent-2: #1d4ed8;
            --alert: #b42318;
        }
        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(15, 118, 110, 0.14), transparent 24%),
                radial-gradient(circle at 88% 12%, rgba(29, 78, 216, 0.12), transparent 22%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
            color: var(--ink-1);
            font-family: "IBM Plex Sans", sans-serif;
        }
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2.4rem;
            max-width: 1480px;
        }
        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(19, 33, 43, 0.96) 0%, rgba(20, 38, 52, 0.94) 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }
        [data-testid="stSidebar"] * {
            color: #edf3f7 !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: rgba(237, 243, 247, 0.78) !important;
        }
        [data-testid="stSidebar"] .stNumberInput input,
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"],
        [data-testid="stSidebar"] .stDateInput input,
        [data-testid="stSidebar"] .stSlider {
            font-family: "IBM Plex Sans", sans-serif;
        }
        [data-testid="stSidebar"] .stButton button,
        [data-testid="stSidebar"] .stFormSubmitButton button {
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.14);
            background: linear-gradient(135deg, rgba(14, 165, 164, 0.92), rgba(29, 78, 216, 0.92));
            color: white !important;
            font-weight: 600;
            letter-spacing: 0.02em;
            box-shadow: 0 10px 24px rgba(14, 165, 164, 0.18);
        }
        .dashboard-card {
            background: linear-gradient(180deg, var(--card-strong) 0%, var(--card) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.15rem 1.2rem;
            box-shadow: var(--shadow);
            margin-bottom: 1.1rem;
        }
        .section-title {
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--accent-2);
            margin-bottom: 0.5rem;
        }
        .section-note {
            color: var(--ink-2);
            font-size: 0.93rem;
            line-height: 1.5;
            margin-bottom: 0.6rem;
        }
        .hero-card {
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(24, 54, 83, 0.88)),
                radial-gradient(circle at top right, rgba(45, 212, 191, 0.20), transparent 24%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 30px;
            padding: 1.35rem 1.45rem;
            color: white;
            box-shadow: 0 24px 54px rgba(15, 23, 42, 0.16);
            margin-bottom: 1.15rem;
            position: relative;
            overflow: hidden;
        }
        .hero-card::after {
            content: "";
            position: absolute;
            inset: auto -40px -40px auto;
            width: 160px;
            height: 160px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(45, 212, 191, 0.18), transparent 70%);
        }
        .hero-title {
            font-size: 1.28rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.35rem;
        }
        .hero-note {
            font-size: 0.96rem;
            line-height: 1.6;
            color: rgba(242, 247, 251, 0.92);
        }
        .compact-note {
            color: rgba(237, 243, 247, 0.72);
            font-size: 0.85rem;
            margin-top: 0.4rem;
            line-height: 1.5;
        }
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(248,250,252,0.76) 100%);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 0.95rem 1rem;
            box-shadow: var(--shadow);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.76rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--ink-2);
        }
        [data-testid="stMetricValue"] {
            font-family: "Azeret Mono", monospace;
            font-size: 1.55rem;
            color: var(--ink-1);
            letter-spacing: -0.03em;
        }
        .stExpander {
            border: 1px solid var(--line) !important;
            border-radius: 18px !important;
            background: rgba(248, 250, 252, 0.72) !important;
        }
        .stDownloadButton button {
            border-radius: 999px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.9);
            color: var(--ink-1);
            font-weight: 600;
        }
        .stAlert {
            border-radius: 18px;
        }
        .stDataFrame {
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid var(--line);
            box-shadow: var(--shadow);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_batch_data(seed: int, batch_count: int) -> pd.DataFrame:
    df = generate_batch_data(n_batches=batch_count, seed=seed)
    return df.sort_values("timestamp").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def calculate_spc(
    df: pd.DataFrame,
    target_temperature: float = 850.0,
    sigma_multiplier: float = 3.0,
) -> dict:
    temp_mean = float(df["temperature"].mean())
    temp_std = float(df["temperature"].std(ddof=1))

    usl = target_temperature + 20
    lsl = target_temperature - 20

    if temp_std == 0 or np.isnan(temp_std):
        cp = np.nan
        cpk = np.nan
    else:
        cp = (usl - lsl) / (6 * temp_std)
        cpk = min(
            (usl - temp_mean) / (3 * temp_std),
            (temp_mean - lsl) / (3 * temp_std),
        )

    ucl = temp_mean + sigma_multiplier * temp_std
    lcl = temp_mean - sigma_multiplier * temp_std

    abnormal_mask = (df["temperature"] > ucl) | (df["temperature"] < lcl)
    abnormal_df = df.loc[
        abnormal_mask,
        ["batch_id", "timestamp", "temperature", "pressure", "yield_rate"],
    ].copy()

    return {
        "Cp": round(float(cp), 4) if not np.isnan(cp) else np.nan,
        "Cpk": round(float(cpk), 4) if not np.isnan(cpk) else np.nan,
        "UCL": round(float(ucl), 4),
        "LCL": round(float(lcl), 4),
        "mean": round(float(temp_mean), 4),
        "std": round(float(temp_std), 4),
        "abnormal_df": abnormal_df,
    }


def highlight_abnormal_rows(row: pd.Series) -> list[str]:
    return ["background-color: #ffe5e5; color: #a40000; font-weight: 600;"] * len(row)


def render_diagnosis(cp: float, cpk: float, abnormal_count: int) -> None:
    with st.expander("查看详细诊断建议", expanded=True):
        if np.isnan(cp):
            st.warning("当前 Cp 无法计算，请检查数据波动或样本数量。")
        elif cp < 1.0:
            st.error("🔴 过程能力严重不足(Cp<1.0)，建议立即停机检查设备稳定性")
        elif cp < 1.33:
            st.warning("🟠 过程能力临界(Cp<1.33)，建议加强巡检频率")
        else:
            st.success("🟢 过程能力充足，维持当前工艺参数")

        if not np.isnan(cp) and not np.isnan(cpk) and cpk < cp * 0.8:
            st.warning("🟠 中心偏移明显，建议重新校准目标温度")

        if abnormal_count > 5:
            st.error(f"🔴 异常批次达{abnormal_count}批，建议排查加热/冷却系统")
        elif abnormal_count == 0:
            st.success("🟢 当前无异常，工艺状态稳定")


def filter_dataframe(df: pd.DataFrame, reactor_options: list[str], time_window: tuple[pd.Timestamp, pd.Timestamp]) -> pd.DataFrame:
    start_time, end_time = time_window
    filtered = df[df["reactor_id"].isin(reactor_options)].copy()
    return filtered[(filtered["timestamp"] >= start_time) & (filtered["timestamp"] <= end_time)].reset_index(drop=True)


def build_temperature_chart(df: pd.DataFrame, target_temperature: float, ucl: float, lcl: float) -> alt.Chart:
    chart_df = df[["timestamp", "temperature"]].copy()
    rule_df = pd.DataFrame(
        {
            "label": ["目标温度", "UCL", "LCL"],
            "value": [target_temperature, ucl, lcl],
        }
    )

    base = alt.Chart(chart_df).encode(x=alt.X("timestamp:T", title="时间"))
    line = base.mark_line(color="#d95f02", strokeWidth=2).encode(
        y=alt.Y("temperature:Q", title="温度 (°C)"),
        tooltip=[
            alt.Tooltip("timestamp:T", title="时间"),
            alt.Tooltip("temperature:Q", title="温度", format=".2f"),
        ],
    )

    rules = (
        alt.Chart(rule_df)
        .mark_rule(strokeDash=[6, 4], strokeWidth=1.8)
        .encode(
            y="value:Q",
            color=alt.Color(
                "label:N",
                scale=alt.Scale(
                    domain=["目标温度", "UCL", "LCL"],
                    range=["#1b9e77", "#c1121f", "#c1121f"],
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=[alt.Tooltip("label:N", title="控制线"), alt.Tooltip("value:Q", title="数值", format=".2f")],
        )
    )

    return (line + rules).properties(height=280).interactive()


def build_pressure_chart(df: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(df).encode(x=alt.X("timestamp:T", title="时间"))
    line = base.mark_line(color="#5b6cfa", strokeWidth=2).encode(
        y=alt.Y("pressure:Q", title="压力 (MPa)"),
        tooltip=[
            alt.Tooltip("timestamp:T", title="时间"),
            alt.Tooltip("pressure:Q", title="压力", format=".3f"),
        ],
    )
    target_rule = alt.Chart(pd.DataFrame({"value": [2.5]})).mark_rule(
        color="#1b9e77", strokeDash=[6, 4], strokeWidth=1.8
    ).encode(y="value:Q")
    return (line + target_rule).properties(height=260).interactive()


def build_yield_chart(df: pd.DataFrame, anomaly_threshold: float) -> alt.Chart:
    scatter_df = df.copy()
    scatter_df["yield_status"] = np.where(scatter_df["yield_rate"] < anomaly_threshold, "低于阈值", "正常")

    points = (
        alt.Chart(scatter_df)
        .mark_circle(size=72, opacity=0.85)
        .encode(
            x=alt.X("timestamp:T", title="时间"),
            y=alt.Y("yield_rate:Q", title="合格率 (%)"),
            color=alt.Color(
                "yield_status:N",
                scale=alt.Scale(domain=["正常", "低于阈值"], range=["#1f78b4", "#d62828"]),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=[
                alt.Tooltip("batch_id:N", title="批次"),
                alt.Tooltip("timestamp:T", title="时间"),
                alt.Tooltip("yield_rate:Q", title="合格率", format=".2f"),
                alt.Tooltip("temperature:Q", title="温度", format=".2f"),
                alt.Tooltip("pressure:Q", title="压力", format=".3f"),
            ],
        )
    )
    threshold_rule = alt.Chart(pd.DataFrame({"value": [anomaly_threshold]})).mark_rule(
        color="#d62828", strokeDash=[6, 4], strokeWidth=1.8
    ).encode(y="value:Q")
    return (points + threshold_rule).properties(height=260).interactive()


def main() -> None:
    inject_styles()

    if "seed" not in st.session_state:
        st.session_state.seed = 42
    if "target_temperature" not in st.session_state:
        st.session_state.target_temperature = 850.0
    if "sigma_multiplier" not in st.session_state:
        st.session_state.sigma_multiplier = 3.0
    if "anomaly_threshold" not in st.session_state:
        st.session_state.anomaly_threshold = 85.0
    if "batch_count" not in st.session_state:
        st.session_state.batch_count = 100

    base_df = load_batch_data(st.session_state.seed, st.session_state.batch_count)
    reactor_choices = sorted(base_df["reactor_id"].unique().tolist())
    time_min = base_df["timestamp"].min().to_pydatetime()
    time_max = base_df["timestamp"].max().to_pydatetime()

    with st.sidebar:
        st.header("控制参数")
        with st.form("controls_form", border=False):
            target_temperature = st.number_input(
                "目标温度 (°C)",
                value=float(st.session_state.target_temperature),
                step=1.0,
            )
            sigma_multiplier = st.slider(
                "控制限倍数",
                min_value=1.0,
                max_value=5.0,
                value=float(st.session_state.sigma_multiplier),
                step=0.5,
            )
            anomaly_threshold = st.slider(
                "异常阈值：最低合格率 (%)",
                min_value=70.0,
                max_value=99.0,
                value=float(st.session_state.anomaly_threshold),
                step=1.0,
            )
            reactor_filter = st.multiselect(
                "反应釜筛选",
                options=reactor_choices,
                default=reactor_choices,
            )
            time_range = st.slider(
                "时间范围",
                min_value=time_min,
                max_value=time_max,
                value=(time_min, time_max),
                format="YYYY-MM-DD HH:mm",
            )
            submitted = st.form_submit_button("应用参数", use_container_width=True)

        if submitted:
            st.session_state.target_temperature = target_temperature
            st.session_state.sigma_multiplier = sigma_multiplier
            st.session_state.anomaly_threshold = anomaly_threshold
        else:
            target_temperature = float(st.session_state.target_temperature)
            sigma_multiplier = float(st.session_state.sigma_multiplier)
            anomaly_threshold = float(st.session_state.anomaly_threshold)

        if st.button("重新生成数据", use_container_width=True):
            st.session_state.seed = int(np.random.default_rng().integers(1, 1_000_000))
            st.rerun()

        st.caption(f"当前随机种子：`{st.session_state.seed}`")
        st.markdown('<div class="compact-note">拖动筛选条件后，点击“应用参数”再刷新主界面，操作会更流畅。</div>', unsafe_allow_html=True)

    if not reactor_filter:
        reactor_filter = reactor_choices

    df = filter_dataframe(base_df, reactor_filter, time_range)
    if df.empty:
        st.warning("当前筛选条件下没有数据，请放宽时间范围或重新选择反应釜。")
        return

    spc_result = calculate_spc(
        df,
        target_temperature=target_temperature,
        sigma_multiplier=sigma_multiplier,
    )

    abnormal_ids = set(spc_result["abnormal_df"]["batch_id"])
    abnormal_count = len(spc_result["abnormal_df"])
    low_yield_mask = df["yield_rate"] < anomaly_threshold

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">锂电池硅碳负极材料生产 SPC 交互看板</div>
            <div class="hero-note">
                当前展示 <strong>{len(df)}</strong> 个批次，覆盖 <strong>{len(reactor_filter)}</strong> 台反应釜，
                时间区间为 <strong>{df["timestamp"].min().strftime("%Y-%m-%d %H:%M")}</strong> 至
                <strong>{df["timestamp"].max().strftime("%Y-%m-%d %H:%M")}</strong>。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Cp 指标", f"{spc_result['Cp']:.3f}" if not np.isnan(spc_result["Cp"]) else "N/A")
    col2.metric("Cpk 指标", f"{spc_result['Cpk']:.3f}" if not np.isnan(spc_result["Cpk"]) else "N/A")
    col3.metric("异常批次数量", f"{abnormal_count}")

    overview_left, overview_right = st.columns([2.2, 1.1])
    with overview_left:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">工艺趋势总览</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-note">温度图保留目标线与控制线，支持拖拽缩放，适合现场汇报时聚焦异常时段。</div>',
            unsafe_allow_html=True,
        )
        st.altair_chart(
            build_temperature_chart(df, target_temperature, spc_result["UCL"], spc_result["LCL"]),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with overview_right:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">当前判读</div>', unsafe_allow_html=True)
        st.write(f"温度均值：`{spc_result['mean']:.2f} °C`")
        st.write(f"温度标准差：`{spc_result['std']:.2f}`")
        st.write(f"温度控制区间：`{spc_result['LCL']:.2f} ~ {spc_result['UCL']:.2f} °C`")
        st.write(f"合格率异常阈值：`{anomaly_threshold:.0f}%`")
        st.write(f"温度超限批次：`{abnormal_count}` / `{len(df)}`")
        render_diagnosis(spc_result["Cp"], spc_result["Cpk"], abnormal_count)
        st.markdown("</div>", unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">压力趋势</div>', unsafe_allow_html=True)
        st.altair_chart(build_pressure_chart(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with chart_col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">合格率散点图</div>', unsafe_allow_html=True)
        st.altair_chart(build_yield_chart(df, anomaly_threshold), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if low_yield_mask.any():
        st.caption(f"当前有 {int(low_yield_mask.sum())} 个批次的合格率低于异常阈值 {anomaly_threshold:.0f}%。")
    else:
        st.caption("当前没有批次低于合格率异常阈值。")

    st.subheader("异常批次明细")
    if spc_result["abnormal_df"].empty:
        st.info("当前控制限下没有温度超限批次。")
    else:
        abnormal_table = spc_result["abnormal_df"].copy()
        abnormal_table["timestamp"] = abnormal_table["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        styled_table = abnormal_table.style.apply(highlight_abnormal_rows, axis=1)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
        csv_bytes = abnormal_table.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            "导出异常批次 CSV",
            data=csv_bytes,
            file_name="abnormal_batches.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
