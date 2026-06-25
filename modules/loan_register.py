"""Loan Register module."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

from utils.helpers import format_currency, get_merged_loans, page_header, status_pill


def render_aggrid(df: pd.DataFrame, key: str = "grid"):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, filterable=True, sortable=True, editable=False)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    if "Risk_Level" in df.columns:
        gb.configure_column("Risk_Level", cellStyle=JsCode("""
            function(params) {
                if (params.value === 'Critical') return {backgroundColor: '#FEE2E2', color: '#991B1B'};
                if (params.value === 'High') return {backgroundColor: '#FEF3C7', color: '#92400E'};
                if (params.value === 'Low') return {backgroundColor: '#D1FAE5', color: '#065F46'};
                return {};
            }
        """))
    grid = AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.SELECTION_CHANGED,
                  theme="streamlit", height=450, key=key, allow_unsafe_jscode=True)
    return grid


def render():
    page_header("Loan Register", "Complete borrowings portfolio with advanced filtering")

    search = st.session_state.get("global_search", "")
    loans = get_merged_loans()

    if search and not loans.empty:
        mask = loans.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
        loans = loans[mask]

    if loans.empty:
        st.warning("No loan data available. Import data or load demo dataset.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        banks = ["All"] + sorted(loans["Bank"].unique().tolist()) if "Bank" in loans.columns else ["All"]
        bank_filter = st.selectbox("Bank", banks)
    with c2:
        types = ["All"] + sorted(loans["Loan_Type"].unique().tolist()) if "Loan_Type" in loans.columns else ["All"]
        type_filter = st.selectbox("Loan Type", types)
    with c3:
        risks = ["All"] + sorted(loans["Risk_Level"].unique().tolist()) if "Risk_Level" in loans.columns else ["All"]
        risk_filter = st.selectbox("Risk Level", risks)
    with c4:
        st.metric("Filtered Loans", len(loans))

    filtered = loans.copy()
    if bank_filter != "All":
        filtered = filtered[filtered["Bank"] == bank_filter]
    if type_filter != "All":
        filtered = filtered[filtered["Loan_Type"] == type_filter]
    if risk_filter != "All":
        filtered = filtered[filtered["Risk_Level"] == risk_filter]

    st.subheader(f"📋 {len(filtered)} Loan Accounts")
    render_aggrid(filtered, "loan_register")

    st.download_button("📥 Export to Excel", filtered.to_csv(index=False).encode(),
                       "loan_register.csv", "text/csv")
