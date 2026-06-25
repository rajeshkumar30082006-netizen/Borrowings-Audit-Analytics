"""Shared helpers for CAP AI Borrowings Audit App."""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

APP_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = APP_ROOT / "assets"
TEMPLATES_DIR = APP_ROOT / "templates"
SAMPLE_DIR = APP_ROOT / "sample_data"

# CAP AI brand palette
BRAND = {
    "navy": "#1B3A6B",
    "blue": "#2E6DB4",
    "sky": "#7EC8E3",
    "sky_light": "#B8E4F5",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "critical": "#DC2626",
}

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": BRAND["navy"]},
        "colorway": [BRAND["navy"], BRAND["blue"], BRAND["sky"], BRAND["success"], BRAND["warning"], BRAND["danger"]],
    }
}

DEFAULT_USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "auditor": hashlib.sha256("audit@2024".encode()).hexdigest(),
}

SHEET_ALIASES = {
    "loan master": "loan_master",
    "interest schedule": "interest_schedule",
    "repayment schedule": "repayment_schedule",
    "bank statements": "bank_statements",
    "security details": "security_details",
    "roc details": "roc_details",
    "drawdown register": "drawdown_register",
    "utilization register": "utilization_register",
    "covenant details": "covenant_details",
}


def init_session_state() -> None:
    """Initialize application session state."""
    defaults: dict[str, Any] = {
        "authenticated": False,
        "username": "",
        "remember_me": False,
        "theme": "light",
        "current_page": "Dashboard",
        "company_name": "CAP AI",
        "currency": "INR",
        "financial_year": "2024-25",
        "tolerance_pct": 2.0,
        "global_search": "",
        "loan_master": None,
        "interest_schedule": None,
        "repayment_schedule": None,
        "bank_statements": None,
        "security_details": None,
        "roc_details": None,
        "drawdown_register": None,
        "utilization_register": None,
        "covenant_details": None,
        "validation_errors": [],
        "ai_insights": [],
        "risk_scores": None,
        "custom_logo": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_login(username: str, password: str) -> bool:
    users = st.session_state.get("users", DEFAULT_USERS)
    return username in users and users[username] == hash_password(password)


def load_css() -> None:
    css_path = ASSETS_DIR / "styles.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    theme_class = "dark-mode" if st.session_state.get("theme") == "dark" else "light-mode"
    st.markdown(f'<div class="{theme_class}" data-theme="{st.session_state.get("theme", "light")}"></div>', unsafe_allow_html=True)


def get_logo_path() -> Path:
    if st.session_state.get("custom_logo"):
        return Path(st.session_state.custom_logo)
    return ASSETS_DIR / "logo.png"


def format_currency(value: float, currency: str | None = None) -> str:
    currency = currency or st.session_state.get("currency", "INR")
    symbol = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}.get(currency, currency)
    if abs(value) >= 1e7:
        return f"{symbol}{value/1e7:.2f} Cr"
    if abs(value) >= 1e5:
        return f"{symbol}{value/1e5:.2f} L"
    return f"{symbol}{value:,.0f}"


def status_pill(status: str) -> str:
    mapping = {
        "Compliant": "status-compliant",
        "Warning": "status-warning",
        "Breached": "status-breached",
        "Critical": "status-critical",
    }
    css = mapping.get(status, "status-warning")
    return f'<span class="status-pill {css}">{status}</span>'


def risk_badge(level: str) -> str:
    css = f"risk-{level.lower()}"
    return f'<span class="{css}">{level.upper()}</span>'


def kpi_card(label: str, value: str, trend: str = "", trend_dir: str = "up", icon: str = "📊") -> str:
    trend_class = "kpi-trend-up" if trend_dir == "up" else "kpi-trend-down"
    trend_html = f'<div class="{trend_class}">{trend}</div>' if trend else ""
    return f"""
    <div class="kpi-card fade-in">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
        {trend_html}
    </div>
    """


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="page-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_footer() -> None:
    company = st.session_state.get("company_name", "CAP AI")
    st.markdown(
        f'<div class="app-footer">© 2024 {company} · Borrowings & Loan Covenants Audit Analytics · Confidential</div>',
        unsafe_allow_html=True,
    )


def get_merged_loans() -> pd.DataFrame:
    """Return loan master or sample data."""
    if st.session_state.get("loan_master") is not None:
        return st.session_state.loan_master.copy()
    sample = SAMPLE_DIR / "loan_master.xlsx"
    if sample.exists():
        return pd.read_excel(sample)
    return pd.DataFrame()


def dataframe_to_excel(df: pd.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()


def ensure_sample_data() -> None:
    """Generate sample Excel files if missing."""
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
