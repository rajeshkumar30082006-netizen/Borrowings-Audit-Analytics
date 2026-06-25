"""Interest Verification module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.calculations import compute_emi, compute_interest, verify_interest_variance
from utils.helpers import BRAND, format_currency, get_merged_loans, page_header, status_pill


def _get_interest_data() -> pd.DataFrame:
    df = st.session_state.get("interest_schedule")
    if df is not None:
        return df
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "sample_data" / "interest_schedule.xlsx"
    if p.exists():
        return pd.read_excel(p)
    return pd.DataFrame()


def render():
    page_header("Interest Verification", "Recompute interest and reconcile with bank charges")

    tab1, tab2, tab3 = st.tabs(["📊 Reconciliation", "🧮 Calculator", "📈 Trend Analysis"])

    with tab1:
        interest_df = _get_interest_data()
        if interest_df.empty:
            st.warning("No interest schedule data available.")
        else:
            tolerance = st.session_state.get("tolerance_pct", 2.0)
            results = []
            for _, row in interest_df.iterrows():
                r = verify_interest_variance(
                    row.get("Bank_Interest", 0),
                    row.get("Calculated_Interest", 0),
                    tolerance,
                )
                r["Loan_Number"] = row.get("Loan_Number", "")
                results.append(r)
            recon = pd.DataFrame(results)

            for _, row in recon.iterrows():
                css = {"Compliant": "status-compliant", "Warning": "status-warning", "Breached": "status-breached"}.get(row["Status"], "")
                st.markdown(
                    f'<div class="glass-card"><strong>{row["Loan_Number"]}</strong> · '
                    f'{status_pill(row["Status"])} · {row["Charge_Type"]}<br>'
                    f'Bank: {format_currency(row["Bank_Interest"])} | Calc: {format_currency(row["Calculated_Interest"])} | '
                    f'Diff: {format_currency(abs(row["Difference"]))} ({row["Variance_Pct"]:.1f}%)</div>',
                    unsafe_allow_html=True,
                )

            st.subheader("Reconciliation Table")
            st.dataframe(recon, use_container_width=True, hide_index=True)

            over = recon[recon["Charge_Type"] == "Overcharge"]
            under = recon[recon["Charge_Type"] == "Undercharge"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Overcharges", len(over))
            c2.metric("Undercharges", len(under))
            c3.metric("Total Variance", format_currency(recon["Difference"].abs().sum()))

    with tab2:
        st.subheader("Interest Computation Engine")
        c1, c2 = st.columns(2)
        with c1:
            principal = st.number_input("Principal Amount (₹)", value=50000000, step=100000)
            rate = st.number_input("Annual Interest Rate (%)", value=9.75, step=0.05)
            tenure = st.number_input("Tenure (Months)", value=84, step=1)
        with c2:
            compounding = st.selectbox("Compounding", ["monthly", "quarterly", "half-yearly", "yearly"])
            moratorium = st.number_input("Moratorium (Months)", value=0, step=1)

        emi = compute_emi(principal, rate, tenure)
        st.metric("Computed EMI", format_currency(emi))

        schedule = compute_interest(principal, rate, tenure, compounding, moratorium)
        st.dataframe(schedule.head(24), use_container_width=True, hide_index=True)

    with tab3:
        interest_df = _get_interest_data()
        if not interest_df.empty:
            fig = px.bar(interest_df, x="Loan_Number", y=["Bank_Interest", "Calculated_Interest"],
                         barmode="group", color_discrete_sequence=[BRAND["navy"], BRAND["sky"]])
            fig.update_layout(title="Bank vs Calculated Interest", height=400)
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.scatter(interest_df, x="Calculated_Interest", y="Bank_Interest",
                              text="Loan_Number", color="Interest_Difference",
                              color_continuous_scale=["green", "yellow", "red"])
            fig2.add_shape(type="line", x0=0, y0=0, x1=interest_df["Calculated_Interest"].max(),
                           y1=interest_df["Calculated_Interest"].max(), line=dict(dash="dash"))
            st.plotly_chart(fig2, use_container_width=True)
