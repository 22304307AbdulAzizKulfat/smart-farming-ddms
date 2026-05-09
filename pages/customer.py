import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import date

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroNex — Customer",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── AUTH GUARD ─────────────────────────────────────────────────────────────
if "user" not in st.session_state or st.session_state.user.get("role") != "customer":
    st.error("🔒 Access denied. Please log in as a Customer.")
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
    border-radius: 10px; padding: 8px 12px; font-size: 22px;
}
.topbar-title { font-family: 'Trebuchet MS', sans-serif; font-size: 20px; font-weight: 700; color: #f1f5f9; }
.topbar-sub { font-size: 12px; color: #64748b; }
.user-badge {
    background: #262b36; border: 1px solid #2a2f3a;
    border-radius: 8px; padding: 6px 14px; font-size: 13px; color: #94a3b8;
}
.user-badge span { color: #3b82f6; font-weight: 600; }
.stat-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
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
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-value { font-size: 32px; font-weight: 800; color: #f1f5f9; font-family: 'Trebuchet MS', sans-serif; }
.stat-label { font-size: 12px; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.08em; }
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px; padding-bottom: 12px; border-bottom: 1px solid #2a2f3a;
}
.section-header h2 { font-family: 'Trebuchet MS', sans-serif; font-size: 17px; font-weight: 700; color: #f1f5f9; margin: 0; }
.section-icon { background: #262b36; border-radius: 8px; padding: 6px 10px; font-size: 16px; }
.harvest-card {
    background: #1e2128; border: 1px solid #2a2f3a;
    border-radius: 12px; padding: 18px 20px; transition: border-color 0.2s;
}
.harvest-card:hover { border-color: #3b82f6; }
.harvest-card-title { font-size: 15px; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; font-family: 'Trebuchet MS', sans-serif; }
.harvest-card-farm { font-size: 12px; color: #64748b; margin-bottom: 12px; }
.harvest-card-info { display: flex; justify-content: space-between; margin-bottom: 12px; }
.harvest-info-item { text-align: center; }
.harvest-info-value { font-size: 16px; font-weight: 700; color: #3b82f6; }
.harvest-info-label { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.pill { display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.pill-green  { background: rgba(34,197,94,0.15);  color: #22c55e; }
.pill-amber  { background: rgba(245,158,11,0.15); color: #f59e0b; }
.pill-red    { background: rgba(239,68,68,0.15);  color: #ef4444; }
.pill-blue   { background: rgba(59,130,246,0.15); color: #3b82f6; }
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
def status_pill(status):
    mapping = {
        "pending":   ("amber", "Pending"),
        "delivered": ("green", "Delivered"),
        "cancelled": ("red",   "Cancelled"),
    }
    cls, label = mapping.get(status, ("blue", status))
    return f'<span class="pill pill-{cls}">{label}</span>'

# ─── TOP BAR ─────────────────────────────────────────────────────────────────
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
        <div>
            <div class="user-badge">Welcome, <span>{user['full_name']}</span> · Customer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.write("")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# ─── STAT CARDS ──────────────────────────────────────────────────────────────
my_orders       = supabase.table("orders").select("*").eq("customer_id", user["user_id"]).execute().data or []
pending_count   = len([o for o in my_orders if o["status"] == "pending"])
delivered_count = len([o for o in my_orders if o["status"] == "delivered"])

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card blue">
        <div class="stat-icon">🛒</div>
        <div class="stat-value">{len(my_orders)}</div>
        <div class="stat-label">Total Orders</div>
    </div>
    <div class="stat-card amber">
        <div class="stat-icon">⏳</div>
        <div class="stat-value">{pending_count}</div>
        <div class="stat-label">Pending Orders</div>
    </div>
    <div class="stat-card green">
        <div class="stat-icon">✅</div>
        <div class="stat-value">{delivered_count}</div>
        <div class="stat-label">Delivered Orders</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🌾 Browse & Order Harvests", "📦 My Orders"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — BROWSE HARVESTS & PLACE ORDER
# ══════════════════════════════════════════════════════════════════════════════
# Uses VIEW: vw_farm_production — customers can see which farms are producing
# PROCEDURE: sp_place_order(p_customer_id) — creates the order record
# TRIGGER: trg_notify_order fires automatically after INSERT on orders
# TRIGGER: trg_crop_update fires automatically after INSERT on harvests (crop → harvested)
with tab1:
    st.markdown('<div class="section-header"><div class="section-icon">🌾</div><h2>Available Harvests</h2></div>', unsafe_allow_html=True)

    # Fetch all harvests with crop, field, farm info
    harvests = supabase.table("harvests")\
        .select("*, crop:crops(crop_name, field_id, fields(field_name, farms(farm_name)))")\
        .order("harvested_at", desc=True)\
        .execute().data or []

    # Search & sort
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Search by crop or farm name", placeholder="e.g. Orange, Georgiou...")
    with col_filter:
        sort_by = st.selectbox("Sort by", ["Newest", "Quantity (High→Low)", "Quantity (Low→High)"])

    if search:
        harvests = [h for h in harvests if
            search.lower() in (h["crop"]["crop_name"] or "").lower() or
            search.lower() in (h["crop"]["fields"]["farms"]["farm_name"] or "").lower()
        ]

    if sort_by == "Quantity (High→Low)":
        harvests = sorted(harvests, key=lambda x: x["quantity_kg"], reverse=True)
    elif sort_by == "Quantity (Low→High)":
        harvests = sorted(harvests, key=lambda x: x["quantity_kg"])

    # VIEW: vw_farm_production — show farm production summary above harvest list
    prod_data = supabase.table("vw_farm_production").select("*").execute().data or []
    if prod_data:
        with st.expander("📊 Farm Production Overview (vw_farm_production)"):
            df = pd.DataFrame(prod_data)
            df.columns = ["Farm Name", "Total Harvest (kg)"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    if not harvests:
        st.info("No harvests available at the moment.")
    else:
        st.write(f"**{len(harvests)} harvest(s) available**")

        for i in range(0, len(harvests), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(harvests):
                    h = harvests[i + j]
                    crop_name    = h["crop"]["crop_name"] if h.get("crop") else "Unknown"
                    field_name   = h["crop"]["fields"]["field_name"] if h["crop"].get("fields") else "Unknown"
                    farm_name    = h["crop"]["fields"]["farms"]["farm_name"] if h["crop"]["fields"].get("farms") else "Unknown"
                    harvested_at = h.get("harvested_at", "")[:10]

                    with col:
                        st.markdown(f"""
                        <div class="harvest-card">
                            <div class="harvest-card-title">🌿 {crop_name}</div>
                            <div class="harvest-card-farm">🏡 {farm_name} · {field_name}</div>
                            <div class="harvest-card-info">
                                <div class="harvest-info-item">
                                    <div class="harvest-info-value">{h['quantity_kg']:.0f}</div>
                                    <div class="harvest-info-label">kg available</div>
                                </div>
                                <div class="harvest-info-item">
                                    <div class="harvest-info-value">{harvested_at}</div>
                                    <div class="harvest-info-label">harvested</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander(f"🛒 Order {crop_name}"):
                            qty = st.number_input(
                                "Quantity (kg)",
                                min_value=0.1,
                                max_value=float(h["quantity_kg"]),
                                value=1.0,
                                step=0.5,
                                key=f"qty_{h['harvest_id']}"
                            )
                            
                            price_per_kg = h.get("price_per_kg") or 0.70
                            total = qty * price_per_kg
                            st.markdown(f"**Price/kg:** ${price_per_kg:.2f} · **Total: ${total:.2f}**")

                            if st.button(f"Place Order →", key=f"order_{h['harvest_id']}", type="primary", use_container_width=True):
                                try:
                                    # PROCEDURE: sp_place_order(p_customer_id)
                                    # Creates the order record via stored procedure
                                    supabase.rpc("sp_place_order", {
                                        "p_customer_id": user["user_id"]
                                    }).execute()
                                    # TRIGGER: trg_notify_order fires automatically on INSERT

                                    # Fetch the newly created order ID
                                    new_order = supabase.table("orders")\
                                        .select("order_id")\
                                        .eq("customer_id", user["user_id"])\
                                        .eq("status", "pending")\
                                        .order("order_id", desc=True)\
                                        .execute().data

                                    if new_order:
                                        new_order_id = new_order[0]["order_id"]
                                        # Add the order item
                                        supabase.table("order_items").insert({
                                            "order_id":    new_order_id,
                                            "harvest_id":  h["harvest_id"],
                                            "quantity_kg": qty,
                                            "price":       round(total, 2),
                                        }).execute()
                                        st.success(f"✅ Order placed! Order #{new_order_id}")
                                        st.rerun()
                                    else:
                                        st.error("Order created but could not retrieve ID.")
                                except Exception as e:
                                    st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MY ORDERS
# ══════════════════════════════════════════════════════════════════════════════
# Uses PROCEDURE: cancel_customer_orders(p_customer_id)
#   → Cancels ALL pending orders for this customer in one call
# Uses QUERY 6: Orders with customer and crop details
with tab2:
    st.markdown('<div class="section-header"><div class="section-icon">📦</div><h2>My Orders</h2></div>', unsafe_allow_html=True)

    # QUERY 6: Orders with customer details and items
    my_orders_full = supabase.table("orders")\
        .select("*, order_items(order_item_id, quantity_kg, price, harvest_id)")\
        .eq("customer_id", user["user_id"])\
        .order("order_date", desc=True)\
        .execute().data or []

    if not my_orders_full:
        st.info("You haven't placed any orders yet. Browse the harvests tab to get started!")
    else:
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "delivered", "cancelled"], key="my_order_filter")
        filtered = my_orders_full if status_filter == "All" else [o for o in my_orders_full if o["status"] == status_filter]

        # PROCEDURE: cancel_customer_orders(p_customer_id)
        # Cancels all pending orders for this customer in a single procedure call
        has_pending = any(o["status"] == "pending" for o in my_orders_full)
        if has_pending:
            if st.button("❌ Cancel ALL my pending orders", type="primary"):
                try:
                    # Calls the stored procedure cancel_customer_orders()
                    supabase.rpc("cancel_customer_orders", {
                        "p_customer_id": user["user_id"]
                    }).execute()
                    st.success("✅ All pending orders cancelled.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        st.write(f"**{len(filtered)} order(s)**")

        for o in filtered:
            items       = o.get("order_items", [])
            total_price = sum(i.get("price", 0) for i in items)
            total_kg    = sum(i.get("quantity_kg", 0) for i in items)
            status_icon = "🟡" if o["status"]=="pending" else "🟢" if o["status"]=="delivered" else "🔴"

            with st.expander(f"{status_icon}  Order #{o['order_id']}  ·  {o['order_date']}  ·  ${total_price:.2f}  ·  {o['status'].upper()}"):
                c1, c2, c3 = st.columns([2, 2, 2])
                with c1:
                    st.write(f"**Order ID:** #{o['order_id']}")
                    st.write(f"**Date:** {o['order_date']}")
                with c2:
                    st.write(f"**Total Weight:** {total_kg:.1f} kg")
                    st.write(f"**Total Price:** ${total_price:.2f}")
                with c3:
                    st.markdown(f"**Status:** {status_pill(o['status'])}", unsafe_allow_html=True)

                    # Cancel single order — raw update (only pending ones)
                    if o["status"] == "pending":
                        if st.button("❌ Cancel this order", key=f"cancel_{o['order_id']}"):
                            try:
                                supabase.table("orders")\
                                    .update({"status": "cancelled"})\
                                    .eq("order_id", o["order_id"])\
                                    .execute()
                                st.success("✅ Order cancelled.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                if items:
                    st.markdown("**Items in this order:**")
                    df = pd.DataFrame([{
                        "Item #":     i["order_item_id"],
                        "Harvest ID": i["harvest_id"],
                        "Qty (kg)":   i["quantity_kg"],
                        "Price ($)":  i["price"],
                    } for i in items])
                    st.dataframe(df, use_container_width=True, hide_index=True)