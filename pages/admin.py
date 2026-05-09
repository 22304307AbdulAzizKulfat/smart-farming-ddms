import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroNex — Admin",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── AUTH GUARD ─────────────────────────────────────────────────────────────
if "user" not in st.session_state or st.session_state.user.get("role") != "admin":
    st.error("🔒 Access denied. Please log in as Admin.")
    st.stop()

# ─── SUPABASE CONNECTION ─────────────────────────────────────────────────────
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

user = st.session_state.user

# ─── STYLES ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1a1d23 0%, #1f2329 100%);
    color: #e2e8f0;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none; }
section.main > div { padding-top: 1rem; }
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    background: #1e2128; border: 1px solid #2a2f3a;
    border-radius: 12px; padding: 14px 24px; margin-bottom: 24px;
}
.topbar-left { display: flex; align-items: center; gap: 14px; }
.logo-box {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    border-radius: 10px; padding: 8px 12px; font-size: 22px; line-height: 1;
}
.topbar-title { font-family: 'Trebuchet MS', sans-serif; font-size: 20px; font-weight: 700; color: #f1f5f9; }
.topbar-sub { font-size: 12px; color: #64748b; }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.user-badge {
    background: #262b36; border: 1px solid #2a2f3a;
    border-radius: 8px; padding: 6px 14px; font-size: 13px; color: #94a3b8;
}
.user-badge span { color: #3b82f6; font-weight: 600; }
.notif-badge {
    background: #262b36; border: 1px solid #2a2f3a;
    border-radius: 8px; padding: 6px 12px; font-size: 13px; color: #f1f5f9;
}
.notif-dot {
    display: inline-block; background: #ef4444; color: white;
    border-radius: 9999px; font-size: 10px; padding: 1px 6px;
    margin-left: 6px; font-weight: 700;
}
.stat-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 16px; margin-bottom: 28px;
}
.stat-card {
    background: #1e2128; border: 1px solid #2a2f3a;
    border-radius: 12px; padding: 20px 24px;
    position: relative; overflow: hidden;
}
.stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.stat-card.blue::before  { background: #3b82f6; }
.stat-card.green::before { background: #22c55e; }
.stat-card.amber::before { background: #f59e0b; }
.stat-card.red::before   { background: #ef4444; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-value { font-size: 32px; font-weight: 800; color: #f1f5f9; font-family: 'Trebuchet MS', sans-serif; }
.stat-label { font-size: 12px; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.08em; }
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px; padding-bottom: 12px; border-bottom: 1px solid #2a2f3a;
}
.section-header h2 { font-family: 'Trebuchet MS', sans-serif; font-size: 17px; font-weight: 700; color: #f1f5f9; margin: 0; }
.section-icon { background: #262b36; border-radius: 8px; padding: 6px 10px; font-size: 16px; }
.pill { display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.pill-green  { background: rgba(34,197,94,0.15);   color: #22c55e; }
.pill-amber  { background: rgba(245,158,11,0.15);  color: #f59e0b; }
.pill-red    { background: rgba(239,68,68,0.15);   color: #ef4444; }
.pill-blue   { background: rgba(59,130,246,0.15);  color: #3b82f6; }
.pill-gray   { background: rgba(100,116,139,0.15); color: #94a3b8; }
.notif-item {
    background: #262b36; border: 1px solid #2a2f3a; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 8px; font-size: 13px; color: #cbd5e1;
}
.notif-item.unread { border-left: 3px solid #3b82f6; }
.notif-time { font-size: 11px; color: #475569; margin-top: 4px; }
.harvest-stat {
    background: #262b36; border: 1px solid #2a2f3a; border-radius: 8px;
    padding: 10px 16px; margin-top: 8px; font-size: 13px; color: #94a3b8;
}
.harvest-stat span { color: #22c55e; font-weight: 700; font-size: 15px; }
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background-color: #262b36 !important; border-color: #2a2f3a !important;
    color: #f1f5f9 !important; border-radius: 8px !important;
}
.stButton > button { border-radius: 8px !important; font-family: 'Trebuchet MS', sans-serif !important; font-weight: 600 !important; }
.stButton > button[kind="primary"] { background: #3b82f6 !important; border: none !important; }
div[data-testid="stExpander"] { background: #1e2128 !important; border: 1px solid #2a2f3a !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fetch(table, select="*", filters=None, order=None):
    q = supabase.table(table).select(select)
    if filters:
        for k, v in filters.items():
            q = q.eq(k, v)
    if order:
        q = q.order(order)
    return q.execute().data or []

def status_pill(status):
    mapping = {
        "pending":   ("amber", "Pending"),
        "delivered": ("green", "Delivered"),
        "cancelled": ("red",   "Cancelled"),
        "active":    ("red",   "Active"),
        "resolved":  ("green", "Resolved"),
        "ignored":   ("gray",  "Ignored"),
    }
    cls, label = mapping.get(status, ("gray", status))
    return f'<span class="pill pill-{cls}">{label}</span>'

# ─── TOP BAR ─────────────────────────────────────────────────────────────────
unread_notifs = fetch("notifications", filters={"admin_id": user["user_id"], "is_read": False})
unread_count  = len(unread_notifs)

col_bar, col_logout = st.columns([10, 1])
with col_bar:
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-left">
            <div class="logo-box">🌱</div>
            <div>
                <div class="topbar-title">AgroNex</div>
                <div class="topbar-sub">Smart Farming Management System</div>
            </div>
        </div>
        <div class="topbar-right">
            <div class="user-badge">Logged in as <span>{user['full_name']}</span> · Admin</div>
            <div class="notif-badge">🔔 Notifications
                {'<span class="notif-dot">' + str(unread_count) + '</span>' if unread_count > 0 else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_logout:
    st.write("")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# ─── STAT CARDS ──────────────────────────────────────────────────────────────
users_data  = fetch("users")
farms_data  = fetch("farms")
orders_data = fetch("orders")

total_users  = len(users_data)
total_farms  = len(farms_data)
total_orders = len(orders_data)

# ── FUNCTION: get_active_alerts_count() ──────────────────────────────────────
# Calls the PL/SQL function to count active alerts instead of fetching all rows
total_active_alerts = supabase.rpc("get_active_alerts_count").execute().data or 0

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card blue">
        <div class="stat-icon">👥</div>
        <div class="stat-value">{total_users}</div>
        <div class="stat-label">Total Users</div>
    </div>
    <div class="stat-card green">
        <div class="stat-icon">🌾</div>
        <div class="stat-value">{total_farms}</div>
        <div class="stat-label">Total Farms</div>
    </div>
    <div class="stat-card amber">
        <div class="stat-icon">🛒</div>
        <div class="stat-value">{total_orders}</div>
        <div class="stat-label">Total Orders</div>
    </div>
    <div class="stat-card red">
        <div class="stat-icon">⚠️</div>
        <div class="stat-value">{total_active_alerts}</div>
        <div class="stat-label">Active Alerts</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔔 Notifications",
    "👥 User Management",
    "🌾 Farm Overview",
    "🛒 Orders",
    "⚠️ Alerts",
    "📊 Reports",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
# Notifications are auto-populated by these triggers:
#   - trg_notify_harvest   → fires after INSERT on harvests
#   - trg_notify_order     → fires after INSERT on orders
#   - trg_notify_new_user  → fires after INSERT on users
#   - trg_notify_new_farm  → fires after INSERT on farms
#   - trg_notify_new_crop  → fires after INSERT on crops
#   - trg_notify_new_alert → fires after INSERT on alerts
with tab1:
    st.markdown('<div class="section-header"><div class="section-icon">🔔</div><h2>Notifications</h2></div>', unsafe_allow_html=True)

    all_notifs = supabase.table("notifications")\
        .select("*")\
        .eq("admin_id", user["user_id"])\
        .order("created_at", desc=True)\
        .execute().data or []

    col_mark, col_filt = st.columns([3, 1])
    with col_mark:
        if unread_count > 0:
            if st.button(f"✅ Mark all {unread_count} as read"):
                supabase.table("notifications")\
                    .update({"is_read": True})\
                    .eq("admin_id", user["user_id"])\
                    .eq("is_read", False)\
                    .execute()
                st.rerun()
    with col_filt:
        show_filter = st.selectbox("Show", ["All", "Unread", "Read"], key="notif_filter")

    if not all_notifs:
        st.info("No notifications yet.")
    else:
        for n in all_notifs:
            if show_filter == "Unread" and n["is_read"]:
                continue
            if show_filter == "Read" and not n["is_read"]:
                continue
            unread_cls = "" if n["is_read"] else " unread"
            created = n.get("created_at", "")[:16].replace("T", " ")
            st.markdown(f"""
            <div class="notif-item{unread_cls}">
                {n['message']}
                <div class="notif-time">📅 {created} {'· <b style="color:#3b82f6">Unread</b>' if not n['is_read'] else '· Read'}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — USER MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
# Uses QUERY 1: All users with role info (ORDER BY role, full_name)
with tab2:
    st.markdown('<div class="section-header"><div class="section-icon">👥</div><h2>User Management</h2></div>', unsafe_allow_html=True)

    with st.expander("➕ Add New User"):
        with st.form("add_user_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_name  = st.text_input("Full Name")
                new_email = st.text_input("Email")
            with c2:
                new_role = st.selectbox("Role", ["admin", "farmer", "technical_staff", "customer"])
                new_pass = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Create User →", type="primary")
            if submitted:
                if not all([new_name, new_email, new_pass]):
                    st.error("All fields are required.")
                else:
                    try:
                        supabase.table("users").insert({
                            "full_name":     new_name,
                            "email":         new_email,
                            "password_hash": new_pass,
                            "role":          new_role,
                        }).execute()
                        # TRIGGER: trg_notify_new_user fires automatically on INSERT
                        st.success(f"✅ User '{new_name}' created.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # QUERY 1: All users with role info ordered by role then full_name
    users_all = supabase.table("users").select("*").order("role").execute().data or []

    role_filter = st.selectbox("Filter by Role", ["All", "admin", "farmer", "technical_staff", "customer"], key="user_role_filter")
    if role_filter != "All":
        users_all = [u for u in users_all if u["role"] == role_filter]

    st.write(f"**{len(users_all)} user(s) found**")

    for u in users_all:
        icon = "🟦" if u["role"]=="admin" else "🟩" if u["role"]=="farmer" else "🟨" if u["role"]=="technical_staff" else "⬜"
        with st.expander(f"{icon}  {u['full_name']}  ·  {u['email']}  ·  {u['role']}"):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                edit_name  = st.text_input("Full Name",  value=u["full_name"],  key=f"uname_{u['user_id']}")
                edit_email = st.text_input("Email",      value=u["email"],      key=f"uemail_{u['user_id']}")
            with c2:
                edit_role = st.selectbox("Role", ["admin","farmer","technical_staff","customer"],
                                          index=["admin","farmer","technical_staff","customer"].index(u["role"]),
                                          key=f"urole_{u['user_id']}")
                edit_pass = st.text_input("New Password (leave blank to keep)", type="password", key=f"upass_{u['user_id']}")
            with c3:
                st.write(f"**ID:** {u['user_id']}")
                st.write(f"**Joined:** {u.get('created_at','')[:10]}")

            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 Save Changes", key=f"usave_{u['user_id']}", type="primary"):
                    update_data = {"full_name": edit_name, "email": edit_email, "role": edit_role}
                    if edit_pass:
                        update_data["password_hash"] = edit_pass
                    try:
                        supabase.table("users").update(update_data).eq("user_id", u["user_id"]).execute()
                        st.success("✅ User updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col_del:
                if u["user_id"] != user["user_id"]:
                    if st.button("🗑️ Delete User", key=f"udel_{u['user_id']}"):
                        try:
                            supabase.table("users").delete().eq("user_id", u["user_id"]).execute()
                            st.success("✅ User deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.caption("(You — cannot delete)")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FARM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
# Uses QUERY 2: All farms with owner names and field count
# Uses FUNCTION: get_farm_total_harvest(p_farm_id) — total kg per farm
with tab3:
    st.markdown('<div class="section-header"><div class="section-icon">🌾</div><h2>Farm Overview</h2></div>', unsafe_allow_html=True)

    with st.expander("➕ Add New Farm"):
        farmers = [u for u in fetch("users") if u["role"] == "farmer"]
        farmer_options = {f["full_name"]: f["user_id"] for f in farmers}
        with st.form("add_farm_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_farm_name = st.text_input("Farm Name")
                new_location  = st.text_input("Location")
            with c2:
                new_size  = st.number_input("Size (hectares)", min_value=0.01, step=0.5)
                new_owner = st.selectbox("Owner (Farmer)", list(farmer_options.keys()))
            submitted = st.form_submit_button("Create Farm →", type="primary")
            if submitted:
                if not all([new_farm_name, new_location]):
                    st.error("Farm name and location are required.")
                else:
                    try:
                        supabase.table("farms").insert({
                            "farm_name": new_farm_name,
                            "location":  new_location,
                            "size":      new_size,
                            "owner_id":  farmer_options[new_owner],
                        }).execute()
                        # TRIGGER: trg_notify_new_farm fires automatically on INSERT
                        st.success(f"✅ Farm '{new_farm_name}' created.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # QUERY 2: All farms with owner names and field count
    farms_full = supabase.table("farms")\
        .select("*, owner:users(full_name), fields(field_id)")\
        .order("farm_id")\
        .execute().data or []

    st.write(f"**{len(farms_full)} farm(s) registered**")

    for f in farms_full:
        field_count = len(f.get("fields", []))
        owner_name  = f["owner"]["full_name"] if f.get("owner") else "Unknown"

        # FUNCTION: get_farm_total_harvest(p_farm_id)
        # Calls the PL/SQL function to calculate total harvested kg for this farm
        total_harvest_kg = supabase.rpc("get_farm_total_harvest", {"p_farm_id": f["farm_id"]}).execute().data or 0

        with st.expander(f"🌾  {f['farm_name']}  ·  {f['location']}  ·  {field_count} field(s)  ·  {total_harvest_kg:.0f} kg harvested"):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                edit_fname    = st.text_input("Farm Name", value=f["farm_name"], key=f"fname_{f['farm_id']}")
                edit_location = st.text_input("Location",  value=f["location"],  key=f"floc_{f['farm_id']}")
            with c2:
                edit_size = st.number_input("Size (ha)", value=float(f["size"]), min_value=0.01, step=0.5, key=f"fsize_{f['farm_id']}")
                st.caption(f"👤 Owner: {owner_name}")
            with c3:
                st.write(f"**ID:** {f['farm_id']}")
                st.write(f"**Fields:** {field_count}")

            # Display result from get_farm_total_harvest() function
            st.markdown(f"""
            <div class="harvest-stat">
                🌾 Total Harvest via <code>get_farm_total_harvest({f['farm_id']})</code>: <span>{total_harvest_kg:.0f} kg</span>
            </div>
            """, unsafe_allow_html=True)

            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 Save Changes", key=f"fsave_{f['farm_id']}", type="primary"):
                    try:
                        supabase.table("farms").update({
                            "farm_name": edit_fname,
                            "location":  edit_location,
                            "size":      edit_size,
                        }).eq("farm_id", f["farm_id"]).execute()
                        st.success("✅ Farm updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col_del:
                if st.button("🗑️ Delete Farm", key=f"fdel_{f['farm_id']}"):
                    try:
                        supabase.table("farms").delete().eq("farm_id", f["farm_id"]).execute()
                        st.success("✅ Farm deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

            # Fields sub-table
            fields = supabase.table("fields").select("*").eq("farm_id", f["farm_id"]).execute().data or []
            if fields:
                st.markdown("**Fields:**")
                df = pd.DataFrame([{
                    "ID": fi["field_id"],
                    "Name": fi["field_name"],
                    "Soil Type": fi["soil_type"] or "—",
                    "Area (ha)": fi["area_hectares"],
                } for fi in fields])
                st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ORDERS
# ══════════════════════════════════════════════════════════════════════════════
# Uses QUERY 6: All orders with customer and crop details
# TRIGGER: trg_notify_order fires automatically when customer places an order
with tab4:
    st.markdown('<div class="section-header"><div class="section-icon">🛒</div><h2>Orders Overview</h2></div>', unsafe_allow_html=True)

    # QUERY 6: All orders with customer and item details
    orders_full = supabase.table("orders")\
        .select("*, customer:users(full_name), order_items(order_item_id, quantity_kg, price, harvest_id)")\
        .order("order_date", desc=True)\
        .execute().data or []

    status_filter = st.selectbox("Filter by Status", ["All", "pending", "delivered", "cancelled"], key="order_status_filter")
    filtered_orders = orders_full if status_filter == "All" else [o for o in orders_full if o["status"] == status_filter]

    st.write(f"**{len(filtered_orders)} order(s)**")

    for o in filtered_orders:
        customer_name = o["customer"]["full_name"] if o.get("customer") else "Unknown"
        items       = o.get("order_items", [])
        total_price = sum(i.get("price", 0) for i in items)
        total_kg    = sum(i.get("quantity_kg", 0) for i in items)
        status_icon = "🟡" if o["status"]=="pending" else "🟢" if o["status"]=="delivered" else "🔴"

        with st.expander(f"{status_icon}  Order #{o['order_id']}  ·  {customer_name}  ·  {o['order_date']}  ·  ${total_price:.2f}"):
            c1, c2, c3 = st.columns([2, 2, 2])
            with c1:
                st.write(f"**Customer:** {customer_name}")
                st.write(f"**Order Date:** {o['order_date']}")
            with c2:
                st.write(f"**Total Weight:** {total_kg:.1f} kg")
                st.write(f"**Total Price:** ${total_price:.2f}")
            with c3:
                new_status = st.selectbox(
                    "Update Status",
                    ["pending", "delivered", "cancelled"],
                    index=["pending","delivered","cancelled"].index(o["status"]),
                    key=f"ostatus_{o['order_id']}"
                )
                if st.button("💾 Update", key=f"osave_{o['order_id']}", type="primary"):
                    try:
                        supabase.table("orders").update({"status": new_status}).eq("order_id", o["order_id"]).execute()
                        st.success("✅ Order status updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

            if items:
                st.markdown("**Order Items:**")
                df = pd.DataFrame([{
                    "Item #":     i["order_item_id"],
                    "Harvest ID": i["harvest_id"],
                    "Qty (kg)":   i["quantity_kg"],
                    "Price ($)":  i["price"],
                } for i in items])
                st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ALERTS
# ══════════════════════════════════════════════════════════════════════════════
# Uses VIEW: vw_active_alerts — real-time active alerts only
# Uses FUNCTION: get_active_alerts_count() — total active alert count
# TRIGGER: trg_sensor_alert auto-creates alerts on bad sensor readings
with tab5:
    st.markdown('<div class="section-header"><div class="section-icon">⚠️</div><h2>Alerts Overview</h2></div>', unsafe_allow_html=True)

    alert_status_filter = st.selectbox("Filter by Status", ["All", "active", "resolved", "ignored"], key="alert_filter")

    if alert_status_filter == "active":
        # VIEW: vw_active_alerts — shows only active alerts for real-time monitoring
        alerts_full = supabase.table("vw_active_alerts").select("*").execute().data or []
        st.caption("📡 Fetched via **vw_active_alerts** view")
    else:
        alerts_full = supabase.table("alerts")\
            .select("*, field:fields(field_name, farm_id, farms(farm_name))")\
            .order("created_at", desc=True)\
            .execute().data or []
        if alert_status_filter != "All":
            alerts_full = [a for a in alerts_full if a["alert_status"] == alert_status_filter]

    # FUNCTION: get_active_alerts_count() — total count of active alerts
    active_count = supabase.rpc("get_active_alerts_count").execute().data or 0
    st.write(f"**{len(alerts_full)} alert(s) shown** · 🔴 {active_count} active total (via `get_active_alerts_count()`)")

    if active_count > 0:
        if st.button(f"✅ Resolve all {active_count} active alerts"):
            supabase.table("alerts").update({"alert_status": "resolved"})\
                .eq("alert_status", "active").execute()
            st.success("All active alerts resolved.")
            st.rerun()

    for a in alerts_full:
        field_info = a.get("field") or {}
        farm_info  = field_info.get("farms") or {}
        field_name = field_info.get("field_name", f"Field #{a['field_id']}")
        farm_name  = farm_info.get("farm_name", "Unknown Farm")
        alert_icon = "🔴" if a["alert_status"]=="active" else "🟢" if a["alert_status"]=="resolved" else "⚫"
        created    = a.get("created_at","")[:16].replace("T"," ")

        with st.expander(f"{alert_icon}  {a['alert_type']}  ·  {field_name}  ·  {farm_name}  ·  {created}"):
            c1, c2 = st.columns([3, 2])
            with c1:
                st.write(f"**Alert Type:** {a['alert_type']}")
                st.write(f"**Field:** {field_name} ({farm_name})")
                st.write(f"**Created:** {created}")
                if a.get("reading_id"):
                    st.write(f"**Triggered by Reading ID:** {a['reading_id']}")
                    st.caption("⚡ Auto-created by TRIGGER: trg_sensor_alert")
                else:
                    st.caption("📝 Manual alert")
            with c2:
                new_alert_status = st.selectbox(
                    "Update Status",
                    ["active", "resolved", "ignored"],
                    index=["active","resolved","ignored"].index(a["alert_status"]),
                    key=f"astat_{a['alert_id']}"
                )
                if st.button("💾 Update", key=f"asave_{a['alert_id']}", type="primary"):
                    try:
                        supabase.table("alerts").update({"alert_status": new_alert_status}).eq("alert_id", a["alert_id"]).execute()
                        st.success("✅ Alert updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                if st.button("🗑️ Delete Alert", key=f"adel_{a['alert_id']}"):
                    try:
                        supabase.table("alerts").delete().eq("alert_id", a["alert_id"]).execute()
                        st.success("✅ Alert deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — REPORTS
# ══════════════════════════════════════════════════════════════════════════════
# Uses VIEW: vw_farm_production      — farm production summary
# Uses VIEW: vw_active_alerts        — active alerts for monitoring
# Uses VIEW: vw_irrigation_summary   — water usage per field
# Uses FUNCTION: get_active_alerts_count() — total active count
# Uses QUERY 5: Total harvest per farm ranked by quantity
with tab6:
    st.markdown('<div class="section-header"><div class="section-icon">📊</div><h2>Reports & Analytics</h2></div>', unsafe_allow_html=True)

    report_tab1, report_tab2, report_tab3 = st.tabs([
        "🌾 Farm Production",
        "💧 Irrigation Summary",
        "⚠️ Active Alerts",
    ])

    with report_tab1:
        st.markdown("#### 🌾 Farm Production Summary")
        st.caption("Source: **vw_farm_production** view")

        # VIEW: vw_farm_production — total harvest per farm
        prod_data = supabase.table("vw_farm_production").select("*").execute().data or []
        if prod_data:
            df = pd.DataFrame(prod_data)
            df = df.sort_values("total_harvest", ascending=False).reset_index(drop=True)
            df.index += 1
            df.columns = ["Farm Name", "Total Harvest (kg)"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No production data yet.")

        st.markdown("#### 🏆 Farm Harvest Ranking")
        st.caption("Source: **QUERY 5** — Farms ranked by total harvest quantity")

        # QUERY 5: Total harvest per farm with farmer name ordered by total
        harvest_data = supabase.table("harvests")\
            .select("quantity_kg, crop:crops(field_id, fields(farm_id, farms(farm_name)))")\
            .execute().data or []

        farm_totals = {}
        for h in harvest_data:
            try:
                farm_name = h["crop"]["fields"]["farms"]["farm_name"]
                farm_totals[farm_name] = farm_totals.get(farm_name, 0) + h["quantity_kg"]
            except:
                pass

        if farm_totals:
            rank_df = pd.DataFrame(
                sorted(farm_totals.items(), key=lambda x: x[1], reverse=True),
                columns=["Farm Name", "Total Harvest (kg)"]
            )
            rank_df.insert(0, "Rank 🏆", range(1, len(rank_df) + 1))
            st.dataframe(rank_df, use_container_width=True, hide_index=True)

    with report_tab2:
        st.markdown("#### 💧 Irrigation Usage Per Field")
        st.caption("Source: **vw_irrigation_summary** view")

        # VIEW: vw_irrigation_summary — total water used and sessions per field
        irr_data = supabase.table("vw_irrigation_summary").select("*").execute().data or []
        if irr_data:
            df = pd.DataFrame(irr_data)
            df.columns = ["Field ID", "Total Water Used (L)", "Irrigation Sessions"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No irrigation data yet.")

    with report_tab3:
        st.markdown("#### ⚠️ Active Alerts Summary")
        st.caption("Source: **vw_active_alerts** view + **get_active_alerts_count()** function")

        # FUNCTION: get_active_alerts_count() — returns total active alert count
        count = supabase.rpc("get_active_alerts_count").execute().data or 0
        st.metric("Total Active Alerts", count)

        # VIEW: vw_active_alerts — all currently active alerts
        active_data = supabase.table("vw_active_alerts").select("*").execute().data or []
        if active_data:
            df = pd.DataFrame([{
                "Alert ID":   a["alert_id"],
                "Field ID":   a["field_id"],
                "Type":       a["alert_type"],
                "Status":     a["alert_status"],
                "Created At": a.get("created_at","")[:16].replace("T"," "),
            } for a in active_data])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No active alerts right now!")