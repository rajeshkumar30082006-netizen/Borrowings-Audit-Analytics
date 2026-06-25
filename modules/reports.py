"""Reports generation module."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.calculations import generate_ai_insights
from utils.exporters import build_exception_report, build_executive_report, export_csv, export_excel, export_pdf_report, export_word_report
from utils.helpers import format_currency, get_merged_loans, get_logo_path, page_header
from utils.validators import run_all_validations


REPORT_TYPES = [
    "Executive Report",
    "Detailed Audit Report",
    "Exception Report",
    "Risk Report",
    "Interest Verification Report",
    "Loan Covenant Report",
    "ROC Compliance Report",
    "Security Report",
    "End-use Report",
]


def render():
    page_header("Reports", "Generate and export audit reports in multiple formats")

    report_type = st.selectbox("Report Type", REPORT_TYPES)
    format_choice = st.multiselect("Export Format", ["PDF", "Excel", "Word", "CSV"], default=["PDF"])

    loans = get_merged_loans()
    company = st.session_state.get("company_name", "CAP AI")
    errors = st.session_state.get("validation_errors") or run_all_validations(st.session_state)
    insights = st.session_state.get("ai_insights") or generate_ai_insights(loans)

    kpis = {
        "Total Loans": len(loans),
        "Outstanding": format_currency(loans["Outstanding_Amount"].sum()) if not loans.empty else "₹0",
        "Exceptions": len(errors),
        "Insights": len(insights),
    }

    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            sections = [{"title": report_type, "text": f"Audit report for {company} — FY {st.session_state.get('financial_year', '2024-25')}"}]

            if report_type == "Executive Report":
                sections.append({"title": "Loan Portfolio", "dataframe": loans})
                if insights:
                    sections.append({"title": "AI Insights", "dataframe": pd.DataFrame(insights)})
            elif report_type == "Exception Report":
                sections.append({"title": "Exceptions", "dataframe": pd.DataFrame(errors) if errors else pd.DataFrame()})
            elif report_type == "Interest Verification Report":
                df = st.session_state.get("interest_schedule")
                if df is not None:
                    sections.append({"title": "Interest Reconciliation", "dataframe": df})
            elif report_type == "Loan Covenant Report":
                df = st.session_state.get("covenant_details")
                if df is not None:
                    sections.append({"title": "Covenant Status", "dataframe": df})
            elif report_type == "ROC Compliance Report":
                df = st.session_state.get("roc_details")
                if df is not None:
                    sections.append({"title": "ROC Filings", "dataframe": df})
            elif report_type == "Security Report":
                df = st.session_state.get("security_details")
                if df is not None:
                    sections.append({"title": "Security Register", "dataframe": df})
            elif report_type == "End-use Report":
                df = st.session_state.get("utilization_register")
                if df is not None:
                    sections.append({"title": "End-use Analysis", "dataframe": df})
            else:
                sections.append({"title": "Loan Data", "dataframe": loans})

            st.success(f"✅ {report_type} generated successfully")

            col1, col2, col3, col4 = st.columns(4)
            safe_name = report_type.lower().replace(" ", "_")

            if "PDF" in format_choice:
                pdf = export_pdf_report(report_type, company, sections, kpis)
                col1.download_button("📄 Download PDF", pdf, f"{safe_name}.pdf", "application/pdf")

            if "Excel" in format_choice:
                dfs = {s["title"][:31]: s["dataframe"] for s in sections if s.get("dataframe") is not None and not s["dataframe"].empty}
                if dfs:
                    xlsx = export_excel(dfs, report_type)
                    col2.download_button("📊 Download Excel", xlsx, f"{safe_name}.xlsx",
                                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            if "Word" in format_choice:
                docx = export_word_report(report_type, company, sections)
                col3.download_button("📝 Download Word", docx, f"{safe_name}.docx",
                                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            if "CSV" in format_choice and not loans.empty:
                col4.download_button("📋 Download CSV", export_csv(loans), f"{safe_name}.csv", "text/csv")

    st.subheader("Report Preview")
    logo = get_logo_path()
    if logo.exists():
        st.image(str(logo), width=100)
    st.markdown(f"**{company}** · {report_type}")
    st.json(kpis)

    st.subheader("AI-Generated Observations")
    if insights:
        for ins in insights:
            st.markdown(
                f'<div class="insight-card"><strong>[{ins.get("Severity", "Info")}] {ins.get("Category")} — {ins.get("Loan")}</strong><br>'
                f'{ins.get("Observation")}<br><em>Recommendation: {ins.get("Recommendation")}</em></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("Generate insights by loading loan data on the dashboard.")
