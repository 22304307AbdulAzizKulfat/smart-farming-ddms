import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AgroNex | Technical Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# AUTH GUARD — Must be logged in as technical_staff
# ══════════════════════════════════════════════════════════════
if "user" not in st.session_state:
    st.warning("⚠️ You are not logged in. Please log in first.")
    st.page_link("app.py", label="→ Go to Login")
    st.stop()

if st.session_state["user"].get("role") != "technical_staff":
    st.error("⛔ Access denied. This page is for Technical Staff only.")
    st.page_link("app.py", label="→ Go back to Login")
    st.stop()

user = st.session_state["user"]

# ══════════════════════════════════════════════════════════════
# SUPABASE CONNECTION
# ══════════════════════════════════════════════════════════════
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("❌ Could not connect to the database. Check your .env credentials.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# GLOBAL STYLES — AgroNex dark-blue theme
# Colors: bg #1a1d23, card #1e2128, input #262b36,
#         blue #3b82f6, border #2a2f3a
# Fonts: Trebuchet MS (headers), Courier New (inputs)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
  :root {
    --bg:       #1a1d23;
    --bg2:      #1f2329;
    --card:     #1e2128;
    --input:    #262b36;
    --blue:     #3b82f6;
    --blue-dim: #1d4ed8;
    --blue-glow:#3b82f630;
    --border:   #2a2f3a;
    --border-hi:#3b82f655;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --green:    #22c55e;
    --red:      #ef4444;
    --yellow:   #f59e0b;
  }
  html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Trebuchet MS', sans-serif !important;
  }
  ::-webkit-scrollbar { width:6px; height:6px; }
  ::-webkit-scrollbar-track { background:var(--bg); }
  ::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
  ::-webkit-scrollbar-thumb:hover { background:var(--blue); }
  .top-bar {
    display:flex; align-items:center; justify-content:space-between;
    background: #1e2128;
    border-bottom:2px solid var(--blue);
    padding:16px 32px; margin-bottom:28px;
    border-radius:0 0 16px 16px;
    box-shadow: 0 4px 24px #3b82f620;
  }
  .top-bar-left { display:flex; align-items:center; gap:14px; }
  .logo-box {
    background: linear-gradient(135deg, var(--blue), var(--blue-dim));
    color:white; border-radius:10px;
    padding:8px 12px; font-size:24px; font-weight:700;
    box-shadow: 0 0 16px var(--blue-glow);
    font-family:'Trebuchet MS',sans-serif;
  }
  .top-bar-title {
    font-size:22px; font-weight:700; color:var(--blue);
    letter-spacing:3px; font-family:'Trebuchet MS',sans-serif;
    text-shadow: 0 0 20px var(--blue-glow);
  }
  .top-bar-sub {
    font-size:12px; color:var(--muted);
    letter-spacing:2px; font-family:'Courier New',monospace;
    text-transform:uppercase;
  }
  .top-bar-right {
    color:var(--muted); font-size:12px;
    font-family:'Courier New',monospace;
    text-align:right; line-height:1.6;
  }
  .top-bar-right span { color:var(--blue); font-weight:600; }
  .stat-card {
    background: linear-gradient(135deg, var(--card) 0%, #1a2035 100%);
    border:1px solid var(--border);
    border-radius:12px; padding:22px 20px; text-align:center;
    transition: all 0.25s ease;
    position:relative; overflow:hidden;
  }
  .stat-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg, transparent, var(--blue), transparent);
    opacity:0; transition:opacity 0.25s;
  }
  .stat-card:hover { border-color:var(--blue); transform:translateY(-2px);
    box-shadow:0 8px 24px var(--blue-glow); }
  .stat-card:hover::before { opacity:1; }
  .stat-icon  { font-size:22px; margin-bottom:6px; }
  .stat-value {
    font-size:40px; font-weight:700; color:var(--blue); line-height:1;
    font-family:'Trebuchet MS',sans-serif;
    text-shadow:0 0 12px var(--blue-glow);
  }
  .stat-label {
    font-size:11px; color:var(--muted); margin-top:6px;
    letter-spacing:2px; text-transform:uppercase;
    font-family:'Courier New',monospace;
  }
  .section-heading {
    font-size:15px; font-weight:700; color:var(--blue);
    letter-spacing:3px; text-transform:uppercase;
    font-family:'Trebuchet MS',sans-serif;
    border-left:3px solid var(--blue);
    padding:6px 0 6px 14px; margin:28px 0 14px;
    background:linear-gradient(90deg,var(--blue-glow),transparent);
    border-radius:0 6px 6px 0;
  }
  .sql-badge {
    font-size:9px; font-family:'Courier New',monospace;
    background:var(--blue-glow); color:var(--blue);
    border:1px solid var(--border-hi);
    border-radius:4px; padding:1px 7px; margin-left:8px;
    vertical-align:middle; letter-spacing:1px;
  }
  .stButton > button {
    background:linear-gradient(135deg,var(--blue),var(--blue-dim)) !important;
    color:white !important; border:none !important;
    border-radius:8px !important;
    font-family:'Trebuchet MS',sans-serif !important;
    font-weight:700 !important; font-size:14px !important;
    padding:9px 22px !important; letter-spacing:1px !important;
    transition:all 0.2s !important;
    box-shadow:0 2px 12px var(--blue-glow) !important;
  }
  .stButton > button:hover {
    background:linear-gradient(135deg,#60a5fa,var(--blue)) !important;
    transform:translateY(-1px) !important;
    box-shadow:0 4px 20px var(--blue-glow) !important;
  }
  .stSelectbox > div > div,
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stTextArea textarea {
    background:var(--input) !important;
    border:1px solid var(--border) !important;
    color:var(--text) !important; border-radius:8px !important;
    font-family:'Courier New',monospace !important;
    font-size:13px !important;
  }
  .stSelectbox > div > div:focus-within,
  .stTextInput > div > div:focus-within {
    border-color:var(--blue) !important;
    box-shadow:0 0 0 2px var(--blue-glow) !important;
  }
  .stTabs [data-baseweb="tab-list"] {
    background:var(--card) !important;
    border-radius:10px !important; padding:4px !important;
    border:1px solid var(--border) !important; gap:4px !important;
  }
  .stTabs [data-baseweb="tab"] {
    font-family:'Trebuchet MS',sans-serif !important;
    font-weight:600 !important; font-size:13px !important;
    letter-spacing:1px !important; color:var(--muted) !important;
    border-radius:7px !important; padding:8px 16px !important;
    border:none !important;
  }
  .stTabs [aria-selected="true"] {
    background:var(--blue) !important; color:white !important;
    box-shadow:0 2px 12px var(--blue-glow) !important;
  }
  .stDataFrame {
    background:var(--card) !important; border-radius:10px !important;
    border:1px solid var(--border) !important; overflow:hidden !important;
  }
  .stDataFrame th {
    background:var(--input) !important; color:var(--blue) !important;
    font-family:'Trebuchet MS',sans-serif !important;
    font-weight:700 !important; letter-spacing:1px !important;
    text-transform:uppercase !important; font-size:11px !important;
  }
  .stDataFrame td {
    font-family:'Courier New',monospace !important;
    font-size:12px !important; color:var(--text) !important;
  }
  .stExpander {
    background:var(--card) !important;
    border:1px solid var(--border) !important;
    border-radius:10px !important; overflow:hidden !important;
  }
  .stExpander:hover { border-color:var(--border-hi) !important; }
  .stExpander summary {
    font-family:'Trebuchet MS',sans-serif !important;
    font-weight:600 !important; color:var(--text) !important;
    padding:12px 16px !important;
  }
  .badge-active {
    background:#ef444418; color:#ef4444;
    border:1px solid #ef444455; border-radius:6px;
    padding:3px 10px; font-size:11px; font-weight:700;
    font-family:'Courier New',monospace; letter-spacing:1px;
  }
  .badge-resolved {
    background:#22c55e18; color:#22c55e;
    border:1px solid #22c55e55; border-radius:6px;
    padding:3px 10px; font-size:11px; font-weight:700;
    font-family:'Courier New',monospace; letter-spacing:1px;
  }
  .badge-ignored {
    background:#64748b18; color:#64748b;
    border:1px solid #64748b55; border-radius:6px;
    padding:3px 10px; font-size:11px; font-weight:700;
    font-family:'Courier New',monospace; letter-spacing:1px;
  }
  hr { border:none !important; border-top:1px solid var(--border) !important; margin:20px 0 !important; }
  #MainMenu, footer, header { visibility:hidden; }
  .block-container { padding-top:0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CACHE HELPERS — prevents repeated API calls on every rerender
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=30, show_spinner=False)
def fetch_all(table: str, select: str = "*", _cb: int = 0):
    try:
        return supabase.table(table).select(select).execute().data or []
    except Exception:
        return []

@st.cache_data(ttl=30, show_spinner=False)
def fetch_filtered(table: str, select: str, col: str, val, _cb: int = 0):
    try:
        return supabase.table(table).select(select).eq(col, val).execute().data or []
    except Exception:
        return []

@st.cache_data(ttl=30, show_spinner=False)
def fetch_ordered(table: str, select: str, order_col: str, desc: bool = True, _cb: int = 0):
    try:
        return supabase.table(table).select(select).order(order_col, desc=desc).execute().data or []
    except Exception:
        return []

def bust():
    """Increment cache-bust key to force data refresh after mutations."""
    st.session_state["_cb"] = st.session_state.get("_cb", 0) + 1

def cb():
    return st.session_state.get("_cb", 0)

# ══════════════════════════════════════════════════════════════
# FRIENDLY ERROR MESSAGES
# ══════════════════════════════════════════════════════════════
_DB_ERRORS = {
    "violates foreign key": "Cannot delete — other records depend on this item.",
    "violates unique":      "A record with these details already exists.",
    "violates not-null":    "A required field is missing.",
    "violates check":       "A value is outside the allowed range.",
    "permission denied":    "You don't have permission to perform this action.",
    "JWT expired":          "Your session has expired. Please log in again.",
}

def friendly(e: Exception) -> str:
    msg = str(e).lower()
    for key, text in _DB_ERRORS.items():
        if key in msg:
            return text
    return "Something went wrong. Please try again."

def ok(msg: str):       st.toast(f"✅ {msg}", icon="✅")
def err(e: Exception):  st.toast(f"❌ {friendly(e)}", icon="❌")

# ══════════════════════════════════════════════════════════════
# REUSABLE TABLE RENDERER
# ══════════════════════════════════════════════════════════════
def show_table(rows: list, empty: str = "No records found."):
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info(empty)

# ══════════════════════════════════════════════════════════════
# PYTHON IMPLEMENTATIONS OF SQL FUNCTIONS
# NOTE: These functions exist in Oracle PL/SQL syntax in the project
# spec. Since Supabase uses PostgreSQL, we implement the same logic
# here in Python to produce identical results.
# ══════════════════════════════════════════════════════════════

def fn_sensor_stability(readings: list) -> str:
    """
    Mirrors fn_sensor_stability(p_sensor_id) from project spec.
    Classifies sensor stability based on value spread:
      spread <= 10  → STABLE
      spread <= 30  → MODERATE
      spread >  30  → UNSTABLE
    """
    values = [r["value"] for r in readings if r.get("value") is not None]
    if not values:
        return "NO DATA"
    spread = max(values) - min(values)
    if spread <= 10:
        return "STABLE"
    elif spread <= 30:
        return "MODERATE"
    else:
        return "UNSTABLE"

def fn_water_efficiency(irrigation_records: list, harvest_records: list) -> float:
    """
    Mirrors fn_water_efficiency(p_field_id) from project spec.
    Returns kg of harvest produced per litre of water used.
    Returns 0 if no water was used.
    """
    total_water   = sum(r.get("water_amount", 0) or 0 for r in irrigation_records)
    total_harvest = sum(r.get("quantity_kg",  0) or 0 for r in harvest_records)
    if total_water == 0:
        return 0.0
    return round(total_harvest / total_water, 2)

def fn_total_harvest(harvest_records: list) -> float:
    """
    Mirrors fn_total_harvest(p_crop_id) from project spec.
    Returns total harvested kg from a list of harvest records.
    """
    return sum(r.get("quantity_kg", 0) or 0 for r in harvest_records)

def fn_alert_count(alerts: list) -> int:
    """
    Mirrors fn_alert_count() from project spec.
    Returns total number of alerts in the system.
    Uses get_active_alerts_count() RPC for active count.
    """
    return len(alerts)

# ══════════════════════════════════════════════════════════════
# PLOTLY DARK THEME CONFIG
# ══════════════════════════════════════════════════════════════
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", family="Trebuchet MS"),
    margin=dict(t=30, b=10, l=10, r=10),
)

# ══════════════════════════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="top-bar">
  <div class="top-bar-left">
    <div class="logo-box">🌱</div>
    <div>
      <div class="top-bar-title">AGRONEX</div>
      <div class="top-bar-sub">Smart Farming System</div>
    </div>
    <div style="width:1px;height:36px;background:#2a2f3a;margin:0 8px;"></div>
    <div style="font-size:13px;color:#94a3b8;letter-spacing:2px;font-family:'Courier New',monospace;">🔧 TECHNICAL DASHBOARD</div>
  </div>
  <div class="top-bar-right">
    <span>{user.get("full_name","Technical Staff")}</span><br>
    {datetime.now().strftime("%d %b %Y &nbsp;&nbsp; %H:%M")}
  </div>
</div>
""", unsafe_allow_html=True)

_, col_logout = st.columns([10, 1])
with col_logout:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# ══════════════════════════════════════════════════════════════
# PRELOAD ALL DATA (cached, refreshed after mutations)
# ══════════════════════════════════════════════════════════════
sensors_all    = fetch_all("sensors",        "sensor_id, sensor_type, installed_at, field_id, installed_by",              _cb=cb())
readings_all   = fetch_ordered("sensor_readings", "reading_id, sensor_id, value, recorded_at, sensors(sensor_type)",      "recorded_at", desc=True, _cb=cb())
actuators_all  = fetch_all("actuators",      "actuator_id, actuator_type, actuator_status, field_id, installation_date",  _cb=cb())
actions_all    = fetch_ordered("actuator_actions", "action_id, start_time, end_time, actuator_id, actuators(actuator_type)", "start_time", desc=True, _cb=cb())
irrigation_all = fetch_all("irrigation",     "irrigation_id, method, water_amount, action_id, field_id, fields(field_name), actuator_actions(start_time)", _cb=cb())
alerts_all_raw = fetch_ordered("alerts",     "alert_id, alert_type, alert_status, created_at, field_id, fields(field_name)", "created_at", desc=True, _cb=cb())
fields_all     = fetch_all("fields",         "field_id, field_name, farm_id",  _cb=cb())
users_all      = fetch_all("users",          "user_id, full_name",             _cb=cb())
harvests_all   = fetch_all("harvests",       "harvest_id, crop_id, quantity_kg, field_id", _cb=cb())

alerts_active  = [a for a in alerts_all_raw if a.get("alert_status") == "active"]
field_opts     = {f["field_name"]: f["field_id"] for f in fields_all}
user_opts      = {u["full_name"]:  u["user_id"]  for u in users_all}

# ══════════════════════════════════════════════════════════════
# STAT CARDS
# fn_alert_count() → total alerts in system (mirrors SQL function)
# get_active_alerts_count() → active alerts via PL/SQL function
# ══════════════════════════════════════════════════════════════

# FUNCTION: get_active_alerts_count() — PostgreSQL PL/SQL function
active_alerts_count = supabase.rpc("get_active_alerts_count").execute().data or 0

c1, c2, c3, c4, c5 = st.columns(5)
for col, val, label, icon in zip(
    [c1, c2, c3, c4, c5],
    [
        len(sensors_all),
        len(readings_all),
        len(actuators_all),
        active_alerts_count,              # FUNCTION: get_active_alerts_count()
        fn_alert_count(alerts_all_raw),   # mirrors fn_alert_count() — total alerts
    ],
    ["SENSORS", "READINGS", "ACTUATORS", "ACTIVE ALERTS", "TOTAL ALERTS"],
    ["📡", "📊", "⚙️", "🔔", "🚨"],
):
    with col:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-icon">{icon}</div>
          <div class="stat-value">{val}</div>
          <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ANALYTICS CHARTS
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-heading">📊 Analytics Overview</div>', unsafe_allow_html=True)

ch1, ch2, ch3 = st.columns(3)

# Chart 1 — Sensor readings line chart (mirrors vw_sensor_status view)
with ch1:
    st.markdown("**Sensor Readings — Last 30** <span class='sql-badge'>vw_sensor_status</span>", unsafe_allow_html=True)
    if readings_all:
        df_r = pd.DataFrame(readings_all[-30:])
        df_r["recorded_at"] = pd.to_datetime(df_r["recorded_at"])
        fig = px.line(
            df_r, x="recorded_at", y="value", color="sensor_id",
            labels={"recorded_at":"", "value":"Value", "sensor_id":"Sensor"},
            color_discrete_sequence=["#3b82f6","#22c55e","#f59e0b","#ef4444","#a855f7"],
        )
        fig.update_layout(**CHART)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#2a2f3a")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No readings yet.")

# Chart 2 — Alert status donut (mirrors vw_active_alerts view)
with ch2:
    st.markdown("**Alert Status Breakdown** <span class='sql-badge'>vw_active_alerts</span>", unsafe_allow_html=True)
    if alerts_all_raw:
        df_a   = pd.DataFrame(alerts_all_raw)
        counts = df_a["alert_status"].value_counts().reset_index()
        counts.columns = ["status","count"]
        fig2 = px.pie(
            counts, names="status", values="count", hole=0.55,
            color="status",
            color_discrete_map={"active":"#ef4444","resolved":"#22c55e","ignored":"#64748b"},
        )
        fig2.update_layout(**CHART)
        fig2.update_traces(textfont_color="#e2e8f0")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No alerts yet.")

# Chart 3 — Actuator status bar chart
with ch3:
    st.markdown("**Actuator Status**", unsafe_allow_html=True)
    if actuators_all:
        df_act     = pd.DataFrame(actuators_all)
        counts_act = df_act["actuator_status"].value_counts().reset_index()
        counts_act.columns = ["status","count"]
        fig3 = px.bar(
            counts_act, x="status", y="count", color="status",
            color_discrete_map={"active":"#3b82f6","inactive":"#f59e0b","maintenance":"#ef4444"},
            labels={"status":"","count":"Count"},
        )
        fig3.update_layout(**CHART)
        fig3.update_xaxes(showgrid=False)
        fig3.update_yaxes(showgrid=True, gridcolor="#2a2f3a")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No actuators yet.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📡  Sensors & Stability",
    "📊  Sensor Readings",
    "⚙️  Actuators",
    "💧  Irrigation",
    "🔔  Alerts",
    "🔍  Analytics Queries",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SENSORS
# Uses: vw_sensor_status (sensor readings view)
#       fn_sensor_stability (stability classification)
#       QUERY 7 (fields with no sensors)
#       get_latest_reading() PL/SQL function
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown(
        '<div class="section-heading">Sensor Management'
        ' <span class="sql-badge">vw_sensor_status + fn_sensor_stability</span></div>',
        unsafe_allow_html=True
    )

    sensors_rich = fetch_all(
        "sensors",
        "sensor_id, sensor_type, installed_at, fields(field_name, farms(farm_name)), users(full_name)",
        _cb=cb()
    )

    # Build sensor table with stability column using fn_sensor_stability logic
    # and get_latest_reading() PL/SQL function for the latest value
    rows = []
    for s in sensors_rich:
        sensor_readings = [r for r in readings_all if r.get("sensor_id") == s["sensor_id"]]

        # fn_sensor_stability — classifies sensor based on reading spread
        stability = fn_sensor_stability(sensor_readings)

        # FUNCTION: get_latest_reading(p_sensor_id) — PL/SQL function call
        latest_val = supabase.rpc("get_latest_reading", {"p_sensor_id": s["sensor_id"]}).execute().data
        unit = {"soil_moisture": "%", "temperature": "°C", "humidity": "%"}.get(s["sensor_type"], "")
        latest_display = f"{latest_val} {unit}" if latest_val is not None else "—"

        rows.append({
            "ID":             s["sensor_id"],
            "Type":           s["sensor_type"],
            "Field":          (s.get("fields") or {}).get("field_name","—"),
            "Farm":           ((s.get("fields") or {}).get("farms") or {}).get("farm_name","—"),
            "Installed By":   (s.get("users") or {}).get("full_name","—"),
            "Installed At":   str(s.get("installed_at",""))[:16],
            "Latest Reading": latest_display,   # get_latest_reading() result
            "Stability":      stability,         # fn_sensor_stability result
        })
    show_table(rows, "No sensors found.")

    # QUERY 7: Fields with no sensors installed
    st.markdown(
        '<div class="section-heading">Fields With No Sensors'
        ' <span class="sql-badge">QUERY 7</span></div>',
        unsafe_allow_html=True
    )
    sensor_field_ids = {s.get("field_id") for s in sensors_all}
    fields_no_sensor = [
        {"Field ID": f["field_id"], "Field Name": f["field_name"]}
        for f in fields_all
        if f["field_id"] not in sensor_field_ids
    ]
    show_table(fields_no_sensor, "✅ All fields have at least one sensor installed.")

    st.markdown("---")

    with st.expander("➕ Add New Sensor"):
        c1, c2 = st.columns(2)
        with c1:
            s_type  = st.selectbox("Sensor Type", ["soil_moisture","temperature","humidity"], key="ns_type")
            s_field = st.selectbox("Field", list(field_opts.keys()), key="ns_field")
        with c2:
            s_user  = st.selectbox("Installed By", list(user_opts.keys()), key="ns_user")
        if st.button("Add Sensor →", key="add_sensor"):
            try:
                supabase.table("sensors").insert({
                    "sensor_type":  s_type,
                    "field_id":     field_opts[s_field],
                    "installed_by": user_opts[s_user],
                }).execute()
                bust(); ok("Sensor added."); st.rerun()
            except Exception as e:
                err(e)

    with st.expander("🗑️ Delete Sensor"):
        del_opts = {f"ID {s['sensor_id']} — {s['sensor_type']}": s["sensor_id"] for s in sensors_rich}
        if del_opts:
            sel = st.selectbox("Select Sensor", list(del_opts.keys()), key="del_sensor_sel")
            if st.button("Delete Sensor →", key="del_sensor"):
                try:
                    supabase.table("sensors").delete().eq("sensor_id", del_opts[sel]).execute()
                    bust(); ok("Sensor deleted."); st.rerun()
                except Exception as e:
                    err(e)
        else:
            st.info("No sensors to delete.")

# ══════════════════════════════════════════════════════════════
# TAB 2 — SENSOR READINGS
# Uses: vw_sensor_status (sensor readings with sensor type)
#       QUERY 4 (avg/min/max per field per sensor type)
# TRIGGER: trg_sensor_alert fires automatically on INSERT
#          creating alerts for out-of-range values
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown(
        '<div class="section-heading">Sensor Readings'
        ' <span class="sql-badge">vw_sensor_status + QUERY 4</span></div>',
        unsafe_allow_html=True
    )

    sensor_id_opts = {f"ID {s['sensor_id']} ({s['sensor_type']})": s["sensor_id"] for s in sensors_all}
    filter_s = st.selectbox("Filter by Sensor", ["All"] + list(sensor_id_opts.keys()), key="filter_readings")

    readings = readings_all if filter_s == "All" else [
        r for r in readings_all if r["sensor_id"] == sensor_id_opts[filter_s]
    ]

    # Mirrors vw_sensor_status view: sensor_id, sensor_type, value, recorded_at
    show_table([{
        "ID":          r["reading_id"],
        "Sensor Type": (r.get("sensors") or {}).get("sensor_type","—"),
        "Value":       r["value"],
        "Recorded At": str(r.get("recorded_at",""))[:16],
    } for r in readings], "No readings found.")

    # QUERY 4: Average, Min, Max per sensor type
    st.markdown(
        '<div class="section-heading">Avg / Min / Max per Sensor Type'
        ' <span class="sql-badge">QUERY 4</span></div>',
        unsafe_allow_html=True
    )
    if readings_all:
        df_q4 = pd.DataFrame([{
            "sensor_id":   r["sensor_id"],
            "sensor_type": (r.get("sensors") or {}).get("sensor_type","—"),
            "value":       r["value"],
        } for r in readings_all if r.get("value") is not None])

        if not df_q4.empty:
            agg = (
                df_q4.groupby("sensor_type")["value"]
                .agg(
                    Avg=lambda x: round(x.mean(), 2),
                    Min=lambda x: round(x.min(), 2),
                    Max=lambda x: round(x.max(), 2),
                    Total_Readings="count"
                )
                .reset_index()
                .rename(columns={"sensor_type":"Sensor Type"})
            )
            show_table(agg.to_dict("records"))
    else:
        st.info("No readings to aggregate.")

    st.markdown("---")

    # Adding a reading triggers trg_sensor_alert automatically
    with st.expander("➕ Add Sensor Reading  ·  triggers trg_sensor_alert automatically"):
        st.caption("⚡ Inserting a reading will auto-trigger trg_sensor_alert if value is out of range")
        c1, c2 = st.columns(2)
        with c1:
            r_sensor = st.selectbox("Sensor", list(sensor_id_opts.keys()), key="nr_sensor")
        with c2:
            r_value  = st.number_input("Value", min_value=0.0, step=0.1, key="nr_value")
        if st.button("Add Reading →", key="add_reading"):
            try:
                supabase.table("sensor_readings").insert({
                    "sensor_id": sensor_id_opts[r_sensor],
                    "value":     r_value,
                }).execute()
                # TRIGGER: trg_sensor_alert fires automatically after this insert
                # It checks if value is out of range and creates an alert if so
                bust(); ok("Reading added. Alert auto-checked by trg_sensor_alert."); st.rerun()
            except Exception as e:
                err(e)

# ══════════════════════════════════════════════════════════════
# TAB 3 — ACTUATORS
# Manages actuators and actuator actions (CRUD)
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-heading">Actuator Management</div>', unsafe_allow_html=True)

    actuators_rich = fetch_all(
        "actuators",
        "actuator_id, actuator_type, actuator_status, installation_date, fields(field_name)",
        _cb=cb()
    )
    show_table([{
        "ID":        a["actuator_id"],
        "Type":      a["actuator_type"],
        "Status":    a["actuator_status"],
        "Field":     (a.get("fields") or {}).get("field_name","—"),
        "Installed": str(a.get("installation_date",""))[:10],
    } for a in actuators_rich], "No actuators found.")

    st.markdown("---")

    with st.expander("➕ Add Actuator"):
        c1, c2 = st.columns(2)
        with c1:
            a_type  = st.text_input("Actuator Type (e.g. Water Pump)", key="na_type")
            a_field = st.selectbox("Field", list(field_opts.keys()), key="na_field")
        with c2:
            a_status = st.selectbox("Status", ["active","inactive","maintenance"], key="na_status")
            a_date   = st.date_input("Installation Date", value=date.today(), key="na_date")
        if st.button("Add Actuator →", key="add_act"):
            if not a_type.strip():
                st.warning("⚠️ Actuator type is required.")
            else:
                try:
                    supabase.table("actuators").insert({
                        "actuator_type":     a_type.strip(),
                        "field_id":          field_opts[a_field],
                        "actuator_status":   a_status,
                        "installation_date": str(a_date),
                    }).execute()
                    bust(); ok("Actuator added."); st.rerun()
                except Exception as e:
                    err(e)

    with st.expander("✏️ Update Actuator Status"):
        upd_opts = {f"ID {a['actuator_id']} — {a['actuator_type']}": a["actuator_id"] for a in actuators_rich}
        if upd_opts:
            c1, c2 = st.columns(2)
            with c1:
                upd_sel = st.selectbox("Select Actuator", list(upd_opts.keys()), key="upd_act_sel")
            with c2:
                new_st  = st.selectbox("New Status", ["active","inactive","maintenance"], key="upd_act_st")
            if st.button("Update Status →", key="upd_act"):
                try:
                    supabase.table("actuators").update({"actuator_status": new_st}).eq("actuator_id", upd_opts[upd_sel]).execute()
                    bust(); ok("Status updated."); st.rerun()
                except Exception as e:
                    err(e)
        else:
            st.info("No actuators available.")

    # Actuator Actions
    st.markdown('<div class="section-heading">Actuator Actions</div>', unsafe_allow_html=True)
    show_table([{
        "Action ID": ac["action_id"],
        "Actuator":  (ac.get("actuators") or {}).get("actuator_type","—"),
        "Start":     str(ac.get("start_time",""))[:16],
        "End":       str(ac.get("end_time",""))[:16] if ac.get("end_time") else "⏳ Ongoing",
    } for ac in actions_all], "No actuator actions recorded.")

    with st.expander("➕ Log Actuator Action"):
        act_log_opts = {f"ID {a['actuator_id']} — {a['actuator_type']}": a["actuator_id"] for a in actuators_rich}
        if act_log_opts:
            c1, c2 = st.columns(2)
            with c1:
                sel_act = st.selectbox("Actuator", list(act_log_opts.keys()), key="log_act_sel")
                start_d = st.date_input("Start Date", value=date.today(), key="log_act_sd")
                start_t = st.time_input("Start Time", value=datetime.now().time(), key="log_act_st")
            with c2:
                has_end = st.checkbox("Set end time?", key="log_act_has_end")
                end_d   = st.date_input("End Date", value=date.today(), key="log_act_ed", disabled=not has_end)
                end_t   = st.time_input("End Time", key="log_act_et", disabled=not has_end)
            if st.button("Log Action →", key="log_act"):
                try:
                    payload = {
                        "actuator_id": act_log_opts[sel_act],
                        "start_time":  datetime.combine(start_d, start_t).isoformat(),
                    }
                    if has_end:
                        payload["end_time"] = datetime.combine(end_d, end_t).isoformat()
                    supabase.table("actuator_actions").insert(payload).execute()
                    bust(); ok("Action logged."); st.rerun()
                except Exception as e:
                    err(e)
        else:
            st.info("Add an actuator first.")

# ══════════════════════════════════════════════════════════════
# TAB 4 — IRRIGATION
# Uses: vw_irrigation_summary (water usage per field)
#       sp_start_irrigation logic (mirrored as direct insert)
#       fn_water_efficiency (harvest per litre of water)
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown(
        '<div class="section-heading">Irrigation Management'
        ' <span class="sql-badge">vw_irrigation_summary + sp_start_irrigation</span></div>',
        unsafe_allow_html=True
    )

    show_table([{
        "ID":           ir["irrigation_id"],
        "Method":       ir["method"],
        "Water (L)":    ir["water_amount"],
        "Field":        (ir.get("fields") or {}).get("field_name","—"),
        "Action Start": str((ir.get("actuator_actions") or {}).get("start_time",""))[:16],
    } for ir in irrigation_all], "No irrigation records found.")

    # VIEW: vw_irrigation_summary — total water + session count per field
    st.markdown(
        '<div class="section-heading">Water Usage Summary per Field'
        ' <span class="sql-badge">vw_irrigation_summary</span></div>',
        unsafe_allow_html=True
    )

    # First try fetching from the actual view in Supabase
    irr_summary_view = supabase.table("vw_irrigation_summary").select("*").execute().data or []
    if irr_summary_view:
        # Use the actual view data from Supabase
        st.caption("📡 Fetched from **vw_irrigation_summary** view")
        show_table(irr_summary_view)
    elif irrigation_all:
        # Fallback: compute summary in Python if view not available
        st.caption("📡 Computed from irrigation records (vw_irrigation_summary logic)")
        df_irr = pd.DataFrame([{
            "field_name":   (ir.get("fields") or {}).get("field_name","—"),
            "water_amount": ir.get("water_amount", 0) or 0,
        } for ir in irrigation_all])
        summary = (
            df_irr.groupby("field_name")["water_amount"]
            .agg(Total_Water_Used_L="sum", Irrigation_Sessions="count")
            .reset_index()
            .rename(columns={"field_name": "Field"})
            .sort_values("Total_Water_Used_L", ascending=False)
        )
        show_table(summary.to_dict("records"))

    # fn_water_efficiency — harvest per litre of water per field
    st.markdown(
        '<div class="section-heading">Water Efficiency per Field'
        ' <span class="sql-badge">fn_water_efficiency</span></div>',
        unsafe_allow_html=True
    )
    eff_rows = []
    for f in fields_all:
        fid          = f["field_id"]
        irr_records  = [ir for ir in irrigation_all if ir.get("field_id") == fid]
        harv_records = [h  for h  in harvests_all   if h.get("field_id")  == fid]
        eff_rows.append({
            "Field":              f["field_name"],
            "Total Water (L)":    sum(r.get("water_amount",0) or 0 for r in irr_records),
            "Total Harvest (kg)": fn_total_harvest(harv_records),   # fn_total_harvest logic
            "Efficiency (kg/L)":  fn_water_efficiency(irr_records, harv_records),  # fn_water_efficiency logic
        })
    show_table(eff_rows, "No data available.")

    st.markdown("---")

    # sp_start_irrigation — mirrors the stored procedure logic
    with st.expander("➕ Log Irrigation  ·  mirrors sp_start_irrigation"):
        st.caption("🔁 Mirrors sp_start_irrigation(field_id, actuator_id, water_amount) — logs an irrigation session")
        action_opts = {
            f"Action ID {a['action_id']} ({str(a.get('start_time',''))[:16]})": a["action_id"]
            for a in actions_all
        }
        c1, c2 = st.columns(2)
        with c1:
            ir_action = st.selectbox(
                "Actuator Action",
                list(action_opts.keys()) if action_opts else ["— No actions available —"],
                key="new_ir_action"
            )
            ir_field = st.selectbox("Field", list(field_opts.keys()), key="new_ir_field")
        with c2:
            ir_method = st.selectbox("Method", ["drip","sprinkler","flood","manual"], key="new_ir_method")
            ir_water  = st.number_input("Water Amount (Litres)", min_value=0.1, step=0.5, key="new_ir_water")
        if st.button("Log Irrigation →", key="add_ir"):
            if not action_opts:
                st.warning("⚠️ No actuator actions available. Log an action first.")
            else:
                try:
                    # Mirrors sp_start_irrigation(field_id, actuator_id, water_amount)
                    supabase.table("irrigation").insert({
                        "action_id":    action_opts[ir_action],
                        "field_id":     field_opts[ir_field],
                        "method":       ir_method,
                        "water_amount": ir_water,
                    }).execute()
                    bust(); ok("Irrigation logged."); st.rerun()
                except Exception as e:
                    err(e)

    with st.expander("🗑️ Delete Irrigation Record"):
        ir_del = {f"ID {ir['irrigation_id']} — {ir['method']}": ir["irrigation_id"] for ir in irrigation_all}
        if ir_del:
            sel = st.selectbox("Select Record", list(ir_del.keys()), key="del_ir_sel")
            if st.button("Delete →", key="del_ir"):
                try:
                    supabase.table("irrigation").delete().eq("irrigation_id", ir_del[sel]).execute()
                    bust(); ok("Record deleted."); st.rerun()
                except Exception as e:
                    err(e)
        else:
            st.info("No records to delete.")

# ══════════════════════════════════════════════════════════════
# TAB 5 — ALERTS
# Uses: vw_active_alerts (real-time active alerts)
#       sp_create_alert logic (manual alert creation)
#       get_active_alerts_count() PL/SQL function
# TRIGGER: trg_sensor_alert auto-creates alerts on bad readings
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown(
        '<div class="section-heading">Alerts Overview'
        ' <span class="sql-badge">vw_active_alerts + sp_create_alert</span></div>',
        unsafe_allow_html=True
    )

    status_filter = st.selectbox("Filter by Status", ["all","active","resolved","ignored"], key="alert_filter")

    if status_filter == "active":
        # VIEW: vw_active_alerts — fetch directly from the view for active alerts
        alerts = supabase.table("vw_active_alerts").select("*").execute().data or []
        st.caption("📡 Fetched from **vw_active_alerts** view")
    elif status_filter == "all":
        alerts = alerts_all_raw
    else:
        alerts = [a for a in alerts_all_raw if a.get("alert_status") == status_filter]

    # FUNCTION: get_active_alerts_count() — display active count
    st.write(f"**{len(alerts)} alert(s) shown** · 🔴 {active_alerts_count} active (via `get_active_alerts_count()`)")

    if alerts:
        for al in alerts:
            status   = al.get("alert_status","active")
            badge    = f'<span class="badge-{status}">{status.upper()}</span>'
            field_nm = (al.get("fields") or {}).get("field_name","—")
            ts       = str(al.get("created_at",""))[:16]

            col_info, col_btn = st.columns([7, 2])
            with col_info:
                st.markdown(
                    f"**#{al['alert_id']}** — {al['alert_type']} &nbsp; {badge} &nbsp; "
                    f"<span style='color:#64748b;font-size:13px;'>Field: {field_nm} | {ts}</span>",
                    unsafe_allow_html=True
                )
            with col_btn:
                if status == "active":
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Resolve", key=f"resolve_{al['alert_id']}"):
                            try:
                                supabase.table("alerts").update({"alert_status":"resolved"}).eq("alert_id", al["alert_id"]).execute()
                                bust(); ok(f"Alert #{al['alert_id']} resolved."); st.rerun()
                            except Exception as e:
                                err(e)
                    with b2:
                        if st.button("Ignore", key=f"ignore_{al['alert_id']}"):
                            try:
                                supabase.table("alerts").update({"alert_status":"ignored"}).eq("alert_id", al["alert_id"]).execute()
                                bust(); st.rerun()
                            except Exception as e:
                                err(e)
            st.markdown("---")
    else:
        st.info("No alerts found for the selected filter.")

    # sp_create_alert — manual alert creation mirrors the stored procedure
    with st.expander("➕ Create Manual Alert  ·  mirrors sp_create_alert"):
        st.caption("🔁 Mirrors sp_create_alert(reading_id, alert_type) — inserts alert with status 'active'")
        c1, c2 = st.columns(2)
        with c1:
            m_field  = st.selectbox("Field", list(field_opts.keys()), key="ma_field")
            m_type   = st.text_input("Alert Description", placeholder="e.g. Equipment fault detected", key="ma_type")
        with c2:
            m_status = st.selectbox("Initial Status", ["active","resolved","ignored"], key="ma_status")
        if st.button("Create Alert →", key="create_alert"):
            if not m_type.strip():
                st.warning("⚠️ Alert description is required.")
            else:
                try:
                    # Mirrors sp_create_alert(reading_id, alert_type) logic:
                    # Inserts a new alert with status 'active' and no linked reading (manual)
                    supabase.table("alerts").insert({
                        "field_id":     field_opts[m_field],
                        "alert_type":   m_type.strip(),
                        "alert_status": m_status,
                        "reading_id":   None,  # NULL = manual alert (no sensor reading)
                    }).execute()
                    bust(); ok("Manual alert created."); st.rerun()
                except Exception as e:
                    err(e)

# ══════════════════════════════════════════════════════════════
# TAB 6 — ANALYTICS QUERIES
# Uses: fn_sensor_stability (stability per sensor)
#       fn_water_efficiency (efficiency per field)
#       fn_total_harvest (total harvest per field)
#       QUERY 4 (avg/min/max per field per sensor type)
#       QUERY 7 (fields with no sensors)
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-heading">Advanced Analytics</div>', unsafe_allow_html=True)

    # fn_sensor_stability — stability report per sensor
    st.markdown(
        "**Sensor Stability Report** <span class='sql-badge'>fn_sensor_stability</span>",
        unsafe_allow_html=True
    )
    st.caption("Mirrors fn_sensor_stability(p_sensor_id) — classifies each sensor as STABLE / MODERATE / UNSTABLE")
    stab_rows = []
    for s in sensors_all:
        sensor_readings = [r for r in readings_all if r.get("sensor_id") == s["sensor_id"]]
        stability = fn_sensor_stability(sensor_readings)  # fn_sensor_stability logic
        values    = [r["value"] for r in sensor_readings if r.get("value") is not None]
        stab_rows.append({
            "Sensor ID":      s["sensor_id"],
            "Type":           s["sensor_type"],
            "Total Readings": len(values),
            "Min Value":      round(min(values), 2) if values else "—",
            "Max Value":      round(max(values), 2) if values else "—",
            "Spread":         round(max(values) - min(values), 2) if values else "—",
            "Stability":      stability,
        })
    show_table(stab_rows, "No sensors found.")

    st.markdown("---")

    # QUERY 4: Average/Min/Max per field per sensor type
    st.markdown(
        "**Average Sensor Readings per Field** <span class='sql-badge'>QUERY 4</span>",
        unsafe_allow_html=True
    )
    st.caption("Matches QUERY 4 — avg, min, max readings grouped by field and sensor type")
    if readings_all and sensors_all and fields_all:
        sensor_map = {s["sensor_id"]: s for s in sensors_all}
        field_map  = {f["field_id"]:  f for f in fields_all}

        q4_rows = []
        for r in readings_all:
            s   = sensor_map.get(r.get("sensor_id"), {})
            fid = s.get("field_id")
            f   = field_map.get(fid, {})
            if r.get("value") is not None:
                q4_rows.append({
                    "field_name":  f.get("field_name","—"),
                    "sensor_type": s.get("sensor_type","—"),
                    "value":       r["value"],
                })

        if q4_rows:
            df_q4b = pd.DataFrame(q4_rows)
            agg_q4 = (
                df_q4b.groupby(["field_name","sensor_type"])["value"]
                .agg(
                    Avg_Reading=lambda x: round(x.mean(), 2),
                    Min_Reading=lambda x: round(x.min(), 2),
                    Max_Reading=lambda x: round(x.max(), 2),
                    Total_Readings="count",
                )
                .reset_index()
                .rename(columns={"field_name":"Field","sensor_type":"Sensor Type"})
            )
            show_table(agg_q4.to_dict("records"))
        else:
            st.info("Not enough data for this query.")
    else:
        st.info("No data available.")

    st.markdown("---")

    # fn_water_efficiency — efficiency summary across all fields
    st.markdown(
        "**Water Efficiency per Field** <span class='sql-badge'>fn_water_efficiency</span>",
        unsafe_allow_html=True
    )
    st.caption("Mirrors fn_water_efficiency(p_field_id) — kg of harvest per litre of water used")
    eff_rows = []
    for f in fields_all:
        fid          = f["field_id"]
        irr_records  = [ir for ir in irrigation_all if ir.get("field_id") == fid]
        harv_records = [h  for h  in harvests_all   if h.get("field_id")  == fid]
        eff_rows.append({
            "Field":             f["field_name"],
            "Water Used (L)":    sum(r.get("water_amount",0) or 0 for r in irr_records),
            "Harvest (kg)":      fn_total_harvest(harv_records),         # fn_total_harvest logic
            "Efficiency (kg/L)": fn_water_efficiency(irr_records, harv_records),  # fn_water_efficiency logic
        })
    show_table(eff_rows, "No field data.")

    st.markdown("---")

    # QUERY 7: Fields with no sensors installed
    st.markdown(
        "**Fields With No Sensors Installed** <span class='sql-badge'>QUERY 7</span>",
        unsafe_allow_html=True
    )
    st.caption("Matches QUERY 7 — fields not present in the sensors table")
    sensor_fids      = {s.get("field_id") for s in sensors_all}
    no_sensor_fields = [
        {"Field ID": f["field_id"], "Field Name": f["field_name"]}
        for f in fields_all if f["field_id"] not in sensor_fids
    ]
    show_table(no_sensor_fields, "✅ All fields have at least one sensor installed.")