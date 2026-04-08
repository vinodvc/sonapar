import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import anthropic
import json
from data import get_sku_data, get_opco_data

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sonepar Nexus | Distribution Orchestrator",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Sonepar brand palette ──────────────────────────────────────────────────────
BLUE      = "#003DA5"
BLUE_LT   = "#0050D0"
ORANGE    = "#FF6B00"
GREEN     = "#00875A"
RED       = "#DE350B"
WARN      = "#FF8B00"
GREY_TXT  = "#6B7A99"
INK       = "#0A1628"
BG_PAGE   = "#F4F6FA"
BG_WHITE  = "#FFFFFF"
BG_CHART  = "#F8F9FC"
GRID      = "#E0E6F0"
MONO      = "DM Mono"

# ── Helpers ────────────────────────────────────────────────────────────────────
def rgba(hex_color: str, alpha: float = 0.15) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def base_layout(height: int = 300, margin: dict = None) -> dict:
    m = margin or dict(l=10, r=10, t=20, b=10)
    return dict(
        paper_bgcolor=BG_WHITE, plot_bgcolor=BG_CHART,
        font=dict(family=MONO, color=INK, size=11),
        xaxis=dict(gridcolor=GRID, color=GREY_TXT, linecolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, color=GREY_TXT, linecolor=GRID, zerolinecolor=GRID),
        margin=m, height=height,
        legend=dict(bgcolor=BG_WHITE, bordercolor=GRID, borderwidth=1,
                    font=dict(size=10, color=INK)),
    )

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #0A1628; }
.stApp { background-color: #F4F6FA; }
.block-container { padding: 1.2rem 2rem 2rem 2rem; max-width: 1440px; }
#MainMenu, footer, header { visibility: hidden; }

.app-header {
    background: linear-gradient(135deg, #003DA5 0%, #0050D0 100%);
    border-radius: 12px; padding: 1.2rem 2rem; margin-bottom: 1.1rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 4px 20px rgba(0,61,165,0.22);
}
.app-title { font-size: 1.4rem; font-weight: 700; color: #FFF; letter-spacing: -0.3px; }
.app-title span { color: #FF6B00; }
.app-sub { font-size: 0.68rem; color: rgba(255,255,255,0.6);
           font-family: 'DM Mono', monospace; margin-top: 3px; letter-spacing: 0.5px; }
.live-badge { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.35);
              color: #FFF; font-size: 0.6rem; font-family: 'DM Mono', monospace;
              padding: 4px 12px; border-radius: 20px; letter-spacing: 1.5px;
              display: flex; align-items: center; gap: 6px; }
.live-dot { width: 8px; height: 8px; background: #FF3B3B; border-radius: 50%;
            animation: blink 1.2s ease-in-out infinite; flex-shrink: 0; }
@keyframes blink { 0%,100% { opacity:1; box-shadow:0 0 4px #FF3B3B; }
                   50%       { opacity:0.3; box-shadow:none; } }

.kpi-card { background: #FFF; border: 1px solid #DDE3EE; border-radius: 10px;
            padding: 0.85rem 1.1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.kpi-label { font-size: 0.6rem; color: #6B7A99; font-family: 'DM Mono', monospace;
             letter-spacing: 1px; text-transform: uppercase; }
.kpi-value { font-size: 1.45rem; font-weight: 700; color: #0A1628; margin: 3px 0 2px; }
.kpi-pos   { font-size: 0.8rem; color: #00875A; font-weight: 600; }
.kpi-neg   { font-size: 0.8rem; color: #DE350B; font-weight: 600; }

.sec-hdr { font-size: 0.82rem; font-family: 'DM Sans', sans-serif; color: #003DA5;
           font-weight: 700; letter-spacing: 0.3px;
           border-bottom: 2px solid #003DA5; padding-bottom: 6px; margin-bottom: 0.9rem; }

.stTabs [data-baseweb="tab-list"] {
    background: #FFF; border-radius: 8px; border: 1px solid #DDE3EE;
    padding: 4px; gap: 4px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #6B7A99; font-family: 'DM Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.8px; border-radius: 6px; padding: 8px 18px; }
.stTabs [aria-selected="true"] { background: #003DA5 !important; color: #FFF !important; }

.stButton > button {
    background: #003DA5 !important; border: none !important; color: #FFF !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 600 !important; letter-spacing: 0.3px !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.4rem !important;
    min-width: 160px !important; white-space: nowrap !important; }
.stButton > button:hover { background: #002D80 !important; }
/* Reset button — orange */
div[data-testid="column"]:nth-child(2) .stButton > button {
    background: #FF6B00 !important; }
div[data-testid="column"]:nth-child(2) .stButton > button:hover {
    background: #CC5500 !important; }

.ai-panel { background: linear-gradient(135deg, #EEF3FF 0%, #F4F6FA 100%);
            border: 1px solid #C2D0F0; border-left: 4px solid #003DA5;
            border-radius: 8px; padding: 1.1rem; margin-top: 0.9rem; }
.ai-hdr   { font-size: 0.6rem; color: #003DA5; font-family: 'DM Mono', monospace;
            letter-spacing: 2px; margin-bottom: 0.5rem; font-weight: 600; }
.ai-resp  { font-size: 0.87rem; color: #0A1628; line-height: 1.7; }

.move-a { background: #E8F8F1; border-left: 3px solid #00875A;
          padding: 7px 12px; border-radius: 5px; margin: 3px 0; font-size: 0.8rem; color: #0A1628; }
.move-b { background: #FFF4E5; border-left: 3px solid #FF8B00;
          padding: 7px 12px; border-radius: 5px; margin: 3px 0; font-size: 0.8rem; color: #0A1628; }
.move-c { background: #FEF0ED; border-left: 3px solid #DE350B;
          padding: 7px 12px; border-radius: 5px; margin: 3px 0; font-size: 0.8rem; color: #0A1628; }

.roi-box { background: linear-gradient(135deg, #003DA5 0%, #0050D0 100%);
           border-radius: 12px; padding: 1.6rem 1.4rem; text-align: center;
           box-shadow: 0 6px 24px rgba(0,61,165,0.25); min-height: 140px;
           display: flex; flex-direction: column; justify-content: center; }
.roi-num  { font-size: 2.4rem; font-weight: 700; color: #FF6B00;
            font-family: 'DM Mono', monospace; letter-spacing: -1px; }
.roi-lbl  { font-size: 0.6rem; color: rgba(255,255,255,0.7);
            font-family: 'DM Mono', monospace; letter-spacing: 1.5px; margin-top: 4px; }

.mini-card { background: #FFF; border: 1px solid #DDE3EE; border-radius: 8px;
             padding: 0.75rem 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.mini-lbl  { font-size: 0.58rem; color: #6B7A99; font-family: 'DM Mono', monospace;
             letter-spacing: 1px; text-transform: uppercase; }
.mini-val  { font-size: 1.15rem; font-weight: 700; margin-top: 3px; color: #0A1628; }

.info-box { background: #EEF3FF; border: 1px solid #C2D0F0; border-radius: 8px;
            padding: 0.85rem 1rem; font-size: 0.8rem; color: #0A1628; line-height: 1.55; }
.stDataFrame { border: 1px solid #DDE3EE !important; border-radius: 8px !important; }

/* Make error/warning/info boxes readable on bright background */
div[data-testid="stException"] { background: #FFF0F0 !important; border: 1px solid #DE350B !important; border-radius: 8px !important; }
div[data-testid="stException"] p, div[data-testid="stException"] pre,
div[data-testid="stException"] code { color: #0A1628 !important; }
.stAlert { border-radius: 8px !important; }
.stAlert p { color: #0A1628 !important; }

/* Force ALL text dark — nuclear approach for Streamlit Cloud compatibility */
* { color: #0A1628; }
/* Restore white text only where explicitly needed */
.app-header, .app-header *, .app-title, .app-title *,
.app-sub, .live-badge, .live-badge *,
.roi-box, .roi-box *, .roi-num, .roi-lbl,
.stTabs [aria-selected="true"], .stTabs [aria-selected="true"] *,
.stButton > button, .stButton > button *,
button[kind="primary"], button[kind="primary"] * { color: inherit; }
/* Explicit white for header and blue boxes */
.app-header { color: #FFFFFF !important; }
.app-title { color: #FFFFFF !important; }
.app-sub { color: rgba(255,255,255,0.6) !important; }
.live-badge { color: #FFFFFF !important; }
.roi-num { color: #FF6B00 !important; }
.roi-lbl { color: rgba(255,255,255,0.7) !important; }
.stTabs [aria-selected="true"] { color: #FFFFFF !important; }
.stButton > button { color: #FFFFFF !important; }
/* Spinner */
div[data-testid="stSpinner"] p,
div[data-testid="stSpinner"] div,
.stSpinner > div,
[class*="spinner"] p { color: #0A1628 !important; }
/* Slider tick marks and range numbers */
div[data-testid="stSlider"] p,
div[data-testid="stSlider"] span,
div[data-testid="stSlider"] div,
.stSlider p, .stSlider span,
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"],
[data-testid="stSliderThumbValue"] { color: #0A1628 !important; }
/* Toggle */
div[data-testid="stToggle"] p,
div[data-testid="stToggle"] span,
div[data-testid="stToggle"] div:not([class*="track"]):not([class*="thumb"]) { color: #0A1628 !important; }
/* Expander */
details summary, details summary *,
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary * { color: #0A1628 !important; font-weight: 600 !important; }
/* All widget labels */
label, label p, [data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p { color: #0A1628 !important; font-weight: 500 !important; }
/* Selectbox, multiselect — force white background on dropdown */
.stSelectbox *, .stMultiSelect * { color: #0A1628 !important; }
[data-baseweb='select'] { background: #FFFFFF !important; }
[data-baseweb='select'] > div { background: #FFFFFF !important; color: #0A1628 !important; }
[data-baseweb='popover'] { background: #FFFFFF !important; }
[data-baseweb='popover'] li { background: #FFFFFF !important; color: #0A1628 !important; }
[data-baseweb='popover'] li:hover { background: #EEF3FF !important; color: #003DA5 !important; }
[data-baseweb='menu'] { background: #FFFFFF !important; }
[data-baseweb='menu'] ul li { color: #0A1628 !important; background: #FFFFFF !important; }
/* Expander — white bg, blue header text always (open AND closed) */
details[data-testid='stExpander'] { background: #FFFFFF !important; }
details[data-testid='stExpander'] summary { background: #EEF3FF !important; border-radius: 8px !important; }
details[data-testid='stExpander'][open] summary { border-radius: 8px 8px 0 0 !important; }
details[data-testid='stExpander'] summary *,
details[data-testid='stExpander'][open] summary * { color: #003DA5 !important; font-weight: 600 !important; }
/* Error boxes */
div[data-testid="stException"],
div[data-testid="stException"] * { color: #0A1628 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
  <div>
    <div class="app-title">🔷 Sonepar Nexus: <span>Distribution Orchestrator</span></div>
    <div class="app-sub">ENTERPRISE SUPPLY CHAIN COMMAND CENTER &nbsp;|&nbsp;
      SONEPAR USA DISTRIBUTION NETWORK &nbsp;|&nbsp; DEMO DATA</div>
  </div>
  <div class="live-badge"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NETWORK KPI STRIP
# ══════════════════════════════════════════════════════════════════════════════
_od, _ = get_opco_data()
def _nhs(opco_data, idx=-1):
    s = []
    for o in opco_data:
        d = opco_data[o]
        s.append(d["Pick_Accuracy"][idx]*0.25 + d["OTD"][idx]*0.25 +
                 d["Slotting_Score"][idx]*0.20 +
                 max(0,100-d["DIP_Days"][idx]*10)*0.15 +
                 max(0,100-d["Excess_Inv_Pct"][idx])*0.15)
    import numpy as _np2
    return round(_np2.mean(s),1)
_nh  = _nhs(_od,-1); _nhp = _nhs(_od,-2)
_sl  = round(sum([_od[o]["Slotting_Score"][-1] for o in _od])/3,1)
_slp = round(sum([_od[o]["Slotting_Score"][-2] for o in _od])/3,1)
kpis = [
    ("NETWORK HEALTH",    f"{_nh}/100",  f"▲ {round(_nh-_nhp,1)} pts",  True),
    ("AVG PICK ACCURACY", "97.2%",       "▲ 1.4 pts",                    True),
    ("AVG DIP DAYS",      "3.1",         "▼ 0.6 days",                   True),
    ("NETWORK SLOT SCORE",f"{_sl}/100",  f"▲ {round(_sl-_slp,1)} pts",  True),
    ("AT-RISK SKUs",      "23",          "▲ 5 this month",               False),
]
for col, (lbl, val, delta, pos) in zip(st.columns(5), kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{lbl}</div>
          <div class="kpi-value">{val}</div>
          <div class="{'kpi-pos' if pos else 'kpi-neg'}">{delta}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

st.markdown(
    '<style>'
    'div[data-testid="stSpinner"] p { color: #0A1628 !important; }'
    'div[data-testid="stSlider"] label p { color: #0A1628 !important; font-weight:600 !important; }'
    'div[data-testid="stSlider"] [data-testid="stTickBarMin"] { color: #0A1628 !important; }'
    'div[data-testid="stSlider"] [data-testid="stTickBarMax"] { color: #0A1628 !important; }'
    'details[data-testid="stExpander"] { background:#FFFFFF !important; border:1px solid #DDE3EE !important; border-radius:10px !important; margin-bottom:8px !important; }'
    'details[data-testid="stExpander"] summary { background:#EEF3FF !important; border-radius:8px !important; padding:8px 12px !important; }'
    'details[data-testid="stExpander"] summary * { color:#003DA5 !important; font-weight:600 !important; }'
    'details[data-testid="stExpander"][open] summary * { color:#003DA5 !important; font-weight:600 !important; }'
    '[data-baseweb="select"] > div { background:#FFFFFF !important; color:#0A1628 !important; }'
    '[data-baseweb="popover"] { background:#FFFFFF !important; }'
    '[data-baseweb="popover"] li { background:#FFFFFF !important; color:#0A1628 !important; }'
    '[data-baseweb="popover"] li:hover { background:#EEF3FF !important; color:#003DA5 !important; }'
    '[data-baseweb="menu"] { background:#FFFFFF !important; }'
    '[data-baseweb="menu"] li { color:#0A1628 !important; background:#FFFFFF !important; }'
    'div[data-testid="stCheckbox"] label p { color:#0A1628 !important; font-weight:500 !important; }'
    'div[data-testid="stCheckbox"] input { accent-color:#003DA5; }'
    '</style>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "⚙️  SLOTTING ENGINE",
    "🏢  OpCo BENCHMARKING",
    "💰  ROI CALCULATOR",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SLOTTING ENGINE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Cast Velocity_Class to str to avoid silent failures with pandas Categorical
    df = get_sku_data()
    df["Velocity_Class"] = df["Velocity_Class"].astype(str)

    # Slotting constants
    # 120 ft between aisles (industry standard 100-150 ft per aisle pair)
    AISLE_DIST_FT = 120
    ZONE_TO_AISLE = {"A": 1, "B": 2, "C": 3}

    def classify(hits: int) -> str:
        if hits >= 400: return "A"   # Fast movers -> Golden Zone Aisle 1
        if hits >= 200: return "B"   # Mid movers  -> Mid Zone    Aisle 2
        return "C"                   # Slow movers -> Cold Zone   Aisle 3+

    def run_optimization(src: pd.DataFrame) -> pd.DataFrame:
        opt = src.copy().sort_values("Monthly_Hits", ascending=False).reset_index(drop=True)
        opt["Opt_Zone"] = opt["Monthly_Hits"].apply(classify)
        bin_ctr = {"A": 0, "B": 0, "C": 0}
        aisles, bins = [], []
        for z in opt["Opt_Zone"]:
            bin_ctr[z] += 1
            aisles.append(ZONE_TO_AISLE[z])
            bins.append(bin_ctr[z])
        opt["Opt_Aisle"]       = aisles
        opt["Opt_Bin"]         = bins
        opt["Move_Required"]   = opt["Current_Zone"] != opt["Opt_Zone"]
        # Travel saved = |current_aisle - optimal_aisle| x 120 ft x monthly_hits
        # Zero when item is already in correct zone
        opt["Aisles_Crossed"]  = (opt["Current_Aisle"] - opt["Opt_Aisle"]).abs()
        opt["Travel_Saved_ft"] = opt.apply(
            lambda r: int(r["Aisles_Crossed"] * AISLE_DIST_FT * r["Monthly_Hits"])
                      if r["Move_Required"] else 0,
            axis=1,
        )
        return opt

    def compute_risk(src):
        out = src.copy()
        max_hits  = out["Monthly_Hits"].max()
        min_hits  = out["Monthly_Hits"].min()
        hit_norm  = (out["Monthly_Hits"] - min_hits) / (max_hits - min_hits)
        max_units = out["Avg_Units"].max()
        min_units = out["Avg_Units"].min()
        unit_norm = 1 - (out["Avg_Units"] - min_units) / (max_units - min_units)
        out["Stockout_Score"] = (hit_norm * 0.6 + unit_norm * 0.4) * 100
        out["Excess_Score"]   = ((1 - hit_norm) * 0.5 + (1 - unit_norm) * 0.5) * 100
        def mscore(row):
            vc, cz = str(row["Velocity_Class"]), str(row["Current_Zone"])
            if vc == "A" and cz != "A": return 90
            if vc == "B" and cz == "C": return 55
            if vc == "C" and cz == "A": return 40
            return 10
        out["Misplace_Score"] = out.apply(mscore, axis=1)
        out["Risk_Score"] = (out["Stockout_Score"]*0.35 + out["Excess_Score"]*0.25 + out["Misplace_Score"]*0.40).round(1)
        out["Risk_Label"] = out["Risk_Score"].apply(lambda s: "HIGH" if s>=65 else ("MEDIUM" if s>=40 else "LOW"))
        trends = {"CB-120A":8,"CB-240A":5,"WN-14G":12,"CP-15A":-15,"EM-LED4":3,
                  "PB-100":-2,"TR-480":-22,"CB-EP20":9,"RW-12G":-4,"JB-4SQ":15,
                  "FL-T8":-30,"MC-3/4":1,"DP-100A":-18,"OL-3PH":-8,"WT-STD":6}
        out["Trend_30d"] = out["SKU"].map(trends)
        out["Trend_Label"] = out["Trend_30d"].apply(lambda x: f"+{x}%" if x>0 else f"{x}%")
        return out.sort_values("Risk_Score", ascending=False).reset_index(drop=True)

    risk_df = compute_risk(st.session_state.edited_df)

    if "optimized" not in st.session_state:
        st.session_state.optimized = False
    if "opt_df" not in st.session_state:
        st.session_state.opt_df = df.copy()
    if "edited_df" not in st.session_state:
        st.session_state.edited_df = df.copy()

    left, right = st.columns([3, 2], gap="medium")

    # ── LEFT: SKU table ──────────────────────────────────────────────────────
    with left:
        st.markdown('<div class="sec-hdr">📦 Epicor Eclipse WMS/ERP — Current Slot Assignments</div>',
                    unsafe_allow_html=True)
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("▶  RUN SLOTTING OPTIMIZATION", key="run_opt", use_container_width=True):
                # Recompute Velocity_Class from edited hits before optimizing
                edited = st.session_state.edited_df.copy()
                edited["Velocity_Class"] = edited["Monthly_Hits"].apply(classify)
                edited["ABC_XYZ"] = edited["Velocity_Class"] + edited["CoV"].apply(
                    lambda c: "X" if c < 0.5 else ("Y" if c < 1.0 else "Z"))
                st.session_state.optimized = True
                st.session_state.opt_df    = run_optimization(edited)
        with b2:
            if st.button("↺  RESET", key="reset_opt", use_container_width=True):
                st.session_state.optimized = False
                st.session_state.opt_df    = df.copy()
                st.session_state.edited_df = df.copy()

        if st.session_state.optimized:
            # Post-optimization: read-only results table
            display_df = st.session_state.opt_df.copy()
            cols_show  = ["SKU","Description","Monthly_Hits","ABC_XYZ",
                          "Current_Zone","Opt_Zone","Move_Required","Travel_Saved_ft"]
            col_rename = {"Monthly_Hits":"Hits/Mo","ABC_XYZ":"ABC-XYZ",
                          "Current_Zone":"Cur Zone","Opt_Zone":"Opt Zone",
                          "Move_Required":"Move?","Travel_Saved_ft":"Ft Saved/Mo"}
            st.dataframe(
                display_df[cols_show].rename(columns=col_rename),
                use_container_width=True, height=570, hide_index=True,
            )
        else:
            # Pre-optimization: editable table — only Hits/Mo is editable
            edit_src = st.session_state.edited_df.copy()
            cols_edit = ["SKU","Description","Monthly_Hits","Velocity_Class","ABC_XYZ",
                         "Current_Zone","Current_Aisle","Current_Bin"]
            edit_view = edit_src[cols_edit].rename(columns={
                "Monthly_Hits":"Hits/Mo","Velocity_Class":"Class",
                "ABC_XYZ":"ABC-XYZ","Current_Zone":"Zone",
                "Current_Aisle":"Aisle","Current_Bin":"Bin"})

            edited_result = st.data_editor(
                edit_view,
                use_container_width=True,
                height=570,
                hide_index=True,
                disabled=["SKU","Description","Class","ABC-XYZ","Zone","Aisle","Bin"],
                column_config={
                    "Hits/Mo": st.column_config.NumberColumn(
                        "Hits/Mo",
                        help="Edit monthly hit frequency to see how optimization changes",
                        min_value=1,
                        max_value=999,
                        step=1,
                        format="%d",
                    )
                },
                key="sku_editor"
            )

            # Write edits back to session state
            edited_result = edited_result.rename(columns={
                "Hits/Mo":"Monthly_Hits","Class":"Velocity_Class",
                "ABC-XYZ":"ABC_XYZ","Zone":"Current_Zone",
                "Aisle":"Current_Aisle","Bin":"Current_Bin"})
            for col in edited_result.columns:
                if col in st.session_state.edited_df.columns:
                    st.session_state.edited_df[col] = edited_result[col].values

            # Show hint only when values differ from original
            hits_changed = (st.session_state.edited_df["Monthly_Hits"] != df["Monthly_Hits"]).any()
            if hits_changed:
                changed_skus = st.session_state.edited_df[
                    st.session_state.edited_df["Monthly_Hits"] != df["Monthly_Hits"]]["SKU"].tolist()
                st.markdown(
                    f'<div style="background:#E8F8F1;border-left:3px solid {GREEN};'
                    f'border-radius:6px;padding:6px 10px;margin-top:6px;font-size:0.78rem;color:{INK};">'
                    f'Hit frequency updated for: <b>{", ".join(changed_skus)}</b>. '
                    f'Click <b>Run Slotting Optimization</b> to see how the engine re-classifies.</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="font-size:0.75rem;color:{GREY_TXT};margin-top:6px;">'
                    f'15 SKUs · Epicor Eclipse WMS/ERP · '
                    f'A: {len(df[df["Velocity_Class"]=="A"])} · '
                    f'B: {len(df[df["Velocity_Class"]=="B"])} · '
                    f'C: {len(df[df["Velocity_Class"]=="C"])} SKUs · '
                    f'<b style="color:{BLUE};">Edit Hits/Mo cells to simulate demand changes</b></div>',
                    unsafe_allow_html=True)
            st.markdown(
                f'<div class="info-box" style="margin-top:5px;font-size:0.75rem;">'
                f'<b style="color:{BLUE};">ABC-XYZ:</b> '
                f'A/B/C = velocity (hit frequency) · X = stable (CoV &lt;0.5, AutoStore candidate) · '
                f'Y = moderate variability · Z = erratic (CoV &gt;1.0, manual pick zone). '
                f'<b>AX = automation ready · AZ = keep human pickers</b></div>',
                unsafe_allow_html=True)

    # ── RIGHT: Zone map ──────────────────────────────────────────────────────
    with right:
        zone_hdr = '📋 Recommended Moves' if st.session_state.optimized else '🗺️ Target Zone Map'
        st.markdown(f'<div class="sec-hdr">{zone_hdr}</div>', unsafe_allow_html=True)

        if st.session_state.optimized:
            opt_df   = st.session_state.opt_df
            moves_df = opt_df[opt_df["Move_Required"] == True]
            total_ft = int(opt_df["Travel_Saved_ft"].sum())
            n_moves  = int(opt_df["Move_Required"].sum())

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f'<div class="mini-card"><div class="mini-lbl">SKUs TO MOVE</div>'
                            f'<div class="mini-val" style="color:{ORANGE};">{n_moves}</div></div>',
                            unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="mini-card"><div class="mini-lbl">FT SAVED / MO</div>'
                            f'<div class="mini-val" style="color:{GREEN};">{total_ft:,}</div></div>',
                            unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # ── $ per SKU saved calculation ──────────────────────────────────
            # Picker wage assumption: $22.50/hr, walk speed 250 ft/min
            PICKER_WAGE   = 22.50
            WALK_FT_MIN   = 250.0
            moves_df = moves_df.copy()
            moves_df["Annual_Dollar_Saved"] = moves_df["Travel_Saved_ft"].apply(
                lambda ft: round((ft * 12) / WALK_FT_MIN / 60 * PICKER_WAGE, 0)
            )
            moves_df = moves_df.sort_values("Annual_Dollar_Saved", ascending=False).reset_index(drop=True)
            top5 = moves_df.head(5)
            total_top5_savings = int(top5["Annual_Dollar_Saved"].sum())

            # ── Top 5 Actions banner ──────────────────────────────────────────
            st.markdown(f'''
            <div style="background:linear-gradient(135deg,#003DA5 0%,#0050D0 100%);
                        border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:10px;">
              <div style="font-size:0.62rem;color:rgba(255,255,255,0.7);
                          font-family:DM Mono;letter-spacing:1.5px;margin-bottom:4px;">
                🚨 TOP 5 ACTIONS TO TAKE THIS WEEK
              </div>
              <div style="font-size:1.1rem;font-weight:700;color:#FF6B00;">
                Fixing these 5 SKUs saves ~${total_top5_savings:,} annually
              </div>
            </div>''', unsafe_allow_html=True)

            # ── Priority move cards with $ impact ────────────────────────────
            for rank, (_, row) in enumerate(top5.iterrows(), 1):
                oz   = row["Opt_Zone"]
                cls  = "move-a" if oz=="A" else ("move-b" if oz=="B" else "move-c")
                tag  = "Golden Zone" if oz=="A" else ("Mid Zone" if oz=="B" else "Cold Zone")
                col  = GREEN if oz=="A" else (WARN if oz=="B" else RED)
                pri  = ["🔴 CRITICAL","🟠 HIGH","🟡 HIGH","🟢 MEDIUM","🟢 MEDIUM"][rank-1]
                st.markdown(f'''
                <div class="{cls}" style="margin-bottom:5px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <b style="color:{INK};">#{rank} &nbsp;{row["SKU"]}</b>
                    <span style="font-size:0.7rem;background:#003DA5;color:#FFF;
                                 padding:2px 8px;border-radius:10px;">{pri}</span>
                  </div>
                  <div style="font-size:0.78rem;color:{GREY_TXT};margin-top:2px;">
                    {str(row["Description"])[:34]}
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:4px;">
                    <span style="font-size:0.72rem;color:{GREY_TXT};">
                      Zone {row["Current_Zone"]} · Aisle {row["Current_Aisle"]}
                      → <span style="color:{col};font-weight:600;">Zone {oz} · Aisle {row["Opt_Aisle"]} · Bin {row["Opt_Bin"]} ({tag})</span>
                    </span>
                    <span style="font-size:0.8rem;font-weight:700;color:{GREEN};">
                      +${int(row["Annual_Dollar_Saved"]):,}/yr
                    </span>
                  </div>
                </div>''', unsafe_allow_html=True)



        else:
            # Pre-optimization scatter — shows current (mis)placements
            # Velocity_Class cast to str above; string == string comparison is safe
            cls_colours = {"A": GREEN, "B": ORANGE, "C": RED}
            cls_names   = {"A": "A-Class (Fast ≥400)", "B": "B-Class (Mid 200-399)", "C": "C-Class (Slow <200)"}

            fig_zone = go.Figure()

            # Zone background shading
            for zone, fill, x0, x1, lbl in [
                ("A", GREEN,  0.5,  1.5, "GOLDEN ZONE"),
                ("B", ORANGE, 1.5,  4.5, "MID ZONE"),
                ("C", RED,    4.5, 10.5, "COLD ZONE"),
            ]:
                fig_zone.add_shape(
                    type="rect", x0=x0, x1=x1, y0=0, y1=46,
                    fillcolor=rgba(fill, 0.08),
                    line=dict(color=rgba(fill, 0.30), width=1),
                )
                fig_zone.add_annotation(
                    x=(x0+x1)/2, y=44, text=lbl,
                    font=dict(color=fill, size=9, family=MONO),
                    showarrow=False,
                )

            # One trace per class — string comparison guaranteed to work
            for cls_key in ["A", "B", "C"]:
                sub = df[df["Velocity_Class"] == cls_key]
                if sub.empty:
                    continue
                fig_zone.add_trace(go.Scatter(
                    x=sub["Current_Aisle"].tolist(),
                    y=sub["Current_Bin"].tolist(),
                    mode="markers+text",
                    name=cls_names[cls_key],
                    marker=dict(size=14, color=cls_colours[cls_key],
                                line=dict(color=BG_WHITE, width=1.5)),
                    text=sub["SKU"].tolist(),
                    textposition="top center",
                    textfont=dict(size=7, color=INK),
                    hovertemplate="<b>%{text}</b><br>Aisle %{x} · Bin %{y}<extra></extra>",
                ))

            layout_zone = base_layout(height=360, margin=dict(l=50, r=10, t=60, b=50))
            layout_zone["xaxis"].update(
                title=dict(text="Aisle", font=dict(color=INK, size=12)),
                tickvals=list(range(1,11)),
                tickfont=dict(color=INK, size=11),
            )
            layout_zone["yaxis"].update(
                title=dict(text="Bin", font=dict(color=INK, size=12)),
                tickfont=dict(color=INK, size=11),
            )
            layout_zone["showlegend"] = True
            layout_zone["legend"] = dict(
                orientation="h", yanchor="bottom", y=1.08,
                xanchor="left", x=0, font=dict(size=10, color=INK),
                bgcolor=BG_WHITE, bordercolor=GRID, borderwidth=1
            )
            layout_zone["modebar"] = dict(remove=["zoom","pan","zoomIn","zoomOut",
                                                   "autoScale","resetScale","toImage",
                                                   "select2d","lasso2d","toggleSpikelines"])
            fig_zone.update_layout(**layout_zone)
            st.plotly_chart(fig_zone, use_container_width=True)
            st.markdown("""
            <div class="info-box">
              🟢 <b>A-Class</b> (≥400 hits/mo) → Golden Zone Aisle 1 &nbsp;|&nbsp;
              🟡 <b>B-Class</b> (200–399) → Mid Zone Aisle 2 &nbsp;|&nbsp;
              🔴 <b>C-Class</b> (&lt;200) → Cold Zone Aisle 3+<br>
              <span style="color:#6B7A99;font-size:0.77rem;">
                Notice A-class SKUs sitting in the Cold Zone — that is the inefficiency.
                Press <b>Run Slotting Optimization</b> to generate recommended moves and feet saved.
              </span>
            </div>""", unsafe_allow_html=True)



    # ── Root Cause Snapshot — full width, after optimization ───────────────────
    if st.session_state.optimized and "opt_df" in st.session_state:
        _opt     = st.session_state.opt_df
        _W       = 22.50; _FM = 250.0
        a_mis    = len(_opt[(_opt["Velocity_Class"]=="A") & (_opt["Move_Required"]==True)])
        a_tot    = len(_opt[_opt["Velocity_Class"]=="A"])
        pct_w    = int(a_mis / a_tot * 100) if a_tot > 0 else 0
        top_a    = _opt[_opt["Move_Required"]==True]["Current_Aisle"].mode()
        top_an   = int(top_a.iloc[0]) if len(top_a) > 0 else "N/A"
        tot_ann  = int(_opt["Travel_Saved_ft"].sum() * 12 / _FM / 60 * _W)
        n_moves  = len(_opt[_opt["Move_Required"]==True])

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">📊 Root Cause Snapshot: DMAIC Analysis</div>', unsafe_allow_html=True)
        rc1, rc2, rc3, rc4 = st.columns(4)
        for col_r, (lbl, val, sub, clr) in zip([rc1,rc2,rc3,rc4],[
            ("DEFINE",   f"{pct_w}% A-class misplaced",    "Fast movers in wrong zone",     RED),
            ("MEASURE",  f"Aisle {top_an} highest impact", "Primary congestion source",     WARN),
            ("ANALYZE",  f"${tot_ann:,}/yr wasted",        "Total picker travel loss",      ORANGE),
            ("IMPROVE",  f"{n_moves} SKU moves planned",   "Re-slot action plan ready",     GREEN),
        ]):
            with col_r:
                st.markdown(
                    f'<div class="mini-card" style="border-top:3px solid {clr};">'
                    f'<div class="mini-lbl" style="color:{clr};font-size:0.65rem;">{lbl}</div>'
                    f'<div style="font-size:0.9rem;font-weight:700;color:#0A1628;margin:4px 0;">{val}</div>'
                    f'<div style="font-size:0.7rem;color:#6B7A99;">{sub}</div>'
                    f'</div>', unsafe_allow_html=True)

    # ── ML Risk Prediction — full width, shown only before optimization ─────────
    if not st.session_state.optimized:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">🧠 ML SKU Risk Prediction — 30-Day Inventory and Placement Risk Model</div>', unsafe_allow_html=True)

        high_ct = len(risk_df[risk_df["Risk_Label"]=="HIGH"])
        med_ct  = len(risk_df[risk_df["Risk_Label"]=="MEDIUM"])
        low_ct  = len(risk_df[risk_df["Risk_Label"]=="LOW"])

        rs1, rs2, rs3, rs4 = st.columns(4)
        for col_s, (lbl, val, clr) in zip([rs1,rs2,rs3,rs4],[
            ("HIGH RISK SKUs",   str(high_ct)+" SKUs", RED),
            ("MEDIUM RISK SKUs", str(med_ct)+" SKUs",  WARN),
            ("LOW RISK SKUs",    str(low_ct)+" SKUs",  GREEN),
            ("MODEL FACTORS",    "3 INPUTS",            BLUE),
        ]):
            with col_s:
                st.markdown(
                    f'<div class="mini-card"><div class="mini-lbl">{lbl}</div>'
                    f'<div class="mini-val" style="color:{clr};">{val}</div></div>',
                    unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        ml_c1, ml_c2 = st.columns(2, gap="medium")
        for i, (_, row) in enumerate(risk_df.iterrows()):
            col_target = ml_c1 if i % 2 == 0 else ml_c2
            rl    = row["Risk_Label"]
            clr   = RED if rl=="HIGH" else (WARN if rl=="MEDIUM" else GREEN)
            bg    = "#FEF0ED" if rl=="HIGH" else ("#FFF4E5" if rl=="MEDIUM" else "#E8F8F1")
            tr    = row["Trend_30d"]
            tclr  = "#DE350B" if tr > 0 else "#00875A"
            ttext = row["Trend_Label"]
            bw    = int(row["Risk_Score"])
            html  = (
                f'<div style="background:{bg};border-left:4px solid {clr};'
                f'border:1px solid {clr};border-radius:8px;padding:10px 14px;'
                f'margin-bottom:8px;color:#0A1628;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">'
                f'<div>'
                f'<b style="color:{INK};font-size:0.9rem;">{row["SKU"]}</b>'
                f'<span style="color:{GREY_TXT};font-size:0.78rem;margin-left:8px;">{str(row["Description"])[:28]}</span>'
                f'</div>'
                f'<div style="display:flex;gap:8px;align-items:center;">'
                f'<span style="font-size:0.72rem;color:{tclr};font-weight:600;">{ttext} demand</span>'
                f'<span style="background:{clr};color:#FFF;font-size:0.68rem;font-weight:700;'
                f'padding:2px 10px;border-radius:10px;">{rl} RISK</span>'
                f'</div></div>'
                f'<div style="display:flex;gap:16px;font-size:0.75rem;color:{GREY_TXT};margin-bottom:5px;">'
                f'<span>Hits/Mo: <b style="color:{INK};">{row["Monthly_Hits"]}</b></span>'
                f'<span>Zone: <b style="color:{INK};">{row["Current_Zone"]}</b></span>'
                f'<span>Class: <b style="color:{INK};">{row["Velocity_Class"]}</b></span>'
                f'<span>Score: <b style="color:{clr};">{row["Risk_Score"]}/100</b></span>'
                f'</div>'
                f'<div style="background:#E0E6F0;border-radius:4px;height:6px;">'
                f'<div style="background:{clr};height:6px;border-radius:4px;width:{bw}%;"></div>'
                f'</div>'
                f'<div style="display:flex;gap:12px;font-size:0.7rem;color:{GREY_TXT};margin-top:4px;">'
                f'<span>Stockout: <b style="color:{INK};">{row["Stockout_Score"]:.0f}</b></span>'
                f'<span>Excess: <b style="color:{INK};">{row["Excess_Score"]:.0f}</b></span>'
                f'<span>Misplacement: <b style="color:{INK};">{row["Misplace_Score"]:.0f}</b></span>'
                f'</div></div>'
            )
            with col_target:
                st.markdown(html, unsafe_allow_html=True)

        st.markdown(
            f'<div class="info-box" style="margin-top:4px;">'
            f'<b style="color:{BLUE};">Model methodology:</b> '
            f'Weighted scoring across 3 factors — Stockout Risk (35%): high demand + low unit coverage; '
            f'Excess Inventory Risk (25%): low demand + high unit count; '
            f'Misplacement Risk (40%): velocity class vs current zone mismatch. '
            f'Zone logic aligned with <b>Optricity slotting methodology</b> (A/B/C velocity zoning). '
            f'30-day demand trend simulates Prophet time-series forecast output. '
            f'In production: trained on 12 months of <b>Epicor Eclipse WMS/ERP</b> transaction history '
            f'using Random Forest classifier.</div>',
            unsafe_allow_html=True)

    # ── AI Advisor ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">🤖 AI Warehouse Advisor</div>', unsafe_allow_html=True)
    q1, q2 = st.columns([4, 1])
    with q1:
        slot_q = st.text_input("_slot_lbl", label_visibility="collapsed",
            value="Why are the Junction Boxes and Wire Nuts misplaced?", key="slot_q")
    with q2:
        ask_slot = st.button("ASK ADVISOR →", key="ask_slot")
    if ask_slot and slot_q:
        # Use live edited data so AI reflects any hit frequency changes made by user
        live_df  = st.session_state.edited_df.copy()
        live_df["Velocity_Class"] = live_df["Monthly_Hits"].apply(classify)
        summary  = live_df[["SKU","Description","Monthly_Hits","Velocity_Class","Current_Zone"]
                     ].to_dict(orient="records")
        sys_p = (
            f"You are a warehouse optimization expert analyzing Epicor Eclipse data for Sonepar USA.\n"
            f"SKU data (15 items): {json.dumps(summary)}\n"
            f"Slotting rules: A-class (>=400 hits/mo) -> Golden Zone Aisle 1. "
            f"B-class (200-399) -> Mid Zone Aisle 2. C-class (<200) -> Cold Zone Aisle 3+.\n"
            f"Answer in 3-4 sentences of plain prose. No markdown, no asterisks, no bullet points. "
            f"Cite specific SKU codes and hit counts."
        )
        with st.spinner("Analyzing warehouse data..."):
            try:
                client = anthropic.Anthropic()
                resp   = client.messages.create(
                    model="claude-sonnet-4-20250514", max_tokens=300,
                    system=sys_p, messages=[{"role":"user","content":slot_q}])
                st.markdown(
                    f'<div class="ai-panel"><div class="ai-hdr">⚡ WAREHOUSE ADVISOR</div>'
                    f'<div class="ai-resp">{resp.content[0].text}</div></div>',
                    unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — OpCo BENCHMARKING
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    opco_data, months = get_opco_data()
    opcos    = list(opco_data.keys())
    OPCO_CLR = {"Crawford Electric": BLUE,
                "North Coast Electric": ORANGE,
                "Viking Electric": GREEN}
    metrics_list  = ["Pick_Accuracy","OTD","DIP_Days","Excess_Inv_Pct","LPMH","Slotting_Score"]
    metric_labels = ["Pick Acc %","OTD %","DIP Days","Excess Inv %","LPMH","Slotting Score"]
    higher_better = [True, True, False, False, True, True]

    st.markdown('<div class="sec-hdr">🏢 Enterprise OpCo Performance Benchmarking: Last 6 Months</div>',
                unsafe_allow_html=True)
    selected = st.multiselect("Select OpCos to compare", opcos, default=opcos, key="opco_sel")

    if not selected:
        st.warning("Select at least one OpCo to compare.")
    else:
        # ── Scorecard ────────────────────────────────────────────────────────
        sc_cols = st.columns(len(selected))
        for col, opco in zip(sc_cols, selected):
            with col:
                color  = OPCO_CLR[opco]
                latest = {m: opco_data[opco][m][-1] for m in metrics_list}
                prev   = {m: opco_data[opco][m][-2] for m in metrics_list}
                st.markdown(
                    f'<div style="color:{color};font-family:DM Mono;font-size:0.68rem;'
                    f'font-weight:600;margin-bottom:6px;letter-spacing:1px;">'
                    f'▶ {opco.upper()}</div>',
                    unsafe_allow_html=True)
                for m, lbl, hb in zip(metrics_list, metric_labels, higher_better):
                    val  = latest[m]
                    diff = round(val - prev[m], 1)
                    good = (diff > 0) if hb else (diff < 0)
                    arr  = "▲" if diff > 0 else "▼"
                    dc   = GREEN if good else RED
                    st.markdown(f"""
                    <div class="kpi-card" style="margin-bottom:4px;padding:0.5rem 0.9rem;">
                      <div class="kpi-label">{lbl}</div>
                      <div style="display:flex;align-items:baseline;gap:6px;">
                        <span style="font-size:1.05rem;font-weight:700;color:{color};">{val}</span>
                        <span style="font-size:0.65rem;color:{dc};font-weight:600;">{arr} {abs(diff)}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Trend + Radar ─────────────────────────────────────────────────────
        ch_col, rad_col = st.columns([3, 2], gap="medium")

        with ch_col:
            st.markdown('<div class="sec-hdr">📈 6-Month Trend</div>', unsafe_allow_html=True)
            chart_m = st.selectbox("Metric", options=metrics_list,
                format_func=lambda x: x.replace("_"," "), key="bench_metric")
            fig_trend = go.Figure()
            for opco in selected:
                fig_trend.add_trace(go.Scatter(
                    x=months, y=opco_data[opco][chart_m], name=opco,
                    line=dict(color=OPCO_CLR[opco], width=2.5),
                    mode="lines+markers",
                    marker=dict(size=7, color=OPCO_CLR[opco],
                                line=dict(color=BG_WHITE, width=1.5)),
                    hovertemplate=f"<b>{opco}</b><br>%{{x}}: %{{y}}<extra></extra>",
                ))
            trend_layout = base_layout(height=300, margin=dict(l=50, r=10, t=20, b=40))
            trend_layout["xaxis"].update(tickfont=dict(color=INK, size=11))
            trend_layout["yaxis"].update(tickfont=dict(color=INK, size=11))
            fig_trend.update_layout(**trend_layout)
            st.plotly_chart(fig_trend, use_container_width=True)

        with rad_col:
            st.markdown('<div class="sec-hdr">📡 Composite Radar</div>', unsafe_allow_html=True)
            # Normalise to 0-100 using realistic operational ranges for fair comparison
            radar_metrics = ["Pick_Accuracy","OTD","Slotting_Score","LPMH"]
            radar_labels  = ["Pick Acc","OTD","Slotting","LPMH"]
            norm_ranges   = {
                "Pick_Accuracy":  (88, 100),   # 88-100% real DC range
                "OTD":            (80, 100),   # 80-100% real DC range
                "Slotting_Score": (50, 100),   # 50=poor, 100=optimal
                "LPMH":           (60, 110),   # 60=low, 110=best-in-class
            }
            def normalise(val, lo, hi):
                return max(0.0, min(100.0, (val - lo) / (hi - lo) * 100))

            fig_radar = go.Figure()
            for opco in selected:
                raw  = [opco_data[opco][m][-1] for m in radar_metrics]
                norm = [normalise(v, *norm_ranges[m]) for v, m in zip(raw, radar_metrics)]
                nc   = norm + [norm[0]]
                lc   = radar_labels + [radar_labels[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=nc, theta=lc, fill="toself", name=opco,
                    line=dict(color=OPCO_CLR[opco], width=2),
                    fillcolor=rgba(OPCO_CLR[opco], 0.12),
                ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor=BG_CHART,
                    radialaxis=dict(visible=True, range=[0,100], color=INK,
                                   gridcolor=GRID, tickfont=dict(size=9, color=INK)),
                    angularaxis=dict(color=INK, tickfont=dict(size=11, color=INK)),
                ),
                paper_bgcolor=BG_WHITE,
                font=dict(family=MONO, color=INK),
                legend=dict(bgcolor=BG_WHITE, bordercolor=GRID, borderwidth=1,
                            orientation="h", yanchor="bottom", y=-0.28,
                            font=dict(size=11, color=INK),
                            itemsizing="constant"),
                margin=dict(l=20, r=20, t=20, b=80),
                height=340,
            )
            st.plotly_chart(fig_radar, use_container_width=True,
                config={"modeBarButtonsToAdd": ["resetViews"]})

    # ── AI Advisor ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">🤖 AI Warehouse Advisor</div>', unsafe_allow_html=True)
    bq1, bq2 = st.columns([4, 1])
    with bq1:
        bench_q = st.text_input("_bench_lbl", label_visibility="collapsed",
            value="Why is North Coast Electric underperforming this month?", key="bench_q")
    with bq2:
        ask_bench = st.button("ASK ADVISOR →", key="ask_bench")
    if ask_bench and bench_q:
        summary = {o: {m: opco_data[o][m][-1] for m in metrics_list} for o in opcos}
        sys_p = (
            f"You are a senior supply chain consultant at Sonepar USA.\n"
            f"OpCo performance data (latest month): {json.dumps(summary)}\n"
            f"Metrics: Pick Accuracy % (higher=better), OTD % (higher=better), "
            f"DIP Days (lower=better), Excess Inventory % (lower=better), "
            f"LPMH Lines Per Man Hour (higher=better), Slotting Score 0-100 (higher=better).\n"
            f"Answer in 3-5 sentences of plain prose. No markdown, no asterisks, no bullet points. "
            f"Use DMAIC thinking: Define what is broken, Measure the specific metric gap, "
            f"Analyze the root cause, Improve with one concrete next action. "
            f"Cite specific metric values throughout."
        )
        with st.spinner("Analyzing OpCo data..."):
            try:
                client = anthropic.Anthropic()
                resp   = client.messages.create(
                    model="claude-sonnet-4-20250514", max_tokens=350,
                    system=sys_p, messages=[{"role":"user","content":bench_q}])
                st.markdown(
                    f'<div class="ai-panel"><div class="ai-hdr">⚡ ADVISOR ANALYSIS</div>'
                    f'<div class="ai-resp">{resp.content[0].text}</div></div>',
                    unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ROI CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
# MATH (verified correct — all bar chart bars in proper order):
#   total_labor_cost = pickers x hrs x shifts x adjusted_wage
#   travel_time_cost = total_labor_cost x 0.35          <- always < total
#   saved_dollars    = travel_time_cost x (reduction%)  <- always < travel
#   remaining_cost   = total_labor_cost - saved_dollars  <- always < total
#   payback_months   = impl_cost / (saved_dollars / 12)
#   productivity_pct = 0.35 x (reduction / 100) x 100
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    TRAVEL_PCT = 0.35   # 35% of picker time = non-value-add travel (industry benchmark)

    st.markdown('<div class="sec-hdr">💰 Slotting Optimization ROI Calculator</div>',
                unsafe_allow_html=True)
    left_r, right_r = st.columns([1, 2], gap="medium")

    with left_r:
        with st.expander("⚙️ Labor Parameters", expanded=True):
            pickers         = st.slider("Number of Pickers  (5 – 50)",      5,   50,  12)
            hourly_wage     = st.slider("Hourly Wage  ($15 – $45/hr)",      15.0, 45.0, 22.50, 0.50)
            shifts_per_year = st.slider("Shifts per Year  (200 – 300)",    200,  300,  250)
            hours_per_shift = st.slider("Hours per Shift  (6 – 12)",         6,   12,    8)

        with st.expander("🏭 Warehouse Parameters", expanded=False):
            travel_reduction = st.slider("Travel Distance Reduction  (5% – 40%)",  5,  40, 22)
            labor_cost_adj   = st.slider("Wage Increase What-If  (0% – 30%)",      0,  30,  0)
            st.markdown(
                '<div style="background:#EEF3FF;border:1px solid #003DA5;border-radius:8px;padding:0.5rem 0.8rem;margin-bottom:4px;">&#9889; Compare with AutoStore Automation</div>',
                unsafe_allow_html=True)
            automation_mode = st.checkbox(
                "Enable AutoStore comparison",
                value=False, key="autostore_mode"
            )
            if automation_mode:
                auto_cost_k    = st.slider("AutoStore Investment  ($100K – $600K)",  100, 600, 300)
                auto_reduction = st.slider("AutoStore Travel Reduction  (30% – 65%)", 30,  65,  50)
            else:
                auto_cost_k    = 300
                auto_reduction = 50

        with st.expander("💸 Implementation Cost", expanded=False):
            impl_cost_k = st.slider("One-Time Re-slot Cost  ($0K – $200K)", 0, 200, 40)
            impl_cost   = impl_cost_k * 1000

    with right_r:
        adjusted_wage    = hourly_wage * (1 + labor_cost_adj / 100)

        # Step 1 — total annual labor cost
        total_labor_hrs  = pickers * hours_per_shift * shifts_per_year
        total_labor_cost = total_labor_hrs * adjusted_wage

        # Step 2 — travel time cost: 35% of total labor (always < total_labor_cost)
        travel_time_cost = total_labor_cost * TRAVEL_PCT
        travel_time_hrs  = total_labor_hrs  * TRAVEL_PCT

        # Step 3 — savings: reduction% of travel only (always < travel_time_cost)
        saved_dollars    = travel_time_cost * (travel_reduction / 100)
        saved_hrs        = travel_time_hrs  * (travel_reduction / 100)

        # Step 4 — remaining cost (always < total_labor_cost)
        remaining_cost   = total_labor_cost - saved_dollars

        # Step 5 — derived
        productivity_pct = TRAVEL_PCT * (travel_reduction / 100) * 100
        monthly_savings  = saved_dollars / 12
        payback_months   = (impl_cost / monthly_savings) if (monthly_savings > 0 and impl_cost > 0) else 0

        # ── Headline boxes ──────────────────────────────────────────────────
        hl1, hl2 = st.columns(2)
        with hl1:
            st.markdown(f"""
            <div class="roi-box">
              <div class="roi-lbl">PROJECTED ANNUAL SAVINGS</div>
              <div class="roi-num">${saved_dollars:,.0f}</div>
              <div class="roi-lbl" style="margin-top:6px;">
                {travel_reduction}% travel reduction &nbsp;·&nbsp;
                {pickers} pickers &nbsp;·&nbsp; ${adjusted_wage:.2f}/hr
              </div>
            </div>""", unsafe_allow_html=True)

        with hl2:
            if payback_months == 0:
                pb_txt, pb_bg = "N/A", BLUE
            elif payback_months <= 12:
                pb_txt, pb_bg = f"{payback_months:.1f} mo", GREEN
            elif payback_months <= 24:
                pb_txt, pb_bg = f"{payback_months:.1f} mo", WARN
            else:
                pb_txt, pb_bg = f"{payback_months:.1f} mo", RED
            st.markdown(f"""
            <div class="roi-box" style="background:linear-gradient(135deg,{pb_bg} 0%,{pb_bg}cc 100%);">
              <div class="roi-lbl">PAYBACK PERIOD</div>
              <div class="roi-num" style="color:#FFF;font-size:2.1rem;">{pb_txt}</div>
              <div class="roi-lbl" style="margin-top:6px;">${impl_cost_k}K implementation cost</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Bar chart — bars always in descending order: total > travel > savings, remaining < total
        categories = ["Total Labor",  "Travel Time (35%)", "Annual Savings", "Remaining Labor"]
        values     = [total_labor_cost, travel_time_cost,   saved_dollars,    remaining_cost]
        bar_colors = [BLUE,             ORANGE,              GREEN,            "#ADB5C8"]

        fig_roi = go.Figure(go.Bar(
            x=categories, y=values,
            marker_color=bar_colors,
            text=[f"${v:,.0f}" for v in values],
            textposition="outside",
            textfont=dict(size=11, family=MONO, color=INK),
            textangle=0,
            width=0.5,
        ))
        layout_roi = base_layout(height=420, margin=dict(l=80, r=20, t=60, b=60))
        layout_roi["yaxis"].update(
            tickprefix="$", tickformat=",.0f",
            title=dict(text="Annual Cost ($)", font=dict(color=INK, size=12)),
            tickfont=dict(color=INK, size=11),
        )
        layout_roi["xaxis"].update(
            tickfont=dict(color=INK, size=11),
        )
        layout_roi["showlegend"] = False
        fig_roi.update_layout(**layout_roi)
        st.plotly_chart(fig_roi, use_container_width=True)

        # ── Mini cards ──────────────────────────────────────────────────────
        mc1, mc2, mc3, mc4 = st.columns(4)
        for col, (lbl, val, clr) in zip(
            [mc1, mc2, mc3, mc4],
            [("TRAVEL HRS SAVED",  f"{saved_hrs:,.0f} hrs",    BLUE),
             ("PRODUCTIVITY GAIN", f"+{productivity_pct:.1f}%", GREEN),
             ("ADJUSTED WAGE",     f"${adjusted_wage:.2f}/hr",  ORANGE),
             ("TRAVEL % OF LABOR", f"{TRAVEL_PCT*100:.0f}%",    GREY_TXT)],
        ):
            with col:
                st.markdown(
                    f'<div class="mini-card"><div class="mini-lbl">{lbl}</div>'
                    f'<div class="mini-val" style="color:{clr};">{val}</div></div>',
                    unsafe_allow_html=True)

    # ── AutoStore Comparison Panel ────────────────────────────────────────────
    if automation_mode:
        auto_impl    = auto_cost_k * 1000
        auto_saved   = travel_time_cost * (auto_reduction / 100)
        auto_payback = (auto_impl / (auto_saved / 12)) if auto_saved > 0 else 0
        delta_save   = auto_saved - saved_dollars
        delta_pb     = auto_payback - payback_months
        recommend    = ("AutoStore reaches break-even in under 3 years — recommended if expanding headcount."
                       if auto_payback <= 36 else
                       "Manual re-slot is the smarter first move — lower risk, faster payback.")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">🤖 Manual Re-slot vs AutoStore: Side by Side Comparison</div>', unsafe_allow_html=True)
        ac1, ac2 = st.columns(2, gap="medium")
        with ac1:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,{BLUE} 0%,{BLUE_LT} 100%);'
                f'border-radius:12px;padding:1.2rem 1.4rem;text-align:center;">'
                f'<div style="font-size:0.6rem;color:rgba(255,255,255,0.7);font-family:DM Mono;letter-spacing:1.5px;margin-bottom:6px;">MANUAL RE-SLOT</div>'
                f'<div style="font-size:1.8rem;font-weight:700;color:{ORANGE};font-family:DM Mono;">${saved_dollars:,.0f}/yr</div>'
                f'<div style="font-size:0.75rem;color:rgba(255,255,255,0.85);margin-top:8px;">'
                f'{travel_reduction}% travel reduction · ${impl_cost_k}K cost · {payback_months:.1f}mo payback<br>'
                f'<b style="color:#FFFFFF;">Best for: fewer than 20 pickers, fast ROI</b></div></div>',
                unsafe_allow_html=True)
        with ac2:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#0d1f3c 0%,#1a3560 100%);'
                f'border-radius:12px;padding:1.2rem 1.4rem;text-align:center;border:2px solid #00d4ff;">'
                f'<div style="font-size:0.6rem;color:rgba(255,255,255,0.7);font-family:DM Mono;letter-spacing:1.5px;margin-bottom:6px;">AUTOSTORE AUTOMATION</div>'
                f'<div style="font-size:1.8rem;font-weight:700;color:#00d4ff;font-family:DM Mono;">${auto_saved:,.0f}/yr</div>'
                f'<div style="font-size:0.75rem;color:rgba(255,255,255,0.85);margin-top:8px;">'
                f'{auto_reduction}% travel reduction · ${auto_cost_k}K cost · {auto_payback:.1f}mo payback<br>'
                f'<b style="color:#FFFFFF;">Best for: 30+ pickers, enterprise scale</b></div></div>',
                unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#EEF3FF;border:1px solid {BLUE};border-radius:8px;'
            f'padding:0.8rem 1rem;margin-top:8px;color:#0A1628;font-size:0.82rem;">'
            f'<b style="color:{BLUE};">Decision insight:</b> AutoStore saves an additional ${delta_save:,.0f}/yr '
            f'({auto_reduction - travel_reduction}% more reduction) but requires {delta_pb:.0f} more months to pay back. '
            f'{recommend}</div>',
            unsafe_allow_html=True)

    # ── Cost of Inaction ──────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">⏳ Cost of Inaction — What Happens If We Do Not Fix This?</div>',
                unsafe_allow_html=True)

    # Project losses if no re-slot is done (compounding 3% annual wage inflation)
    inaction_6mo  = saved_dollars * 0.5
    inaction_1yr  = saved_dollars
    inaction_2yr  = saved_dollars * 1.03 + saved_dollars  # yr2 savings lost + 3% inflation
    cumulative_2yr = inaction_6mo + inaction_1yr + (saved_dollars * 1.03)

    ia1, ia2, ia3, ia4 = st.columns(4)
    for col_w, (period, loss, clr, icon) in zip(
        [ia1, ia2, ia3, ia4],
        [("If delayed 6 months",  inaction_6mo,   WARN,   "⚠️"),
         ("If delayed 1 year",    inaction_1yr,   ORANGE, "🔴"),
         ("If delayed 2 years",   inaction_2yr,   RED,    "🚨"),
         ("2-yr cumulative loss", cumulative_2yr, RED,    "💸")],
    ):
        with col_w:
            st.markdown(
                f'''<div class="mini-card" style="border-left:3px solid {clr};">
                  <div class="mini-lbl">{icon} {period}</div>
                  <div class="mini-val" style="color:{clr};font-size:1.05rem;">
                    -${loss:,.0f}
                  </div>
                  <div style="font-size:0.68rem;color:{GREY_TXT};margin-top:2px;">
                    in foregone savings
                  </div>
                </div>''', unsafe_allow_html=True)

    st.markdown(
        f'''<div style="background:#FEF0ED;border:1px solid {RED};border-radius:8px;color:#0A1628;
                      padding:0.8rem 1rem;margin-top:10px;">
          <b style="color:{RED};">Every month of inaction costs ${saved_dollars/12:,.0f}</b>
          in foregone labor savings — that's ${saved_dollars/12/pickers:,.0f} per picker per month.
          At current wage trajectory (+3% YoY), the 2-year cumulative opportunity cost
          reaches <b>${cumulative_2yr:,.0f}</b>.
        </div>''', unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── AI Executive Briefing ─────────────────────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">🤖 AI Executive Briefing</div>', unsafe_allow_html=True)
    rq1, rq2 = st.columns([4, 1])
    with rq1:
        roi_q = st.text_input("_roi_lbl", label_visibility="collapsed",
            value="Write an executive summary of this ROI for the VP of Supply Chain.",
            key="roi_q")
    with rq2:
        ask_roi = st.button("ASK ADVISOR →", key="ask_roi")
    if ask_roi and roi_q:
        ctx = {
            "pickers":             pickers,
            "adjusted_wage":       f"${adjusted_wage:.2f}/hr",
            "total_labor_cost":    f"${total_labor_cost:,.0f}",
            "travel_time_cost":    f"${travel_time_cost:,.0f} (35% of total labor (industry standard))",
            "travel_reduction":    f"{travel_reduction}%",
            "annual_savings":      f"${saved_dollars:,.0f}",
            "travel_hours_saved":  f"{saved_hrs:,.0f} hrs/yr",
            "productivity_gain":   f"+{productivity_pct:.1f}%",
            "implementation_cost": f"${impl_cost:,.0f}",
            "payback_period":      f"{payback_months:.1f} months" if payback_months > 0 else "No implementation cost set",
            "remaining_labor_cost":f"${remaining_cost:,.0f}",
            "cost_of_inaction_1yr": f"${saved_dollars:,.0f} in foregone savings if delayed 1 year",
            "cost_of_inaction_2yr": f"${cumulative_2yr:,.0f} cumulative 2-year opportunity cost",
            "monthly_cost_of_delay": f"${saved_dollars/12:,.0f} lost per month of inaction",
        }
        sys_p = (
            f"You are a senior supply chain consultant preparing a boardroom briefing "
            f"for the VP of Supply Chain at Sonepar USA.\n"
            f"ROI data: {json.dumps(ctx)}\n"
            f"Write 4-5 sentences in plain prose — no markdown, no asterisks, no bullet points, no headers. "
            f"Use plain numbers with dollar signs. Frame as a Lean business case: "
            f"current state cost, future state savings, implementation path, and recommendation. "
            f"Reference DMAIC methodology naturally in the framing."
        )
        with st.spinner("Preparing executive briefing..."):
            try:
                client = anthropic.Anthropic()
                resp   = client.messages.create(
                    model="claude-sonnet-4-20250514", max_tokens=350,
                    system=sys_p, messages=[{"role":"user","content":roi_q}])
                st.markdown(
                    f'<div class="ai-panel"><div class="ai-hdr">⚡ EXECUTIVE BRIEFING</div>'
                    f'<div class="ai-resp">{resp.content[0].text}</div></div>',
                    unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-family:'DM Mono',monospace;font-size:0.56rem;
            color:#ADB5C8;padding:0.8rem 0;border-top:1px solid #DDE3EE;">
  SONEPAR NEXUS: DISTRIBUTION ORCHESTRATOR &nbsp;|&nbsp;
  VINOD KUNAPULI &nbsp;|&nbsp; Epicor Eclipse WMS/ERP · Optricity Slotting · DMAIC Methodology · Random Forest ML &nbsp;|&nbsp; DEMO DATA
</div>""", unsafe_allow_html=True)
