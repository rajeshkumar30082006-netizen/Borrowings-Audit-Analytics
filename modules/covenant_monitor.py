"""Covenant Monitoring module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.calculations import evaluate_covenant
from utils.helpers import BRAND, page_header, status_pill


def _get_covenants() -> pd.DataFrame:
    df = st.session_state.get("covenant_details")
    if df is not None:
        return df
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "sample_data" / "covenant_details.xlsx"
    if p.exists():
        return pd.read_excel(p)
    return pd.DataFrame()


def render():
    page_header("Covenant Monitoring", "Track DSCR, Current Ratio, Debt Equity & compliance status")

    covenants = _get_covenants()
    if covenants.empty:
        st.warning("No covenant data. Import covenant details or load demo data.")
        return

    summary = covenants.groupby("Status").size().reset_index(name="Count")
    cols = st.columns(3)
    for i, status in enumerate(["Compliant", "Warning", "Breached"]):
        count = summary[summary["Status"] == status]["Count"].sum() if not summary.empty else 0
        with cols[i]:
            st.markdown(status_pill(status) + f" **{int(count)}** covenants", unsafe_allow_html=True)

    st.subheader("Covenant Compliance Matrix")
    st.dataframe(covenants, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Actual vs Sanctioned")
        fig = go.Figure()
        for cov in covenants["Covenant"].unique():
            sub = covenants[covenants["Covenant"] == cov]
            fig.add_trace(go.Bar(name=f"{cov} Actual", x=sub["Loan_Number"], y=sub["Actual"]))
            fig.add_trace(go.Bar(name=f"{cov} Sanctioned", x=sub["Loan_Number"], y=sub["Sanctioned"], opacity=0.5))
        fig.update_layout(barmode="group", height=400, colorway=[BRAND["blue"], BRAND["sky"]])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Status Distribution")
        fig = px.pie(summary, names="Status", values="Count", color="Status",
                     color_discrete_map={"Compliant": BRAND["success"], "Warning": BRAND["warning"], "Breached": BRAND["danger"]},
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Covenant Calculator")
    with st.expander("Evaluate Custom Covenant", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            actual = st.number_input("Actual Value", value=1.35, step=0.01)
        with c2:
            sanctioned = st.number_input("Sanctioned Threshold", value=1.25, step=0.01)
        with c3:
            higher = st.checkbox("Higher is Better", value=True)
        status = evaluate_covenant(actual, sanctioned, higher)
        st.markdown(f"Status: {status_pill(status)}", unsafe_allow_html=True)

    breached = covenants[covenants["Status"] == "Breached"]
    if not breached.empty:
        st.error(f"⚠ {len(breached)} covenant breach(es) require immediate attention")
        st.dataframe(breached, hide_index=True)
