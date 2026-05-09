import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# ============================================================
# SUPABASE CONNECTION
# ============================================================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AgroNex — Smart Farming",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# SESSION STATE INIT
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# ============================================================
# AUTHENTICATE FUNCTION
# ============================================================
def authenticate_user(email: str, password: str):
    try:
        response = supabase.table("users") \
            .select("user_id, full_name, email, role, password_hash") \
            .eq("email", email) \
            .execute()

        if response.data and len(response.data) > 0:
            user = response.data[0]
            if user['password_hash'] == password:
                return user
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


    


# ============================================================
# REDIRECT BASED ON ROLE
# ============================================================
def go_to_dashboard(role: str):
    if role == 'admin':
        st.switch_page("pages/admin.py")
    elif role == 'farmer':
        st.switch_page("pages/farmer.py")
    elif role == 'technical_staff':
        st.switch_page("pages/technical.py")
    elif role == 'customer':
        st.switch_page("pages/customer.py")

# ============================================================
# IF ALREADY LOGGED IN REDIRECT
# ============================================================
if st.session_state.logged_in and st.session_state.user:
    go_to_dashboard(st.session_state.user['role'])

# ============================================================
# LOGIN UI
# ============================================================
else:
    # ── Background & global styles ──────────────────────────
    st.markdown("""
        <style>
        /* Background */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(160deg, #1a1d23 0%, #1f2329 50%, #1a1e26 100%);
            min-height: 100vh;
        }
        [data-testid="stHeader"] { background: transparent; }
        #MainMenu, footer { visibility: hidden; }

        /* Top accent bar */
        [data-testid="stAppViewContainer"]::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #1d4ed8, #3b82f6, #60a5fa, #3b82f6, #1d4ed8);
            z-index: 999;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
        <div style="text-align:center; padding: 52px 0 36px;">
            <div style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 72px; height: 72px;
                background: linear-gradient(135deg, #1e3a8a, #1d4ed8);
                border-radius: 18px;
                font-size: 2rem;
                margin-bottom: 18px;
                box-shadow: 0 8px 32px rgba(29,78,216,0.35);
            ">🌱</div>
            <div style="
                font-family: 'Trebuchet MS', sans-serif;
                font-weight: 900;
                font-size: 2.2rem;
                color: #f1f5f9;
                letter-spacing: -0.03em;
                margin-bottom: 6px;
            ">
                Agro<span style="color: #3b82f6;">Nex</span>
            </div>
            <div style="
                font-size: 0.68rem;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.2em;
            ">Next Generation Farm Management</div>
        </div>
    """, unsafe_allow_html=True)

    # ── Login Card ───────────────────────────────────────────
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:

        # Card top border accent
        st.markdown("""
            <div style="
                height: 2px;
                background: linear-gradient(90deg, transparent, #3b82f6, transparent);
                border-radius: 2px;
                margin-bottom: -1px;
            "></div>
            <div style="
                background: #1e2128;
                border: 1px solid #2a2f3a;
                border-top: none;
                border-radius: 0 0 14px 14px;
                padding: 32px 28px 28px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            ">
                <div style="
                    font-size: 1.15rem;
                    font-weight: 700;
                    color: #e2e8f0;
                    margin-bottom: 6px;
                    text-align: center;
                    font-family: 'Trebuchet MS', sans-serif;
                ">Sign in to your account</div>
                <div style="
                    font-size: 0.78rem;
                    color: #64748b;
                    text-align: center;
                    margin-bottom: 24px;
                ">Enter your credentials to access the system</div>
            </div>
        """, unsafe_allow_html=True)

        # Email
        email = st.text_input(
            "📧  Email Address",
            placeholder="you@agronex.cy",
            key="email_input"
        )

        # Password
        password = st.text_input(
            "🔒  Password",
            type="password",
            placeholder="Enter your password",
            key="password_input"
        )

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Style inputs and button
        st.markdown("""
            <style>
            /* Input labels */
            div[data-testid="stTextInput"] label p {
                font-size: 0.72rem !important;
                color: #94a3b8 !important;
                letter-spacing: 0.05em !important;
                font-family: 'Courier New', monospace !important;
            }

            /* Input boxes */
            div[data-testid="stTextInput"] input {
                background-color: #262b36 !important;
                border: 1px solid #2e3441 !important;
                border-radius: 8px !important;
                color: #e2e8f0 !important;
                font-size: 0.88rem !important;
                padding: 10px 14px !important;
                font-family: 'Courier New', monospace !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
            }
            div[data-testid="stTextInput"] input::placeholder {
                color: #3d4452 !important;
            }

            /* Button */
            div[data-testid="stButton"] button {
                background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 12px 20px !important;
                font-size: 0.85rem !important;
                font-weight: 700 !important;
                letter-spacing: 0.08em !important;
                text-transform: uppercase !important;
                width: 100% !important;
                transition: all 0.2s !important;
                font-family: 'Trebuchet MS', sans-serif !important;
            }
            div[data-testid="stButton"] button:hover {
                background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
                box-shadow: 0 6px 24px rgba(59,130,246,0.35) !important;
                transform: translateY(-1px) !important;
            }

            /* Error/success alerts */
            div[data-testid="stAlert"] {
                border-radius: 8px !important;
                font-size: 0.78rem !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Login Button
        login_clicked = st.button("Access System →", use_container_width=True)

        if login_clicked:
            if not email or not password:
                st.error("⚠️ Please fill in both fields.")
            else:
                with st.spinner("Verifying credentials..."):
                    user = authenticate_user(email.strip(), password.strip())

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"✅ Welcome back, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password. Please try again.")

        # Divider
        st.markdown("""
            <div style="
                display: flex; align-items: center; gap: 12px;
                margin: 24px 0 18px;
            ">
                <div style="flex:1; height:1px; background:#2a2f3a;"></div>
                <div style="font-size:0.6rem; color:#374151;
                            text-transform:uppercase; letter-spacing:0.12em;">
                    System Access Levels
                </div>
                <div style="flex:1; height:1px; background:#2a2f3a;"></div>
            </div>
        """, unsafe_allow_html=True)

        # Role badges
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
                <div style="background:#262b36; border:1px solid #2e3441;
                            border-radius:8px; padding:10px; text-align:center;
                            margin-bottom:8px;">
                    <div style="font-size:1.2rem; margin-bottom:4px;">🛠️</div>
                    <div style="font-size:0.62rem; color:#3b82f6;
                                text-transform:uppercase; letter-spacing:0.08em;">Admin</div>
                </div>
                <div style="background:#262b36; border:1px solid #2e3441;
                            border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:1.2rem; margin-bottom:4px;">🚜</div>
                    <div style="font-size:0.62rem; color:#3b82f6;
                                text-transform:uppercase; letter-spacing:0.08em;">Farmer</div>
                </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("""
                <div style="background:#262b36; border:1px solid #2e3441;
                            border-radius:8px; padding:10px; text-align:center;
                            margin-bottom:8px;">
                    <div style="font-size:1.2rem; margin-bottom:4px;">📡</div>
                    <div style="font-size:0.62rem; color:#3b82f6;
                                text-transform:uppercase; letter-spacing:0.08em;">Technical</div>
                </div>
                <div style="background:#262b36; border:1px solid #2e3441;
                            border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:1.2rem; margin-bottom:4px;">🛒</div>
                    <div style="font-size:0.62rem; color:#3b82f6;
                                text-transform:uppercase; letter-spacing:0.08em;">Customer</div>
                </div>
            """, unsafe_allow_html=True)

