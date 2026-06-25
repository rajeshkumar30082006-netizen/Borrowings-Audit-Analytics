"""Security & ROC Compliance module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.helpers import BRAND, page_header, status_pill


def _load(name: str) -> pd.DataFrame:
    df = st.session_state.get(name)
    if df is not None:
        return df
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "sample_data" / f"{name}.xlsx"
    if p.exists():
        return pd.read_excel(p)
    return pd.DataFrame()


def render():
    page_header("Security & ROC Compliance", "Verify charges, collateral, CHG forms & ROC filings")

    tab1, tab2, tab3 = st.tabs(["🛡 Security Register", "📋 ROC Filings", "🚨 Exception Report"])

    with tab1:
        security = _load("security_details")
        if security.empty:
            st.warning("No security data available.")
        else:
            st.dataframe(security, use_container_width=True, hide_index=True)
            if "Security_Value" in security.columns:
                fig = px.treemap(security, path=["Security_Type", "Loan_Number"], values="Security_Value",
                                 color_discrete_sequence=[BRAND["navy"], BRAND["blue"], BRAND["sky"]])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            pending = security[security.get("Charge_Status", pd.Series()).isin(["Pending", "Not Created", "Missing"])]
            if not pending.empty:
                st.error(f"⚠ {len(pending)} charge(s) not created")

    with tab2:
        roc = _load("roc_details")
        if roc.empty:
            st.warning("No ROC data available.")
        else:
            st.dataframe(roc, use_container_width=True, hide_index=True)

            forms = ["CHG-1", "CHG-4", "CHG-9"]
            for form in forms:
                form_data = roc[roc.get("Form_Type", pd.Series()) == form]
                if not form_data.empty:
                    filed = len(form_data[form_data["Filing_Status"] == "Filed"])
                    total = len(form_data)
                    st.progress(filed / total if total else 0, text=f"{form}: {filed}/{total} filed")

            pending_roc = roc[roc["Filing_Status"].isin(["Pending", "Overdue"])]
            if not pending_roc.empty:
                st.warning(f"⚠ {len(pending_roc)} ROC filing(s) pending/overdue")
                for _, row in pending_roc.iterrows():
                    st.markdown(
                        f'<div class="alert-card warning"><strong>{row.get("Loan_Number")}</strong> · '
                        f'{row.get("Form_Type")} · Status: {row.get("Filing_Status")}</div>',
                        unsafe_allow_html=True,
                    )

    with tab3:
        security = _load("security_details")
        roc = _load("roc_details")
        exceptions = []

        if not security.empty:
            for _, row in security.iterrows():
                if str(row.get("Charge_Status", "")).lower() in ("pending", "not created", "missing"):
                    exceptions.append({"Type": "Security", "Loan": row.get("Loan_Number"), "Issue": "Charge not created", "Severity": "High"})

        if not roc.empty:
            for _, row in roc.iterrows():
                if str(row.get("Filing_Status", "")).lower() in ("pending", "overdue"):
                    exceptions.append({"Type": "ROC", "Loan": row.get("Loan_Number"), "Issue": f"{row.get('Form_Type')} not filed", "Severity": "High"})

        if exceptions:
            st.dataframe(pd.DataFrame(exceptions), use_container_width=True, hide_index=True)
        else:
            st.success("No security or ROC exceptions.")
