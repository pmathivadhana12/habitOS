"""
auth.py — HabitOS Login / Register / Onboarding pages
"""

import streamlit as st
from database import (
    register_user, login_user, seed_default_habits,
    create_household, join_household, get_user_household,
    get_demo_credentials, seed_demo_data
)

AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500&display=swap');

.auth-wrap {
    min-height: 80vh;
    display: flex;
    align-items: center;
    justify-content: center;
}
.auth-logo-big {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 42px;
    color: #e8f0f8;
    letter-spacing: -1px;
    text-align: center;
    line-height: 1;
}
.auth-tagline {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #445566;
    text-align: center;
    margin-top: 6px;
    margin-bottom: 32px;
}
.demo-pill-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,212,255,0.06);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 20px;
    padding: 5px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #00d4ff;
    letter-spacing: 1.5px;
    cursor: pointer;
    text-transform: uppercase;
}
.demo-popup {
    background: #0d1117;
    border: 1px solid #1e2d40;
    border-radius: 14px;
    padding: 20px 24px;
    margin-top: 8px;
    position: relative;
}
.demo-popup::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, #7b2fff);
    border-radius: 14px 14px 0 0;
}
.demo-user-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #1e2d40;
}
.demo-user-row:last-child { border-bottom: none; }
.demo-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: #e8f0f8;
}
.demo-cred {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #445566;
}
.stTabs [data-baseweb="tab-list"] {
    background: #111620 !important;
    border-radius: 10px !important;
    border: 1px solid #1e2d40 !important;
    padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #8899aa !important;
    border-radius: 7px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,rgba(0,212,255,0.15),rgba(123,47,255,0.15)) !important;
    color: #00d4ff !important;
}
.stTextInput input {
    background: #111620 !important;
    border: 1px solid #1e2d40 !important;
    border-radius: 8px !important;
    color: #e8f0f8 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 1px #00d4ff22 !important;
}
.stButton > button {
    background: linear-gradient(135deg,rgba(0,212,255,0.1),rgba(123,47,255,0.1)) !important;
    border: 1px solid #2a4a6b !important;
    color: #00d4ff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,rgba(0,212,255,0.2),rgba(123,47,255,0.2)) !important;
    border-color: #00d4ff !important;
    box-shadow: 0 0 16px rgba(0,212,255,0.15) !important;
}
.invite-box {
    font-family: 'Space Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #00d4ff;
    text-align: center;
    letter-spacing: 6px;
    padding: 16px;
    background: #111620;
    border: 1px solid #1e2d40;
    border-radius: 10px;
    margin: 12px 0;
}
</style>
"""


def show_login_page():
    # If user already set in session (mid-rerun), bail immediately
    if st.session_state.get("user") and st.session_state.get("page") == "app":
        return

    # Seed demo data (fast no-op if already done)
    seed_demo_data()

    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # ── Two-column layout: left = branding, right = form ──
    left, gap, right = st.columns([1.1, 0.15, 1.1])

    # ── LEFT — branding + demo ──────────────────────────────────────────────
    with left:
        st.markdown("<div style='padding-top:60px;'>", unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div class="auth-logo-big">⬡ HabitOS</div>
        <div class="auth-tagline">Health Analytics Platform</div>
        """, unsafe_allow_html=True)

        # Value props
        st.markdown("""
        <div style="margin:32px 0 28px 0;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                <span style="font-size:20px;">📊</span>
                <div>
                    <div style="font-family:Syne;font-weight:700;font-size:14px;color:#e8f0f8;">Track daily habits</div>
                    <div style="font-family:Inter;font-size:12px;color:#445566;">Gym, water, sleep, vitamins & more</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                <span style="font-size:20px;">🏠</span>
                <div>
                    <div style="font-family:Syne;font-weight:700;font-size:14px;color:#e8f0f8;">Household mode</div>
                    <div style="font-family:Inter;font-size:12px;color:#445566;">Compare & compete with family or roommates</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:20px;">🔥</span>
                <div>
                    <div style="font-family:Syne;font-weight:700;font-size:14px;color:#e8f0f8;">Streaks & insights</div>
                    <div style="font-family:Inter;font-size:12px;color:#445566;">See trends, drop-offs and leaderboards</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Divider
        st.markdown("<div style='height:1px;background:#1e2d40;margin:24px 0;'></div>", unsafe_allow_html=True)

        # ── Demo section — subtle ──
        st.markdown("""
        <div style="font-family:Space Mono;font-size:10px;letter-spacing:3px;
                    text-transform:uppercase;color:#445566;margin-bottom:12px;">
        Want to explore first?
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🏠 Household Demo", use_container_width=True, key="demo_hh_btn"):
                st.session_state.show_demo_popup = "household"
        with col_b:
            if st.button("🧍 Individual Demo", use_container_width=True, key="demo_ind_btn"):
                st.session_state.show_demo_popup = "individual"

        # ── Demo popup ──
        popup = st.session_state.get("show_demo_popup")
        if popup:
            st.markdown("""
            <div class="demo-popup">
                <div style="font-family:Syne;font-weight:800;font-size:15px;
                            color:#e8f0f8;margin-bottom:12px;">
                    Try with demo data — no sign up needed
                </div>
            </div>
            """, unsafe_allow_html=True)

            if popup == "household":
                st.info("🏠 **Household Demo** — Ram, Mathi & Guna's 3 weeks of real habit data. Full leaderboard, trends, radar charts.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("▶ Enter as Ram", use_container_width=True, key="demo_ram"):
                        _do_demo_login("ram@demo.habitos", "household")
                with c2:
                    if st.button("▶ Enter as Mathi", use_container_width=True, key="demo_mathi"):
                        _do_demo_login("mathi@demo.habitos", "household")
                if st.button("▶ Enter as Guna", use_container_width=True, key="demo_guna"):
                    _do_demo_login("guna@demo.habitos", "household")
            else:
                st.info("🧍 **Individual Demo** — Mathi's personal dashboard. Habit radar, heatmap, streaks & trend line.")
                if st.button("▶ Explore Mathi's Dashboard", use_container_width=True, key="demo_mathi_ind"):
                    _do_demo_login("mathi@demo.habitos", "individual")

            if st.button("✕ Close", key="close_demo_popup"):
                st.session_state.show_demo_popup = None
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Vertical divider ────────────────────────────────────────────────────
    with gap:
        st.markdown("""
        <div style="display:flex;justify-content:center;padding-top:80px;">
            <div style="width:1px;height:420px;background:linear-gradient(180deg,transparent,#1e2d40 20%,#1e2d40 80%,transparent);"></div>
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT — sign in / create account ───────────────────────────────────
    with right:
        st.markdown("<div style='padding-top:60px;'>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["SIGN IN", "CREATE ACCOUNT"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@email.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("⬡ SIGN IN", use_container_width=True, key="btn_login"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    result = login_user(email, password)
                    if result["ok"]:
                        st.session_state.user = result["user"]
                        st.session_state.page = "onboard_check"
                        st.rerun()
                    else:
                        st.error(result["error"])

            # Subtle demo hint below login
            st.markdown("""
            <div style="margin-top:20px;text-align:center;">
                <span style="font-family:Space Mono;font-size:10px;color:#2a3a4a;">
                    Demo: ram@demo.habitos / demo1234
                </span>
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            name   = st.text_input("Full Name", placeholder="Your name", key="reg_name")
            email2 = st.text_input("Email", placeholder="you@email.com", key="reg_email")
            pass2  = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pass")
            pass3  = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_pass2")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("⬡ CREATE ACCOUNT", use_container_width=True, key="btn_register"):
                if not all([name, email2, pass2, pass3]):
                    st.error("Please fill in all fields.")
                elif len(pass2) < 6:
                    st.error("Password must be at least 6 characters.")
                elif pass2 != pass3:
                    st.error("Passwords don't match.")
                else:
                    result = register_user(name, email2, pass2)
                    if result["ok"]:
                        seed_default_habits(result["user"]["id"])
                        st.session_state.user = result["user"]
                        st.session_state.page = "onboarding"
                        st.rerun()
                    else:
                        st.error(result["error"])

        st.markdown("</div>", unsafe_allow_html=True)


def _do_demo_login(email: str, mode: str):
    """Helper: log in as demo user and route to app. Sets all state atomically."""
    with st.spinner("Loading demo..."):
        result = login_user(email, "demo1234")
        if result["ok"]:
            hh = get_user_household(result["user"]["id"])
            # Set ALL session state at once before rerun to avoid partial renders
            st.session_state.update({
                "user": result["user"],
                "household": hh,
                "mode": mode,
                "page": "app",
                "nav": "🏠 Household Dashboard" if mode == "household" else "🧍 Individual Dashboard",
                "show_demo_popup": None,
            })
        else:
            st.error("Demo login failed. Please refresh and try again.")
            return
    st.rerun()


def show_onboarding_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    user = st.session_state.user

    col = st.columns([1, 2, 1])[1]
    with col:
        first = user['name'].split()[0]
        st.markdown(
            "<div style='background:#0d1117;border:1px solid #1e2d40;border-radius:16px;"
            "padding:32px 36px;position:relative;overflow:hidden;margin-bottom:24px;'>"
            "<div style='position:absolute;top:0;left:0;right:0;height:3px;"
            "background:linear-gradient(90deg,#00d4ff,#7b2fff);'></div>"
            "<div style='font-family:Syne,sans-serif;font-weight:800;font-size:28px;"
            "color:#e8f0f8;'>👋 Welcome, " + first + "!</div>"
            "<div style='font-family:Space Mono;font-size:10px;letter-spacing:3px;"
            "text-transform:uppercase;color:#445566;margin-top:6px;'>Set up your space</div>"
            "</div>",
            unsafe_allow_html=True
        )

        choice = st.radio(
            "How do you want to track?",
            ["🧍 Solo — just me", "🏠 Create a household", "🔗 Join a household"],
            key="onboard_choice"
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if "Solo" in choice:
            if st.button("⬡ GET STARTED", use_container_width=True):
                st.session_state.page = "app"
                st.session_state.mode = "individual"
                st.rerun()

        elif "Create" in choice:
            hh_name = st.text_input("Household name", placeholder="e.g. The Dream Team")
            if st.button("⬡ CREATE HOUSEHOLD", use_container_width=True):
                if not hh_name:
                    st.error("Enter a household name.")
                else:
                    result = create_household(hh_name, user["id"])
                    if result["ok"]:
                        st.session_state.household = result["household"]
                        st.session_state.invite_code = result["household"]["invite_code"]
                        st.session_state.page = "show_invite"
                        st.rerun()
                    else:
                        st.error(result["error"])

        elif "Join" in choice:
            code = st.text_input("Invite code", placeholder="8-character code")
            if st.button("⬡ JOIN HOUSEHOLD", use_container_width=True):
                if not code:
                    st.error("Enter the invite code.")
                else:
                    result = join_household(code, user["id"])
                    if result["ok"]:
                        st.session_state.household = result["household"]
                        st.session_state.page = "app"
                        st.session_state.mode = "household"
                        st.rerun()
                    else:
                        st.error(result["error"])


def show_invite_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    code = st.session_state.get("invite_code", "????????")
    hh = st.session_state.get("household", {})

    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown(
            "<div style='background:#0d1117;border:1px solid #1e2d40;border-radius:16px;"
            "padding:32px 36px;position:relative;overflow:hidden;margin-bottom:24px;'>"
            "<div style='position:absolute;top:0;left:0;right:0;height:3px;"
            "background:linear-gradient(90deg,#00d4ff,#7b2fff);'></div>"
            "<div style='font-family:Syne,sans-serif;font-weight:800;font-size:24px;color:#e8f0f8;'>"
            "🏠 " + hh.get("name","Your Household") + "</div>"
            "<div style='font-family:Space Mono;font-size:10px;letter-spacing:3px;"
            "text-transform:uppercase;color:#445566;margin-top:6px;'>Household created!</div>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='font-family:Space Mono;font-size:10px;color:#445566;"
            "letter-spacing:2px;text-transform:uppercase;text-align:center;margin-bottom:8px;'>"
            "Share this invite code</div>"
            "<div class='invite-box'>" + code + "</div>",
            unsafe_allow_html=True
        )
        st.info("Send this code to your household members. They enter it when signing up under 'Join a household'.")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⬡ GO TO DASHBOARD", use_container_width=True):
            st.session_state.page = "app"
            st.session_state.mode = "household"
            st.rerun()


def check_onboard_or_app():
    user = st.session_state.user
    hh = get_user_household(user["id"])
    if hh:
        st.session_state.household = hh
        st.session_state.mode = "household"
    else:
        st.session_state.mode = "individual"
    st.session_state.page = "app"
    st.rerun()
