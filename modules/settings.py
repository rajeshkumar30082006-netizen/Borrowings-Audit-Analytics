"""Settings module."""

from __future__ import annotations

import streamlit as st

from utils.helpers import ASSETS_DIR, DEFAULT_USERS, hash_password, page_header


def render():
    page_header("Settings", "Configure application preferences and security")

    tab1, tab2, tab3 = st.tabs(["🏢 Company", "🎨 Theme", "🔐 Security"])

    with tab1:
        st.subheader("Company Settings")
        company = st.text_input("Company Name", st.session_state.get("company_name", "CAP AI"))
        currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"],
                                index=["INR", "USD", "EUR", "GBP"].index(st.session_state.get("currency", "INR")))
        fy = st.text_input("Financial Year", st.session_state.get("financial_year", "2024-25"))
        tolerance = st.slider("Interest Tolerance (%)", 0.5, 10.0, float(st.session_state.get("tolerance_pct", 2.0)), 0.5)

        uploaded_logo = st.file_uploader("Upload Custom Logo", type=["png", "jpg", "jpeg"])
        if uploaded_logo:
            logo_path = ASSETS_DIR / "custom_logo.png"
            with open(logo_path, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            st.session_state.custom_logo = str(logo_path)
            st.success("Logo uploaded successfully!")

        if st.button("Save Company Settings", type="primary"):
            st.session_state.company_name = company
            st.session_state.currency = currency
            st.session_state.financial_year = fy
            st.session_state.tolerance_pct = tolerance
            st.toast("Settings saved!", icon="✅")

    with tab2:
        st.subheader("Theme Settings")
        theme = st.radio("Mode", ["light", "dark"], index=0 if st.session_state.get("theme") == "light" else 1, horizontal=True)
        if st.button("Apply Theme"):
            st.session_state.theme = theme
            st.rerun()

        st.markdown("#### Brand Colors")
        st.markdown("""
        | Color | Hex | Usage |
        |-------|-----|-------|
        | Navy | `#1B3A6B` | Headers, primary buttons |
        | Blue | `#2E6DB4` | Links, accents |
        | Sky | `#7EC8E3` | Backgrounds, highlights |
        """)

    with tab3:
        st.subheader("Change Password")
        current = st.text_input("Current Password", type="password")
        new_pass = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Update Password"):
            username = st.session_state.get("username", "admin")
            users = st.session_state.get("users", DEFAULT_USERS)
            if users.get(username) != hash_password(current):
                st.error("Current password incorrect.")
            elif new_pass != confirm:
                st.error("Passwords do not match.")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                if "users" not in st.session_state:
                    st.session_state.users = dict(DEFAULT_USERS)
                st.session_state.users[username] = hash_password(new_pass)
                st.success("Password updated successfully!")

        st.subheader("Session")
        st.write(f"Logged in as: **{st.session_state.get('username', 'N/A')}**")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()
