"""Executive Dashboard module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.calculations import compute_risk_score, generate_ai_insights
from utils.helpers import BRAND, format_currency, get_merged_loans, kpi_card, page_header, risk_badge, status_pill


def _load_data():
    loans = get_merged_loans()
    if loans.empty:
        from utils.sample_generator import generate_sample_data
        generate_sample_data()
        loans = get_merged_loans()
    return loans


def render():
    page_header("Executive Dashboard", "Real-time borrowings & covenant audit overview")
    loans = _load_data()

    total_loans = len(loans)
    outstanding = loans["Outstanding_Amount"].sum() if "Outstanding_Amount" in loans.columns else 0
    interest_payable = loans.get("Interest_Difference", pd.Series([0])).abs().sum()
    interest_diff = loans.get("Interest_Difference", pd.Series([0])).sum()

    covenants = st.session_state.get("covenant_details")
    if covenants is None:
        try:
            from pathlib import Path
            p = Path(__file__).resolve().parent.parent / "sample_data" / "covenant_details.xlsx"
            if p.exists():
                covenants = pd.read_excel(p)
        except Exception:
            covenants = pd.DataFrame()
    breached = len(covenants[covenants["Status"] == "Breached"]) if covenants is not None and not covenants.empty else 0

    roc = st.session_state.get("roc_details")
    if roc is None:
        try:
            from pathlib import Path
            p = Path(__file__).resolve().parent.parent / "sample_data" / "roc_details.xlsx"
            if p.exists():
                roc = pd.read_excel(p)
        except Exception:
            roc = pd.DataFrame()
    roc_pending = len(roc[roc["Filing_Status"].isin(["Pending", "Overdue"])]) if roc is not None and not roc.empty else 0

    high_risk = len(loans[loans.get("Risk_Level", pd.Series()).isin(["High", "Critical"])]) if "Risk_Level" in loans.columns else 0

    cols = st.columns(4)
    kpis = [
        ("Total Loans", str(total_loans), "↑ 2 new", "up", "🏦"),
        ("Outstanding Amount", format_currency(outstanding), "↑ 3.2%", "up", "💰"),
        ("Interest Payable", format_currency(interest_payable), "", "up", "📊"),
        ("Interest Difference", format_currency(abs(interest_diff)), "⚠ Review", "down", "⚡"),
    ]
    for col, (label, val, trend, td, icon) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(label, val, trend, td, icon), unsafe_allow_html=True)

    cols2 = st.columns(4)
    kpis2 = [
        ("Covenants Breached", str(breached), "🔴 Action", "down", "🚨"),
        ("ROC Pending", str(roc_pending), "⚠ Filing", "down", "📋"),
        ("Loan Accounts", str(total_loans), "", "up", "📂"),
        ("High Risk Loans", str(high_risk), "🔴 Critical", "down", "🛡"),
    ]
    for col, (label, val, trend, td, icon) in zip(cols2, kpis2):
        with col:
            st.markdown(kpi_card(label, val, trend, td, icon), unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Outstanding by Bank")
        if "Bank" in loans.columns:
            bank_data = loans.groupby("Bank")["Outstanding_Amount"].sum().reset_index()
            fig = px.bar(bank_data, x="Bank", y="Outstanding_Amount", color="Bank",
                         color_discrete_sequence=[BRAND["navy"], BRAND["blue"], BRAND["sky"]])
            fig.update_layout(showlegend=False, margin=dict(t=20, b=20), height=350)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Loan Distribution")
        if "Loan_Type" in loans.columns:
            fig = px.pie(loans, names="Loan_Type", values="Outstanding_Amount", hole=0.45,
                         color_discrete_sequence=[BRAND["navy"], BRAND["blue"], BRAND["sky"], BRAND["success"]])
            fig.update_layout(margin=dict(t=20, b=20), height=350)
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("DSCR Trend")
        if "DSCR_Actual" in loans.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=loans["Loan_Number"], y=loans["DSCR_Actual"], mode="lines+markers",
                                     name="Actual", line=dict(color=BRAND["blue"], width=3)))
            if "DSCR_Sanctioned" in loans.columns:
                fig.add_trace(go.Scatter(x=loans["Loan_Number"], y=loans["DSCR_Sanctioned"], mode="lines",
                                         name="Threshold", line=dict(color=BRAND["danger"], dash="dash")))
            fig.update_layout(height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Risk Distribution")
        if "Risk_Level" in loans.columns:
            risk_counts = loans["Risk_Level"].value_counts().reset_index()
            risk_counts.columns = ["Risk", "Count"]
            colors_map = {"Low": BRAND["success"], "Medium": BRAND["warning"], "High": BRAND["danger"], "Critical": BRAND["critical"]}
            fig = px.bar(risk_counts, x="Risk", y="Count", color="Risk", color_discrete_map=colors_map)
            fig.update_layout(showlegend=False, height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚨 Recent Alerts")
    insights = generate_ai_insights(loans, covenants, roc)
    st.session_state.ai_insights = insights
    if insights:
        for ins in insights[:5]:
            sev = ins.get("Severity", "Medium")
            css = "alert-card" if sev in ("High", "Critical") else "alert-card warning"
            st.markdown(
                f'<div class="{css}"><strong>{ins["Category"]} · {ins["Loan"]}</strong><br>{ins["Observation"]}<br>'
                f'<em>→ {ins["Recommendation"]}</em></div>',
                unsafe_allow_html=True,
            )
    else:
        st.success("No critical alerts at this time.")

    st.subheader("Portfolio Overview")
    display_cols = [c for c in ["Loan_Number", "Bank", "Loan_Type", "Outstanding_Amount", "Risk_Level", "DSCR_Actual"] if c in loans.columns]
    st.dataframe(loans[display_cols], use_container_width=True, hide_index=True)
