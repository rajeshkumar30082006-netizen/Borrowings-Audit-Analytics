"""End-use Monitoring module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.calculations import compute_risk_score
from utils.helpers import BRAND, format_currency, page_header, risk_badge


def _load_utilization() -> pd.DataFrame:
    df = st.session_state.get("utilization_register")
    if df is not None:
        return df
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "sample_data" / "utilization_register.xlsx"
    if p.exists():
        return pd.read_excel(p)
    return pd.DataFrame()


def render():
    page_header("End-use Monitoring", "Verify loan utilization against sanctioned purpose")

    util = _load_utilization()
    if util.empty:
        st.warning("No utilization data. Import or load demo data.")
        return

    flags = util["End_Use_Flag"].value_counts() if "End_Use_Flag" in util.columns else pd.Series()
    cols = st.columns(4)
    for col, flag in zip(cols, ["Compliant", "Diversion", "Suspicious", "Round Amount"]):
        with col:
            st.metric(flag, int(flags.get(flag, 0)))

    st.subheader("Utilization Register")
    st.dataframe(util, use_container_width=True, hide_index=True)

    diversions = util[util.get("End_Use_Flag", pd.Series()).isin(["Diversion", "Suspicious"])]
    if not diversions.empty:
        st.error(f"🚨 {len(diversions)} end-use deviation(s) detected")
        for _, row in diversions.iterrows():
            st.markdown(
                f'<div class="alert-card"><strong>{row.get("Loan_Number")}</strong> · '
                f'{format_currency(row.get("Amount", 0))} → {row.get("Vendor", "N/A")}<br>'
                f'Flag: {row.get("End_Use_Flag")} · Purpose: {row.get("Purpose_Mapped")}</div>',
                unsafe_allow_html=True,
            )

    st.subheader("Risk Scoring")
    risk_rows = []
    for loan in util["Loan_Number"].unique():
        loan_util = util[util["Loan_Number"] == loan]
        factors = {
            "end_use_deviation": any(loan_util["End_Use_Flag"].isin(["Diversion", "Suspicious"])),
            "interest_mismatch": False,
            "covenant_breach": False,
            "roc_pending": False,
            "security_missing": False,
            "delayed_repayment": False,
            "expired_charge": False,
        }
        level, score = compute_risk_score(factors)
        risk_rows.append({"Loan_Number": loan, "Risk_Level": level, "Risk_Score": score})

    risk_df = pd.DataFrame(risk_rows)
    st.dataframe(risk_df, hide_index=True)

    if "Amount" in util.columns:
        fig = px.scatter(util, x="Transaction_Date", y="Amount", color="End_Use_Flag", size="Amount",
                         hover_data=["Loan_Number", "Vendor"], color_discrete_sequence=[BRAND["success"], BRAND["warning"], BRAND["danger"]])
        fig.update_layout(title="Utilization Pattern Analysis", height=400)
        st.plotly_chart(fig, use_container_width=True)
