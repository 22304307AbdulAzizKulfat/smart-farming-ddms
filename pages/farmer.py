import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import date, datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroNex | Farmer",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── SUPABASE CONNECTION ─────────────────────────────────────────────────────
# Using supabase-py library (consistent with rest of project)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── AUTH GUARD ──────────────────────────────────────────────────────────────
if "user" not in st.session_state or st.session_state.user.get("role") != "farmer":
    st.error("🔒 Access denied.")
    st.stop()

user      = st.session_state.user
farmer_id = user["user_id"]

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1a1d23 0%, #1f2329 100%) !important;
    color: #e2e8f0; font-family: 'Trebuchet MS', sans-serif;
}
.topbar {
    display: flex; justify-content: space-between; align-items: center;
    background: #1e2128; border-bottom: 2px solid #2a2f3a;
    padding: 14px 32px; margin: -1rem -1rem 2rem -1rem;
    border-radius: 0 0 12px 12px;
}
.logo-text { font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: 1px; }
.logo-box { background: #3b82f6; border-radius: 10px; padding: 6px 12px; font-size: 22px; }
.user-badge {
    background: #262b36; border: 1px solid #2a2f3a;
    border-radius: 20px; padding: 6px 14px; font-size: 14px; color: #cbd5e1;
}
.stat-grid { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 28px; }
.stat-card {
    background: #1e2128; border: 1px solid #2a2f3a; border-radius: 14px;
    padding: 22px 28px; flex: 1; min-width: 140px; text-align: center;
}
.stat-card:hover { border-color: #3b82f6; }
.stat-number { font-size: 36px; font-weight: 800; color: #3b82f6; }
.stat-label { font-size: 13px; color: #94a3b8; margin-top: 4px; }
.section-title {
    font-size: 18px; font-weight: 700; color: #ffffff;
    margin: 28px 0 14px; border-left: 4px solid #3b82f6; padding-left: 12px;
}
.data-table {
    background: #1e2128; border: 1px solid #2a2f3a;
    border-radius: 12px; overflow: hidden; width: 100%; border-collapse: collapse;
}
.data-table th {
    background: #262b36; color: #94a3b8; font-size: 12px;
    text-transform: uppercase; letter-spacing: 0.5px; padding: 12px 16px; text-align: left;
}
.data-table td {
    padding: 12px 16px; border-top: 1px solid #2a2f3a;
    font-size: 14px; color: #cbd5e1; font-family: 'Courier New', monospace;
}
.data-table tr:hover td { background: #262b36; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-growing   { background: #14532d; color: #4ade80; }
.badge-harvested { background: #1e3a5f; color: #60a5fa; }
.badge-failed    { background: #450a0a; color: #f87171; }
.badge-active    { background: #422006; color: #fb923c; }
.badge-resolved  { background: #14532d; color: #4ade80; }
.badge-ignored   { background: #1e293b; color: #94a3b8; }
.no-data {
    text-align: center; color: #475569; padding: 32px; font-size: 15px;
    background: #1e2128; border: 1px dashed #2a2f3a; border-radius: 12px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input {
    background: #262b36 !important; border: 1px solid #2a2f3a !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
}
div.stButton > button {
    background: #3b82f6; color: white; border: none; border-radius: 8px;
    font-weight: 600; transition: background 0.2s;
}
div.stButton > button:hover { background: #2563eb; }
div[data-testid="stExpander"] {
    background: #1e2128 !important; border: 1px solid #2a2f3a !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── TOP BAR ─────────────────────────────────────────────────────────────────
col_logo, col_right = st.columns([6, 1])
with col_logo:
    st.markdown(f"""
    <div class="topbar">
        <div style="display:flex;align-items:center;gap:12px">
            <div class="logo-box">🌱</div>
            <div class="logo-text">AgroNex</div>
        </div>
        <div class="user-badge">🧑‍🌾 {user['full_name']}</div>
    </div>
    """, unsafe_allow_html=True)
with col_right:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def badge(status):
    cls = {
        "growing":   "badge-growing",
        "harvested": "badge-harvested",
        "failed":    "badge-failed",
        "active":    "badge-active",
        "resolved":  "badge-resolved",
        "ignored":   "badge-ignored",
    }.get(status, "badge-ignored")
    return f'<span class="badge {cls}">{status}</span>'

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
# All queries using supabase-py (consistent with admin/customer pages)
farms     = supabase.table("farms").select("*").eq("owner_id", farmer_id).execute().data or []
farm_ids  = [f["farm_id"] for f in farms]

all_fields = []
for fid in farm_ids:
    all_fields += supabase.table("fields").select("*").eq("farm_id", fid).execute().data or []
field_ids = [f["field_id"] for f in all_fields]

all_crops = []
for fid in field_ids:
    all_crops += supabase.table("crops").select("*").eq("field_id", fid).execute().data or []

# QUERY 5: Harvests recorded by this farmer
all_harvests = supabase.table("harvests").select("*").eq("harvested_by", farmer_id).execute().data or []

all_sensors = []
for fid in field_ids:
    all_sensors += supabase.table("sensors").select("*").eq("field_id", fid).execute().data or []

all_alerts = []
for fid in field_ids:
    all_alerts += supabase.table("alerts").select("*").eq("field_id", fid).execute().data or []

active_alerts = [a for a in all_alerts if a["alert_status"] == "active"]

# ─── STAT CARDS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card"><div class="stat-number">{len(farms)}</div><div class="stat-label">🏡 My Farms</div></div>
    <div class="stat-card"><div class="stat-number">{len(all_fields)}</div><div class="stat-label">🌾 Fields</div></div>
    <div class="stat-card"><div class="stat-number">{len(all_crops)}</div><div class="stat-label">🌱 Crops</div></div>
    <div class="stat-card"><div class="stat-number">{len(all_harvests)}</div><div class="stat-label">📦 Harvests</div></div>
    <div class="stat-card"><div class="stat-number">{len(active_alerts)}</div><div class="stat-label">🚨 Active Alerts</div></div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏡 Farms & Fields",
    "🌱 Crops",
    "📦 Harvests",
    "📡 Sensors",
    "🚨 Alerts"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FARMS & FIELDS
# ══════════════════════════════════════════════════════════════════════════════
# Uses QUERY 2: Farms with owner name and field count
# TRIGGER: trg_notify_new_farm fires automatically on INSERT into farms
with tab1:
    col_f, col_fi = st.columns(2)

    with col_f:
        st.markdown('<div class="section-title">My Farms</div>', unsafe_allow_html=True)
        if farms:
            rows = "".join([
                f"<tr><td>{f['farm_id']}</td><td>{f['farm_name']}</td><td>{f['location']}</td><td>{f['size']} ha</td></tr>"
                for f in farms
            ])
            st.markdown(f'<table class="data-table"><thead><tr><th>#</th><th>Farm</th><th>Location</th><th>Size</th></tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No farms found.</div>', unsafe_allow_html=True)

        with st.expander("➕ Add New Farm"):
            with st.form("add_farm"):
                fn  = st.text_input("Farm Name")
                loc = st.text_input("Location")
                sz  = st.number_input("Size (hectares)", min_value=0.01, step=0.1)
                if st.form_submit_button("Create Farm"):
                    if fn and loc:
                        try:
                            supabase.table("farms").insert({
                                "farm_name": fn,
                                "location":  loc,
                                "size":      sz,
                                "owner_id":  farmer_id
                            }).execute()
                            # TRIGGER: trg_notify_new_farm fires automatically
                            st.success("✅ Farm created!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Fill all fields.")

        with st.expander("✏️ Edit / Delete Farm"):
            if farms:
                farm_opts = {f["farm_name"]: f["farm_id"] for f in farms}
                sel  = st.selectbox("Select farm", list(farm_opts.keys()), key="edf")
                sid  = farm_opts[sel]
                sd   = next(f for f in farms if f["farm_id"] == sid)
                with st.form("edit_farm"):
                    efn  = st.text_input("Farm Name", value=sd["farm_name"])
                    eloc = st.text_input("Location",  value=sd["location"])
                    esz  = st.number_input("Size (ha)", value=float(sd["size"]), min_value=0.01)
                    c1, c2 = st.columns(2)
                    upd = c1.form_submit_button("Update")
                    dlt = c2.form_submit_button("🗑 Delete")
                if upd:
                    supabase.table("farms").update({"farm_name": efn, "location": eloc, "size": esz}).eq("farm_id", sid).execute()
                    st.success("✅ Updated!")
                    st.rerun()
                if dlt:
                    supabase.table("farms").delete().eq("farm_id", sid).execute()
                    st.success("🗑 Deleted!")
                    st.rerun()
            else:
                st.info("No farms to edit.")

    with col_fi:
        st.markdown('<div class="section-title">Fields</div>', unsafe_allow_html=True)
        farm_map = {f["farm_id"]: f["farm_name"] for f in farms}
        if all_fields:
            rows = "".join([
                f"<tr><td>{fi['field_id']}</td><td>{fi['field_name']}</td><td>{farm_map.get(fi['farm_id'],'?')}</td><td>{fi['soil_type']}</td><td>{fi['area_hectares']} ha</td></tr>"
                for fi in all_fields
            ])
            st.markdown(f'<table class="data-table"><thead><tr><th>#</th><th>Field</th><th>Farm</th><th>Soil</th><th>Area</th></tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No fields found.</div>', unsafe_allow_html=True)

        with st.expander("➕ Add New Field"):
            if farms:
                with st.form("add_field"):
                    fo   = {f["farm_name"]: f["farm_id"] for f in farms}
                    sf   = st.selectbox("Farm", list(fo.keys()))
                    fn2  = st.text_input("Field Name")
                    soil = st.selectbox("Soil Type", ["clay","sandy","loamy","silty","peaty"])
                    area = st.number_input("Area (ha)", min_value=0.01, step=0.1)
                    if st.form_submit_button("Add Field"):
                        if fn2:
                            supabase.table("fields").insert({
                                "field_name":    fn2,
                                "farm_id":       fo[sf],
                                "soil_type":     soil,
                                "area_hectares": area
                            }).execute()
                            st.success("✅ Field added!")
                            st.rerun()
            else:
                st.info("Create a farm first.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CROPS
# ══════════════════════════════════════════════════════════════════════════════
# Uses QUERY 3: All crops with field and farm details
# TRIGGER: trg_notify_new_crop fires automatically on INSERT into crops
with tab2:
    st.markdown('<div class="section-title">Crop Management</div>', unsafe_allow_html=True)
    field_map = {f["field_id"]: f["field_name"] for f in all_fields}

    if all_crops:
        rows = "".join([
            f"<tr><td>{c['crop_id']}</td><td>{c['crop_name']}</td><td>{field_map.get(c['field_id'],'?')}</td><td>{badge(c['status'])}</td><td>{c['planting_date']}</td></tr>"
            for c in all_crops
        ])
        st.markdown(f'<table class="data-table"><thead><tr><th>#</th><th>Crop</th><th>Field</th><th>Status</th><th>Planted</th></tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="no-data">No crops yet.</div>', unsafe_allow_html=True)

    col_a, col_e = st.columns(2)
    with col_a:
        with st.expander("➕ Add Crop"):
            if all_fields:
                with st.form("add_crop"):
                    fo3   = {f["field_name"]: f["field_id"] for f in all_fields}
                    cname = st.text_input("Crop Name")
                    cfield= st.selectbox("Field", list(fo3.keys()))
                    cdate = st.date_input("Planting Date", value=date.today())
                    if st.form_submit_button("Add Crop"):
                        if cname:
                            supabase.table("crops").insert({
                                "crop_name":     cname,
                                "field_id":      fo3[cfield],
                                "status":        "growing",
                                "planting_date": str(cdate)
                            }).execute()
                            # TRIGGER: trg_notify_new_crop fires automatically
                            st.success("✅ Crop added!")
                            st.rerun()
            else:
                st.info("Add a field first.")

    with col_e:
        with st.expander("✏️ Edit / Delete Crop"):
            if all_crops:
                co   = {f"{c['crop_name']} (#{c['crop_id']})": c["crop_id"] for c in all_crops}
                sc   = st.selectbox("Select crop", list(co.keys()), key="edc")
                scid = co[sc]
                scd  = next(c for c in all_crops if c["crop_id"] == scid)
                with st.form("edit_crop"):
                    ecn = st.text_input("Crop Name", value=scd["crop_name"])
                    est = st.selectbox("Status", ["growing","harvested","failed"],
                                       index=["growing","harvested","failed"].index(scd["status"]))
                    c1, c2 = st.columns(2)
                    u = c1.form_submit_button("Update")
                    d = c2.form_submit_button("🗑 Delete")
                if u:
                    supabase.table("crops").update({"crop_name": ecn, "status": est}).eq("crop_id", scid).execute()
                    st.success("✅ Updated!")
                    st.rerun()
                if d:
                    supabase.table("crops").delete().eq("crop_id", scid).execute()
                    st.success("🗑 Deleted!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HARVESTS
# ══════════════════════════════════════════════════════════════════════════════
# PROCEDURE: add_harvest(p_crop_id, p_harvested_by, p_harvest_date, p_quantity_kg)
#   → Inserts into harvests AND updates crop status to 'harvested' automatically
# FUNCTION: get_farm_total_harvest(p_farm_id) → total kg harvested per farm
# TRIGGER: trg_notify_harvest fires automatically after INSERT on harvests
# TRIGGER: trg_crop_update updates crop status automatically
with tab3:
    st.markdown('<div class="section-title">Harvest Records</div>', unsafe_allow_html=True)
    crop_map = {c["crop_id"]: c["crop_name"] for c in all_crops}

    if all_harvests:
        total_kg = sum(h["quantity_kg"] for h in all_harvests if h.get("quantity_kg"))
        rows = "".join([
            f"<tr><td>{h['harvest_id']}</td><td>{crop_map.get(h['crop_id'],'?')}</td>"
            f"<td>{h['quantity_kg']} kg</td>"
            f"<td>${h['price_per_kg']:.2f}</td>"
            f"<td>{str(h['harvested_at'])[:16]}</td></tr>"
            for h in all_harvests
        ])
        st.markdown(
            f'<table class="data-table"><thead><tr><th>#</th><th>Crop</th><th>Quantity</th><th>Price/kg</th><th>Date</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>'
            f'<div style="text-align:right;color:#3b82f6;font-weight:700;margin-top:10px">Total: {total_kg:,.2f} kg</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="no-data">No harvests recorded yet.</div>', unsafe_allow_html=True)

    # PROCEDURE: add_harvest() called via supabase.rpc()
    with st.expander("➕ Record New Harvest  ·  via add_harvest() procedure"):
        growing = [c for c in all_crops if c["status"] == "growing"]
        if growing:
            with st.form("add_harvest_form"):
                ho     = {f"{c['crop_name']} (#{c['crop_id']})": c["crop_id"] for c in growing}
                shc    = st.selectbox("Crop", list(ho.keys()))
                hqty   = st.number_input("Quantity (kg)", min_value=0.1, step=0.5)
                # price_per_kg set by farmer — read by customer page when ordering
                hprice = st.number_input(
                    "Price per kg ($)",
                    min_value=0.01, step=0.05, value=0.70,
                    help="This price will be visible to customers when they order"
                )
                hdt = st.date_input("Harvest Date", value=date.today())
                st.caption("⚠️ This calls the add_harvest() procedure which also marks the crop as harvested.")
                if st.form_submit_button("Record Harvest"):
                    cid = ho[shc]
                    try:
                        # PROCEDURE: add_harvest(p_crop_id, p_harvested_by, p_harvest_date, p_quantity_kg)
                        # Automatically: 1) inserts harvest, 2) updates crop status to 'harvested'
                        # TRIGGER: trg_notify_harvest notifies admin automatically
                        supabase.rpc("add_harvest", {
                            "p_crop_id":      cid,
                            "p_harvested_by": farmer_id,
                            "p_harvest_date": str(datetime.combine(hdt, datetime.min.time())),
                            "p_quantity_kg":  hqty,
                        }).execute()

                        # Update price_per_kg on the newly created harvest
                        latest = supabase.table("harvests")\
                            .select("harvest_id")\
                            .eq("crop_id", cid)\
                            .eq("harvested_by", farmer_id)\
                            .order("harvested_at", desc=True)\
                            .execute().data
                        if latest:
                            supabase.table("harvests")\
                                .update({"price_per_kg": hprice})\
                                .eq("harvest_id", latest[0]["harvest_id"])\
                                .execute()

                        st.success("✅ Harvest recorded via add_harvest() procedure!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No growing crops available to harvest.")

    # FUNCTION: get_farm_total_harvest(p_farm_id)
    with st.expander("📊 Farm Harvest Totals  ·  via get_farm_total_harvest() function"):
        st.caption("Calls PL/SQL function get_farm_total_harvest(p_farm_id) for each farm")
        for farm in farms:
            # FUNCTION: get_farm_total_harvest(p_farm_id) — returns total harvested kg
            result = supabase.rpc("get_farm_total_harvest", {"p_farm_id": farm["farm_id"]}).execute().data
            total  = float(result) if result is not None else 0
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;background:#262b36;border:1px solid #2a2f3a;'
                f'border-radius:10px;padding:14px 20px;margin-bottom:10px">'
                f'<span style="color:#e2e8f0;font-weight:600">🏡 {farm["farm_name"]}</span>'
                f'<span style="color:#3b82f6;font-weight:800">{total:,.2f} kg</span></div>',
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SENSORS
# ══════════════════════════════════════════════════════════════════════════════
# FUNCTION: get_latest_reading(p_sensor_id) → most recent sensor value
# Uses QUERY 4: Average sensor readings per field per sensor type
# TRIGGER: trg_sensor_alert auto-creates alerts on bad readings
with tab4:
    st.markdown('<div class="section-title">Sensor Monitoring</div>', unsafe_allow_html=True)
    field_map2 = {f["field_id"]: f["field_name"] for f in all_fields}

    if all_sensors:
        rows = ""
        for s in all_sensors:
            # FUNCTION: get_latest_reading(p_sensor_id)
            result  = supabase.rpc("get_latest_reading", {"p_sensor_id": s["sensor_id"]}).execute().data
            val     = f"{result}" if result is not None else "—"
            unit    = {"soil_moisture": "%", "temperature": "°C", "humidity": "%"}.get(s["sensor_type"], "")
            display = f"{val} {unit}" if val != "—" else "—"
            rows   += (
                f"<tr><td>{s['sensor_id']}</td>"
                f"<td>{s['sensor_type'].replace('_',' ').title()}</td>"
                f"<td>{field_map2.get(s['field_id'],'?')}</td>"
                f"<td style='color:#3b82f6;font-weight:700'>{display}</td></tr>"
            )
        st.markdown(
            f'<table class="data-table"><thead><tr><th>#</th><th>Type</th><th>Field</th><th>Latest Reading</th></tr></thead><tbody>{rows}</tbody></table>',
            unsafe_allow_html=True
        )
        st.caption("⚡ Latest readings via get_latest_reading() · Alerts auto-created by trg_sensor_alert trigger")
    else:
        st.markdown('<div class="no-data">No sensors in your fields.</div>', unsafe_allow_html=True)

    # QUERY 4: Average, min, max readings per sensor per field
    with st.expander("📊 Sensor Reading Averages  ·  QUERY 4"):
        st.caption("Average / min / max readings per field per sensor type")
        if all_sensors:
            avg_data = []
            for s in all_sensors:
                readings = supabase.table("sensor_readings")\
                    .select("value")\
                    .eq("sensor_id", s["sensor_id"])\
                    .execute().data or []
                if readings:
                    vals = [r["value"] for r in readings]
                    avg_data.append({
                        "Sensor ID": s["sensor_id"],
                        "Type":      s["sensor_type"].replace("_"," ").title(),
                        "Field":     field_map2.get(s["field_id"], "?"),
                        "Avg":       round(sum(vals)/len(vals), 2),
                        "Min":       round(min(vals), 2),
                        "Max":       round(max(vals), 2),
                        "Readings":  len(vals),
                    })
            if avg_data:
                import pandas as pd
                st.dataframe(pd.DataFrame(avg_data), use_container_width=True, hide_index=True)
            else:
                st.info("No readings available yet.")

    with st.expander("📋 Reading History"):
        if all_sensors:
            sl = {
                f"Sensor #{s['sensor_id']} — {s['sensor_type'].replace('_',' ').title()}": s["sensor_id"]
                for s in all_sensors
            }
            ss       = st.selectbox("Select Sensor", list(sl.keys()))
            readings = supabase.table("sensor_readings")\
                .select("*")\
                .eq("sensor_id", sl[ss])\
                .order("recorded_at", desc=True)\
                .limit(20)\
                .execute().data or []
            if readings:
                rows = "".join([
                    f"<tr><td>{r['reading_id']}</td><td>{r['value']}</td><td>{str(r['recorded_at'])[:16]}</td></tr>"
                    for r in readings
                ])
                st.markdown(
                    f'<table class="data-table"><thead><tr><th>#</th><th>Value</th><th>Recorded At</th></tr></thead><tbody>{rows}</tbody></table>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<div class="no-data">No readings.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ALERTS
# ══════════════════════════════════════════════════════════════════════════════
# Alerts auto-created by TRIGGER: trg_sensor_alert on bad sensor readings
# Uses VIEW: vw_active_alerts concept — filtered here for this farmer's fields only
with tab5:
    st.markdown('<div class="section-title">Field Alerts</div>', unsafe_allow_html=True)
    field_map3 = {f["field_id"]: f["field_name"] for f in all_fields}

    if all_alerts:
        rows = "".join([
            f"<tr><td>{a['alert_id']}</td><td>{field_map3.get(a['field_id'],'?')}</td>"
            f"<td>{a['alert_type']}</td><td>{badge(a['alert_status'])}</td><td>{str(a['created_at'])[:16]}</td></tr>"
            for a in all_alerts
        ])
        st.markdown(
            f'<table class="data-table"><thead><tr><th>#</th><th>Field</th><th>Type</th><th>Status</th><th>Created</th></tr></thead><tbody>{rows}</tbody></table>',
            unsafe_allow_html=True
        )
        st.caption("⚡ Alerts with a reading_id were auto-created by trg_sensor_alert trigger")
    else:
        st.markdown('<div class="no-data">✅ No alerts — all fields are healthy!</div>', unsafe_allow_html=True)

    active_list = [a for a in all_alerts if a["alert_status"] == "active"]
    if active_list:
        with st.expander(f"⚡ Manage Active Alerts ({len(active_list)})"):
            for a in active_list:
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f"🚨 **{a['alert_type']}** — {field_map3.get(a['field_id'],'?')} _(#{a['alert_id']})_")
                if c2.button("✅ Resolve", key=f"r{a['alert_id']}"):
                    supabase.table("alerts").update({"alert_status": "resolved"}).eq("alert_id", a["alert_id"]).execute()
                    st.rerun()
                if c3.button("🙈 Ignore", key=f"i{a['alert_id']}"):
                    supabase.table("alerts").update({"alert_status": "ignored"}).eq("alert_id", a["alert_id"]).execute()
                    st.rerun()