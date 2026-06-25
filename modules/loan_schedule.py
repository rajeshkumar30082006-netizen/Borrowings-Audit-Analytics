"""Loan Schedule Verification module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.calculations import compare_schedules, compute_emi
from utils.helpers import BRAND, format_currency, page_header


def _get_schedule() -> pd.DataFrame:
    df = st.session_state.get("repayment_schedule")
    if df is not None:
        return df
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "sample_data" / "repayment_schedule.xlsx"
    if p.exists():
        return pd.read_excel(p)
    return pd.DataFrame()


def render():
    page_header("Loan Schedule Verification", "Verify disbursement, repayment, EMI & outstanding balances")

    schedule = _get_schedule()
    if schedule.empty:
        st.warning("No repayment schedule data. Import or load demo data.")
        return

    status_counts = schedule["Status"].value_counts() if "Status" in schedule.columns else pd.Series()
    cols = st.columns(4)
    statuses = [("Paid", "✅"), ("Overdue", "⚠"), ("Missed", "🔴"), ("Future", "📅")]
    for col, (status, icon) in zip(cols, statuses):
        count = status_counts.get(status, 0)
        with col:
            st.metric(f"{icon} {status}", int(count))

    st.subheader("Repayment Schedule")
    st.dataframe(schedule, use_container_width=True, hide_index=True)

    overdue = schedule[schedule.get("Status", pd.Series()) == "Overdue"] if "Status" in schedule.columns else pd.DataFrame()
    missed = schedule[schedule.get("Status", pd.Series()) == "Missed"] if "Status" in schedule.columns else pd.DataFrame()

    if not overdue.empty or not missed.empty:
        st.error("⚠ Schedule exceptions detected")
        if not overdue.empty:
            st.subheader("Overdue Installments")
            st.dataframe(overdue, hide_index=True)
        if not missed.empty:
            st.subheader("Missed Installments")
            st.dataframe(missed, hide_index=True)

    if "Outstanding" in schedule.columns and "Loan_Number" in schedule.columns:
        fig = px.line(schedule, x="Due_Date", y="Outstanding", color="Loan_Number",
                      markers=True, color_discrete_sequence=[BRAND["navy"], BRAND["blue"], BRAND["sky"]])
        fig.update_layout(title="Outstanding Balance Trend", height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("EMI Verification")
    loans = st.session_state.get("loan_master")
    if loans is not None and not loans.empty:
        for _, loan in loans.head(3).iterrows():
            calc_emi = compute_emi(
                loan.get("Outstanding_Amount", loan.get("Sanctioned_Amount", 0)),
                loan.get("Interest_Rate", 0),
                loan.get("Tenure_Months", 12),
            )
            actual_emi = loan.get("EMI", 0)
            match = "✅ Match" if abs(calc_emi - actual_emi) < 1000 else "❌ Mismatch"
            st.write(f"**{loan.get('Loan_Number')}**: Calculated EMI {format_currency(calc_emi)} vs Actual {format_currency(actual_emi)} {match}")
