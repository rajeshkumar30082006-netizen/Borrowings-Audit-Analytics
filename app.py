"""
CAP AI — Borrowings & Loan Covenants Audit Analytics
Enterprise-grade Streamlit application for banking audit engagements.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from streamlit_option_menu import option_menu

from utils.helpers import (
    ASSETS_DIR,
    get_logo_path,
    init_session_state,
    load_css,
    render_footer,
    verify_login,
)
from utils.sample_generator import generate_sample_data

# Page modules
from modules import (
    analytics,
    covenant_monitor,
    dashboard,
    end_use,
    import_data,
    interest_check,
    loan_register,
    loan_schedule,
    reports,
    security_roc,
    settings,
)

st.set_page_config(
    page_title="CAP AI · Borrowings Audit",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

MENU_ITEMS = [
    "Dashboard",
    "Import Data",
    "Loan Register",
    "Covenant Monitoring",
    "Interest Verification",
    "Loan Schedule",
    "Security & ROC",
    "End-use Monitoring",
    "Analytics",
    "Reports",
    "Settings",
]

MENU_ICONS = [
    "house", "cloud-upload", "journal-text", "bar-chart",
    "calculator", "calendar-check", "shield-check", "eye",
    "graph-up", "file-earmark-text", "gear",
]

PAGE_MAP = {
    "Dashboard": dashboard,
    "Import Data": import_data,
    "Loan Register": loan_register,
    "Covenant Monitoring": covenant_monitor,
    "Interest Verification": interest_check,
    "Loan Schedule": loan_schedule,
    "Security & ROC": security_roc,
    "End-use Monitoring": end_use,
    "Analytics": analytics,
    "Reports": reports,
    "Settings": settings,
}


def render_login():
    """Professional glassmorphism login page."""
    load_css()
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #1B3A6B 0%, #2E6DB4 40%, #7EC8E3 100%) !important; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stHeader"] { display: none; }
        .block-container { padding-top: 2rem; max-width: 480px; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo = get_logo_path()
        if logo.exists():
            st.image(str(logo), use_container_width=True)

        st.markdown("""
        <div style="text-align:center; color:white; margin-bottom:2rem;">
            <h1 style="color:white; font-weight:800; margin-bottom:0.25rem;">Welcome Back</h1>
            <p style="color:rgba(255,255,255,0.8);">Borrowings & Loan Covenants Audit Analytics</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            username = st.text_input("Username", placeholder="Enter username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
            remember = st.checkbox("Remember Me")

            col_a, col_b = st.columns(2)
            with col_a:
                login_btn = st.button("Sign In", type="primary", use_container_width=True)
            with col_b:
                st.button("Forgot Password?", use_container_width=True)

            if login_btn:
                if verify_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.remember_me = remember
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown("""
        <div style="text-align:center; color:rgba(255,255,255,0.6); margin-top:2rem; font-size:0.85rem;">
            Demo: admin / admin123 · auditor / audit@2024
        </div>
        """, unsafe_allow_html=True)


def render_sidebar() -> str:
    """Render branded sidebar with navigation."""
    logo = get_logo_path()
    with st.sidebar:
        if logo.exists():
            st.image(str(logo), use_container_width=True)
        st.markdown(f"**{st.session_state.get('company_name', 'CAP AI')}**")
        st.caption(f"FY {st.session_state.get('financial_year', '2024-25')} · {st.session_state.get('username', '')}")

        st.markdown("---")

        search = st.text_input("🔍 Global Search", st.session_state.get("global_search", ""),
                               placeholder="Loan, Bank, ROC...", key="sidebar_search")
        st.session_state.global_search = search

        selected = option_menu(
            menu_title=None,
            options=MENU_ITEMS,
            icons=MENU_ICONS,
            menu_icon="cast",
            default_index=MENU_ITEMS.index(st.session_state.get("current_page", "Dashboard")),
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"color": "#2E6DB4", "font-size": "16px"},
                "nav-link": {
                    "font-size": "14px",
                    "font-weight": "500",
                    "padding": "8px 12px",
                    "border-radius": "10px",
                    "margin": "2px 0",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #1B3A6B, #2E6DB4)",
                    "color": "white",
                    "font-weight": "600",
                },
            },
        )

        st.markdown("---")
        theme_toggle = st.toggle("🌙 Dark Mode", value=st.session_state.get("theme") == "dark")
        if theme_toggle != (st.session_state.get("theme") == "dark"):
            st.session_state.theme = "dark" if theme_toggle else "light"
            st.rerun()

        st.caption("v1.0 · CAP AI Audit Platform")

    return selected


def main():
    init_session_state()
    load_css()

    # Ensure sample data exists
    sample_dir = ROOT / "sample_data"
    if not (sample_dir / "loan_master.xlsx").exists():
        generate_sample_data()

    if not st.session_state.authenticated:
        render_login()
        return

    selected = render_sidebar()
    st.session_state.current_page = selected

    module = PAGE_MAP.get(selected)
    if module:
        module.render()

    render_footer()


if __name__ == "__main__":
    main()
