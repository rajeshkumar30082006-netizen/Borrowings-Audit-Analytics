"""Analytics dashboards module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.helpers import BRAND, get_merged_loans, page_header


def render():
    page_header("Analytics", "Interactive dashboards with advanced visualizations")

    loans = get_merged_loans()
    if loans.empty:
        st.warning("No data for analytics. Load demo data first.")
        return

    bank_filter = st.multiselect("Filter by Bank", loans["Bank"].unique() if "Bank" in loans.columns else [])
    type_filter = st.multiselect("Filter by Loan Type", loans["Loan_Type"].unique() if "Loan_Type" in loans.columns else [])

    filtered = loans.copy()
    if bank_filter:
        filtered = filtered[filtered["Bank"].isin(bank_filter)]
    if type_filter:
        filtered = filtered[filtered["Loan_Type"].isin(type_filter)]

    tab1, tab2, tab3 = st.tabs(["📊 Portfolio", "📈 Trends", "🗺 Risk Heatmap"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.treemap(filtered, path=["Bank", "Loan_Type"], values="Outstanding_Amount",
                             color="Outstanding_Amount", color_continuous_scale="Blues")
            fig.update_layout(title="Outstanding Treemap", height=400)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.sunburst(filtered, path=["Loan_Type", "Bank"], values="Outstanding_Amount",
                              color_discrete_sequence=[BRAND["navy"], BRAND["blue"], BRAND["sky"]])
            fig.update_layout(title="Loan Hierarchy", height=400)
            st.plotly_chart(fig, use_container_width=True)

        fig = px.bar(filtered, x="Bank", y="Outstanding_Amount", color="Loan_Type", barmode="stack",
                     color_discrete_sequence=[BRAND["navy"], BRAND["blue"], BRAND["sky"]])
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if "DSCR_Actual" in filtered.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=filtered["Loan_Number"], y=filtered["DSCR_Actual"],
                                     mode="lines+markers", name="DSCR", line=dict(color=BRAND["blue"], width=3)))
            fig.add_trace(go.Scatter(x=filtered["Loan_Number"], y=filtered.get("Current_Ratio_Actual", []),
                                     mode="lines+markers", name="Current Ratio", line=dict(color=BRAND["sky"])))
            fig.update_layout(title="Covenant Ratio Trends", height=400)
            st.plotly_chart(fig, use_container_width=True)

        if "Interest_Rate" in filtered.columns:
            fig = px.scatter(filtered, x="Outstanding_Amount", y="Interest_Rate", size="Sanctioned_Amount",
                             color="Risk_Level", hover_data=["Loan_Number", "Bank"],
                             color_discrete_map={"Low": BRAND["success"], "Medium": BRAND["warning"],
                                                 "High": BRAND["danger"], "Critical": BRAND["critical"]})
            fig.update_layout(title="Interest Rate vs Outstanding (Bubble)", height=400)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        metrics = ["DSCR_Actual", "Current_Ratio_Actual", "Interest_Rate"]
        available = [m for m in metrics if m in filtered.columns]
        if available and "Bank" in filtered.columns:
            heatmap_data = filtered.groupby("Bank")[available].mean()
            fig = px.imshow(heatmap_data.T, labels=dict(x="Bank", y="Metric", color="Value"),
                            color_continuous_scale="RdYlGn", aspect="auto")
            fig.update_layout(title="Risk Heatmap by Bank", height=400)
            st.plotly_chart(fig, use_container_width=True)

        if "Tenure_Months" in filtered.columns:
            fig = px.bar(filtered, x="Loan_Number", y="Tenure_Months", color="Outstanding_Amount",
                         title="Loan Maturity Timeline", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

    if "Risk_Level" in filtered.columns:
        risk_counts = filtered["Risk_Level"].value_counts()
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=risk_counts.get("High", 0) + risk_counts.get("Critical", 0),
            title={"text": "High Risk Loans"},
            gauge={"axis": {"range": [0, len(filtered)]}, "bar": {"color": BRAND["danger"]},
                   "steps": [{"range": [0, len(filtered)//3], "color": BRAND["success"]},
                             {"range": [len(filtered)//3, 2*len(filtered)//3], "color": BRAND["warning"]}]},
        ))
        st.plotly_chart(fig, use_container_width=True)
