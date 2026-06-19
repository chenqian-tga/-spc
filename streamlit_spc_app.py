from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

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
        .status-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.85rem;
            margin-bottom: 1rem;
        }
        .status-pill {
            background: rgba(255, 255, 255, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            padding: 0.85rem 0.95rem;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
        }
        .status-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #64748b;
            margin-bottom: 0.35rem;
        }
        .status-value {
            font-size: 1rem;
            font-weight: 700;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 0.42rem;
        }
        .signal-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            display: inline-block;
            box-shadow: 0 0 0 4px rgba(255,255,255,0.5);
        }
        .dark-panel {
            background:
                linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(17, 33, 54, 0.92) 100%);
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 28px;
            padding: 1.05rem 1.1rem;
            box-shadow: 0 24px 54px rgba(15, 23, 42, 0.18);
            margin-bottom: 1.1rem;
        }
        .dark-title {
            font-size: 0.78rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            font-weight: 700;
            color: rgba(191, 219, 254, 0.9);
            margin-bottom: 0.55rem;
        }
        .copilot-card {
            background:
                linear-gradient(180deg, rgba(7, 14, 28, 0.98) 0%, rgba(15, 23, 42, 0.94) 100%);
            border: 1px solid rgba(96, 165, 250, 0.14);
            border-radius: 28px;
            padding: 1.1rem 1.15rem;
            box-shadow: 0 24px 56px rgba(2, 6, 23, 0.22);
            margin-bottom: 1.1rem;
        }
        .copilot-head {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 0.7rem;
        }
        .copilot-badge {
            width: 34px;
            height: 34px;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(45,212,191,0.96), rgba(59,130,246,0.96));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.95rem;
            font-weight: 700;
            box-shadow: 0 12px 22px rgba(45,212,191,0.18);
        }
        .copilot-title {
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 700;
        }
        .copilot-subtitle {
            color: #94a3b8;
            font-size: 0.82rem;
            margin-top: 0.15rem;
        }
        .copilot-summary {
            color: #e2e8f0;
            line-height: 1.75;
            font-size: 0.95rem;
            margin-bottom: 0.7rem;
        }
        .copilot-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }
        .copilot-chip {
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid rgba(148, 163, 184, 0.14);
            color: #dbeafe;
            background: rgba(30, 41, 59, 0.72);
        }
        .copilot-actions {
            color: #cbd5e1;
            font-size: 0.9rem;
            line-height: 1.8;
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
        iframe[title="streamlit_echarts.st_echarts"] {
            border-radius: 20px;
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


def get_process_status(cp: float, abnormal_count: int) -> tuple[str, str, str]:
    if abnormal_count > 5 or (not np.isnan(cp) and cp < 1.0):
        return "告警", "#ef4444", "工艺波动已超过安全舒适区"
    if abnormal_count > 0 or (not np.isnan(cp) and cp < 1.33):
        return "关注", "#f59e0b", "过程能力偏紧，建议维持监控"
    return "稳定", "#14b8a6", "当前窗口运行平稳"


def get_shift_status(std: float) -> tuple[str, str]:
    if std > 18:
        return "波动偏大", "#ef4444"
    if std > 14:
        return "轻微偏移", "#f59e0b"
    return "控制良好", "#14b8a6"


def render_status_strip(cp: float, cpk: float, abnormal_count: int, std: float, low_yield_count: int) -> None:
    process_label, process_color, _ = get_process_status(cp, abnormal_count)
    shift_label, shift_color = get_shift_status(std)
    yield_label = "风险升高" if low_yield_count > 5 else ("轻度承压" if low_yield_count > 0 else "产出稳定")
    yield_color = "#ef4444" if low_yield_count > 5 else ("#f59e0b" if low_yield_count > 0 else "#14b8a6")
    center_label = "偏移明显" if (not np.isnan(cp) and not np.isnan(cpk) and cpk < cp * 0.8) else "中心稳定"
    center_color = "#f59e0b" if center_label == "偏移明显" else "#14b8a6"

    st.markdown(
        f"""
        <div class="status-strip">
            <div class="status-pill">
                <div class="status-label">Process State</div>
                <div class="status-value"><span class="signal-dot" style="background:{process_color};"></span>{process_label}</div>
            </div>
            <div class="status-pill">
                <div class="status-label">Thermal Spread</div>
                <div class="status-value"><span class="signal-dot" style="background:{shift_color};"></span>{shift_label}</div>
            </div>
            <div class="status-pill">
                <div class="status-label">Yield Signal</div>
                <div class="status-value"><span class="signal-dot" style="background:{yield_color};"></span>{yield_label}</div>
            </div>
            <div class="status-pill">
                <div class="status-label">Centering</div>
                <div class="status-value"><span class="signal-dot" style="background:{center_color};"></span>{center_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_copilot_card(cp: float, cpk: float, abnormal_count: int, total_count: int, low_yield_count: int, std: float) -> None:
    process_label, _, process_note = get_process_status(cp, abnormal_count)
    if abnormal_count > 5:
        primary_action = "优先排查加热/冷却系统和温控执行机构，确认异常是否集中在同一时间段或同一反应釜。"
    elif not np.isnan(cp) and cp < 1.33:
        primary_action = "建议短周期复核温度设定值、采样频率和设备漂移，避免过程能力继续收窄。"
    else:
        primary_action = "建议保持当前工艺窗口，并持续观察低合格率批次是否有聚集趋势。"

    if not np.isnan(cp) and not np.isnan(cpk) and cpk < cp * 0.8:
        secondary_action = "检测到中心偏移迹象，建议重新校准目标温度并核对偏差来源。"
    else:
        secondary_action = "当前中心偏移不明显，可将优化重点放在波动压缩而非目标值重设。"

    st.markdown(
        f"""
        <div class="copilot-card">
            <div class="copilot-head">
                <div class="copilot-badge">AI</div>
                <div>
                    <div class="copilot-title">智能副驾判读</div>
                    <div class="copilot-subtitle">基于 Cp / Cpk / 异常批次 / 合格率阈值的即时建议</div>
                </div>
            </div>
            <div class="copilot-summary">
                当前系统状态判定为 <strong>{process_label}</strong>。{process_note} 目前共监控 <strong>{total_count}</strong> 个批次，
                温度标准差为 <strong>{std:.2f}</strong>，异常批次 <strong>{abnormal_count}</strong> 个，
                低于合格率阈值的批次 <strong>{low_yield_count}</strong> 个。
            </div>
            <div class="copilot-chip-row">
                <div class="copilot-chip">Cp {0.0 if np.isnan(cp) else cp:.3f}</div>
                <div class="copilot-chip">Cpk {0.0 if np.isnan(cpk) else cpk:.3f}</div>
                <div class="copilot-chip">异常 {abnormal_count}/{total_count}</div>
                <div class="copilot-chip">低合格率 {low_yield_count}</div>
            </div>
            <div class="copilot-actions">
                1. {primary_action}<br/>
                2. {secondary_action}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filter_dataframe(df: pd.DataFrame, reactor_options: list[str], time_window: tuple[pd.Timestamp, pd.Timestamp]) -> pd.DataFrame:
    start_time, end_time = time_window
    filtered = df[df["reactor_id"].isin(reactor_options)].copy()
    return filtered[(filtered["timestamp"] >= start_time) & (filtered["timestamp"] <= end_time)].reset_index(drop=True)


def _base_echarts_options() -> dict:
    return {
        "animationDuration": 700,
        "animationEasing": "cubicOut",
        "backgroundColor": "transparent",
        "grid": {"left": 54, "right": 24, "top": 56, "bottom": 54, "containLabel": True},
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(15, 23, 42, 0.92)",
            "borderColor": "rgba(148, 163, 184, 0.22)",
            "textStyle": {"color": "#f8fafc"},
        },
        "axisPointer": {"lineStyle": {"color": "rgba(29, 78, 216, 0.45)", "type": "dashed"}},
        "legend": {"top": 8, "textStyle": {"color": "#44505c", "fontSize": 12}},
        "toolbox": {
            "right": 6,
            "feature": {
                "dataZoom": {"yAxisIndex": "none"},
                "restore": {},
                "saveAsImage": {},
            },
            "iconStyle": {"borderColor": "#587086"},
        },
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "axisLine": {"lineStyle": {"color": "rgba(88, 112, 134, 0.34)"}},
            "axisLabel": {"color": "#5f6e78", "fontSize": 11},
            "splitLine": {"show": False},
        },
        "yAxis": {
            "type": "value",
            "axisLine": {"show": False},
            "axisLabel": {"color": "#5f6e78", "fontSize": 11},
            "splitLine": {"lineStyle": {"color": "rgba(88, 112, 134, 0.10)"}},
        },
        "dataZoom": [
            {"type": "inside", "start": 0, "end": 100},
            {
                "type": "slider",
                "height": 18,
                "bottom": 10,
                "borderColor": "rgba(88, 112, 134, 0.16)",
                "fillerColor": "rgba(29, 78, 216, 0.12)",
                "backgroundColor": "rgba(255, 255, 255, 0.62)",
            },
        ],
    }


def _dark_echarts_options() -> dict:
    options = _base_echarts_options()
    options.update(
        {
            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "rgba(2, 6, 23, 0.94)",
                "borderColor": "rgba(148, 163, 184, 0.18)",
                "textStyle": {"color": "#e2e8f0"},
            },
            "legend": {"top": 8, "textStyle": {"color": "#cbd5e1", "fontSize": 12}},
            "toolbox": {
                "right": 6,
                "feature": {
                    "dataZoom": {"yAxisIndex": "none"},
                    "restore": {},
                    "saveAsImage": {},
                },
                "iconStyle": {"borderColor": "#cbd5e1"},
            },
            "xAxis": {
                **options["xAxis"],
                "axisLine": {"lineStyle": {"color": "rgba(148, 163, 184, 0.24)"}},
                "axisLabel": {"color": "#94a3b8", "fontSize": 11},
            },
            "yAxis": {
                **options["yAxis"],
                "axisLabel": {"color": "#94a3b8", "fontSize": 11},
                "splitLine": {"lineStyle": {"color": "rgba(148, 163, 184, 0.08)"}},
            },
            "dataZoom": [
                {"type": "inside", "start": 0, "end": 100},
                {
                    "type": "slider",
                    "height": 18,
                    "bottom": 10,
                    "borderColor": "rgba(148, 163, 184, 0.10)",
                    "fillerColor": "rgba(45, 212, 191, 0.15)",
                    "backgroundColor": "rgba(15, 23, 42, 0.76)",
                    "textStyle": {"color": "#94a3b8"},
                },
            ],
        }
    )
    return options


def build_summary_gauge(cp: float, cpk: float, abnormal_count: int) -> dict:
    if np.isnan(cp):
        cp = 0.0
    health_score = max(0, min(100, int(cp / 1.67 * 100)))
    cpk_value = 0.0 if np.isnan(cpk) else round(cpk, 3)

    return {
        "backgroundColor": "transparent",
        "series": [
            {
                "type": "gauge",
                "center": ["50%", "58%"],
                "radius": "90%",
                "startAngle": 210,
                "endAngle": -30,
                "min": 0,
                "max": 100,
                "splitNumber": 5,
                "progress": {"show": True, "width": 16, "roundCap": True},
                "axisLine": {
                    "lineStyle": {
                        "width": 16,
                        "color": [
                            [0.5, "#dc2626"],
                            [0.8, "#f59e0b"],
                            [1, "#14b8a6"],
                        ],
                    }
                },
                "axisTick": {"show": False},
                "splitLine": {"length": 14, "lineStyle": {"width": 2, "color": "#64748b"}},
                "axisLabel": {"distance": 20, "color": "#cbd5e1", "fontSize": 11},
                "pointer": {"show": True, "length": "62%", "width": 4},
                "anchor": {"show": True, "showAbove": True, "size": 12, "itemStyle": {"color": "#e2e8f0"}},
                "title": {"show": True, "offsetCenter": [0, "74%"], "color": "#94a3b8", "fontSize": 12},
                "detail": {
                    "valueAnimation": True,
                    "formatter": "{value}",
                    "color": "#f8fafc",
                    "fontSize": 24,
                    "offsetCenter": [0, "18%"],
                },
                "data": [{"value": health_score, "name": "过程健康评分"}],
            }
        ],
        "graphic": [
            {
                "type": "text",
                "left": "center",
                "top": "12%",
                "style": {"text": f"Cpk {cpk_value:.3f}", "fill": "#cbd5e1", "font": "500 14px IBM Plex Sans"},
            },
            {
                "type": "text",
                "left": "center",
                "top": "84%",
                "style": {"text": f"异常 {abnormal_count} 批", "fill": "#94a3b8", "font": "500 12px IBM Plex Sans"},
            },
        ],
    }


def build_abnormal_donut(abnormal_count: int, total_count: int) -> dict:
    normal_count = max(total_count - abnormal_count, 0)
    return {
        "backgroundColor": "transparent",
        "tooltip": {"trigger": "item"},
        "legend": {
            "bottom": 0,
            "textStyle": {"color": "#cbd5e1", "fontSize": 11},
        },
        "series": [
            {
                "name": "批次分布",
                "type": "pie",
                "radius": ["58%", "78%"],
                "center": ["50%", "48%"],
                "avoidLabelOverlap": False,
                "label": {"show": False},
                "labelLine": {"show": False},
                "itemStyle": {"borderColor": "#0f172a", "borderWidth": 2},
                "data": [
                    {"value": normal_count, "name": "正常批次", "itemStyle": {"color": "#14b8a6"}},
                    {"value": abnormal_count, "name": "异常批次", "itemStyle": {"color": "#ef4444"}},
                ],
            }
        ],
        "graphic": [
            {
                "type": "text",
                "left": "center",
                "top": "38%",
                "style": {"text": str(total_count), "fill": "#f8fafc", "font": "700 26px Azeret Mono"},
            },
            {
                "type": "text",
                "left": "center",
                "top": "53%",
                "style": {"text": "总批次", "fill": "#94a3b8", "font": "500 12px IBM Plex Sans"},
            },
        ],
    }


def build_temperature_chart_options(df: pd.DataFrame, target_temperature: float, ucl: float, lcl: float) -> dict:
    labels = df["timestamp"].dt.strftime("%m-%d %H:%M").tolist()
    values = df["temperature"].round(2).tolist()
    abnormal_points = [
        [labels[idx], values[idx]]
        for idx, value in enumerate(values)
        if value > ucl or value < lcl
    ]
    options = _dark_echarts_options()
    options.update(
        {
            "legend": {"data": ["温度", "异常点"], "top": 8, "textStyle": {"color": "#cbd5e1", "fontSize": 12}},
            "xAxis": {**options["xAxis"], "data": labels},
            "yAxis": {**options["yAxis"], "name": "温度 (°C)", "nameTextStyle": {"color": "#94a3b8"}},
            "series": [
                {
                    "name": "温度",
                    "type": "line",
                    "smooth": True,
                    "symbol": "none",
                    "lineStyle": {"width": 3, "color": "#fb923c"},
                    "areaStyle": {
                        "color": {
                            "type": "linear",
                            "x": 0,
                            "y": 0,
                            "x2": 0,
                            "y2": 1,
                            "colorStops": [
                                {"offset": 0, "color": "rgba(251, 146, 60, 0.26)"},
                                {"offset": 1, "color": "rgba(251, 146, 60, 0.02)"},
                            ],
                        }
                    },
                    "data": values,
                    "markLine": {
                        "silent": True,
                        "symbol": "none",
                        "label": {"color": "#cbd5e1"},
                        "data": [
                            {"name": "目标温度", "yAxis": round(target_temperature, 2), "lineStyle": {"color": "#2dd4bf", "type": "dashed"}},
                            {"name": "UCL", "yAxis": round(ucl, 2), "lineStyle": {"color": "#f87171", "type": "dashed"}},
                            {"name": "LCL", "yAxis": round(lcl, 2), "lineStyle": {"color": "#f87171", "type": "dashed"}},
                        ],
                    },
                },
                {
                    "name": "异常点",
                    "type": "scatter",
                    "data": abnormal_points,
                    "symbolSize": 9,
                    "itemStyle": {"color": "#f87171", "shadowBlur": 14, "shadowColor": "rgba(248,113,113,0.28)"},
                },
            ],
        }
    )
    return options


def build_pressure_chart_options(df: pd.DataFrame) -> dict:
    labels = df["timestamp"].dt.strftime("%m-%d %H:%M").tolist()
    values = df["pressure"].round(3).tolist()
    options = _dark_echarts_options()
    options.update(
        {
            "legend": {"data": ["压力"], "top": 8, "textStyle": {"color": "#cbd5e1", "fontSize": 12}},
            "xAxis": {**options["xAxis"], "data": labels},
            "yAxis": {**options["yAxis"], "name": "压力 (MPa)", "nameTextStyle": {"color": "#94a3b8"}},
            "series": [
                {
                    "name": "压力",
                    "type": "line",
                    "smooth": True,
                    "symbol": "none",
                    "lineStyle": {"width": 3, "color": "#60a5fa"},
                    "areaStyle": {
                        "color": {
                            "type": "linear",
                            "x": 0,
                            "y": 0,
                            "x2": 0,
                            "y2": 1,
                            "colorStops": [
                                {"offset": 0, "color": "rgba(96, 165, 250, 0.22)"},
                                {"offset": 1, "color": "rgba(96, 165, 250, 0.02)"},
                            ],
                        }
                    },
                    "data": values,
                    "markLine": {
                        "silent": True,
                        "symbol": "none",
                        "label": {"color": "#cbd5e1"},
                        "data": [
                            {"name": "目标压力", "yAxis": 2.5, "lineStyle": {"color": "#2dd4bf", "type": "dashed"}},
                        ],
                    },
                }
            ],
        }
    )
    return options


def build_yield_chart_options(df: pd.DataFrame, anomaly_threshold: float) -> dict:
    labels = df["timestamp"].dt.strftime("%m-%d %H:%M").tolist()
    normal_data = []
    abnormal_data = []
    for idx, row in df.iterrows():
        item = {
            "value": [labels[idx], round(float(row["yield_rate"]), 2)],
            "batch_id": row["batch_id"],
            "temperature": round(float(row["temperature"]), 2),
            "pressure": round(float(row["pressure"]), 3),
        }
        if row["yield_rate"] < anomaly_threshold:
            abnormal_data.append(item)
        else:
            normal_data.append(item)

    options = _dark_echarts_options()
    options["tooltip"] = {
        "trigger": "item",
        "backgroundColor": "rgba(2, 6, 23, 0.94)",
        "borderColor": "rgba(148, 163, 184, 0.22)",
        "textStyle": {"color": "#f8fafc"},
        "formatter": """
        function(params) {
            const data = params.data;
            return `${data.batch_id}<br/>时间: ${data.value[0]}<br/>合格率: ${data.value[1]}%<br/>温度: ${data.temperature}°C<br/>压力: ${data.pressure} MPa`;
        }
        """,
    }
    options.update(
        {
            "legend": {"data": ["正常", "低于阈值"], "top": 8, "textStyle": {"color": "#cbd5e1", "fontSize": 12}},
            "xAxis": {**options["xAxis"], "data": labels},
            "yAxis": {**options["yAxis"], "name": "合格率 (%)", "nameTextStyle": {"color": "#94a3b8"}},
            "series": [
                {
                    "name": "正常",
                    "type": "scatter",
                    "data": normal_data,
                    "symbolSize": 11,
                    "itemStyle": {"color": "#2dd4bf", "opacity": 0.9},
                },
                {
                    "name": "低于阈值",
                    "type": "scatter",
                    "data": abnormal_data,
                    "symbolSize": 13,
                    "itemStyle": {"color": "#f87171", "shadowBlur": 12, "shadowColor": "rgba(248,113,113,0.28)"},
                    "markLine": {
                        "silent": True,
                        "symbol": "none",
                        "label": {"color": "#cbd5e1"},
                        "data": [
                            {"name": "异常阈值", "yAxis": round(anomaly_threshold, 2), "lineStyle": {"color": "#f87171", "type": "dashed"}},
                        ],
                    },
                },
            ],
        }
    )
    return options


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

    abnormal_count = len(spc_result["abnormal_df"])
    low_yield_mask = df["yield_rate"] < anomaly_threshold
    low_yield_count = int(low_yield_mask.sum())

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
    render_status_strip(spc_result["Cp"], spc_result["Cpk"], abnormal_count, spc_result["std"], low_yield_count)

    col1, col2, col3 = st.columns(3)
    col1.metric("Cp 指标", f"{spc_result['Cp']:.3f}" if not np.isnan(spc_result["Cp"]) else "N/A")
    col2.metric("Cpk 指标", f"{spc_result['Cpk']:.3f}" if not np.isnan(spc_result["Cpk"]) else "N/A")
    col3.metric("异常批次数量", f"{abnormal_count}")

    gauge_col, donut_col, insight_col = st.columns([1.1, 1.1, 1.6])
    with gauge_col:
        st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dark-title">Process Health</div>', unsafe_allow_html=True)
        st_echarts(
            options=build_summary_gauge(spc_result["Cp"], spc_result["Cpk"], abnormal_count),
            height="280px",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with donut_col:
        st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dark-title">Batch Mix</div>', unsafe_allow_html=True)
        st_echarts(
            options=build_abnormal_donut(abnormal_count, len(df)),
            height="280px",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with insight_col:
        render_copilot_card(
            spc_result["Cp"],
            spc_result["Cpk"],
            abnormal_count,
            len(df),
            low_yield_count,
            spc_result["std"],
        )

    overview_left, overview_right = st.columns([2.2, 1.1])
    with overview_left:
        st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dark-title">工艺趋势总览</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="color:#94a3b8;font-size:0.93rem;line-height:1.6;margin-bottom:0.65rem;">借鉴 ECharts Demo 的交互思路，加入缩放、图层控制和导出能力，适合更专业的展示与分析。</div>',
            unsafe_allow_html=True,
        )
        st_echarts(
            options=build_temperature_chart_options(df, target_temperature, spc_result["UCL"], spc_result["LCL"]),
            height="360px",
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
        st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dark-title">压力趋势</div>', unsafe_allow_html=True)
        st_echarts(
            options=build_pressure_chart_options(df),
            height="320px",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with chart_col2:
        st.markdown('<div class="dark-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dark-title">合格率散点图</div>', unsafe_allow_html=True)
        st_echarts(
            options=build_yield_chart_options(df, anomaly_threshold),
            height="320px",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if low_yield_mask.any():
        st.caption(f"当前有 {low_yield_count} 个批次的合格率低于异常阈值 {anomaly_threshold:.0f}%。")
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
