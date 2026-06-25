"""Excel import module with validation and mapping."""

from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from utils.helpers import SHEET_ALIASES, page_header
from utils.validators import detect_duplicates, detect_missing, run_all_validations


SHEET_CONFIG = {
    "loan_master": ["Loan_Number", "Bank", "Sanctioned_Amount", "Interest_Rate"],
    "interest_schedule": ["Loan_Number", "Bank_Interest", "Calculated_Interest"],
    "repayment_schedule": ["Loan_Number", "Installment_No", "Due_Date", "EMI"],
    "bank_statements": ["Date", "Description", "Debit", "Credit"],
    "security_details": ["Loan_Number", "Security_Type", "Charge_Status"],
    "roc_details": ["Loan_Number", "Form_Type", "Filing_Status"],
    "drawdown_register": ["Loan_Number", "Drawdown_Date", "Amount"],
    "utilization_register": ["Loan_Number", "Transaction_Date", "Amount", "End_Use_Flag"],
    "covenant_details": ["Loan_Number", "Covenant", "Actual", "Sanctioned", "Status"],
}


def _map_sheet(name: str) -> str | None:
    key = name.strip().lower()
    return SHEET_ALIASES.get(key)


def _process_file(uploaded_file) -> dict[str, pd.DataFrame]:
    results = {}
    xl = pd.ExcelFile(uploaded_file)
    for sheet in xl.sheet_names:
        mapped = _map_sheet(sheet)
        if mapped:
            df = pd.read_excel(uploaded_file, sheet_name=sheet)
            results[mapped] = df
    return results


def render():
    page_header("Import Data", "Upload Excel files with drag & drop or browse")

    tab1, tab2, tab3 = st.tabs(["📤 Upload Files", "🔍 Preview & Validate", "📥 Download Templates"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload Excel files (.xlsx, .xls)",
            type=["xlsx", "xls"],
            accept_multiple_files=True,
            help="Supported sheets: Loan Master, Interest Schedule, Repayment Schedule, etc.",
        )

        if uploaded_files:
            progress = st.progress(0)
            all_data = {}
            for i, f in enumerate(uploaded_files):
                try:
                    data = _process_file(f)
                    all_data.update(data)
                    st.success(f"✅ {f.name}: {len(data)} sheet(s) mapped")
                except Exception as e:
                    st.error(f"❌ {f.name}: {str(e)}")
                progress.progress((i + 1) / len(uploaded_files))

            if st.button("Import All Data", type="primary"):
                for key, df in all_data.items():
                    st.session_state[key] = df
                errors = run_all_validations(st.session_state, st.session_state.get("tolerance_pct", 2.0))
                st.session_state.validation_errors = errors
                st.toast(f"Imported {len(all_data)} datasets!", icon="✅")
                if errors:
                    st.warning(f"⚠ {len(errors)} validation issues detected. See Validate tab.")
                else:
                    st.success("All validations passed!")
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Load Sample Data")
        if st.button("Load Demo Dataset"):
            from utils.sample_generator import generate_sample_data
            from utils.helpers import SAMPLE_DIR
            generate_sample_data()
            for name in SHEET_CONFIG:
                path = SAMPLE_DIR / f"{name}.xlsx"
                if path.exists():
                    st.session_state[name] = pd.read_excel(path)
            st.session_state.validation_errors = run_all_validations(st.session_state)
            st.success("Demo data loaded successfully!")
            st.rerun()

    with tab2:
        st.subheader("Data Preview")
        selected = st.selectbox("Select dataset", list(SHEET_CONFIG.keys()))
        df = st.session_state.get(selected)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.subheader("Missing Data")
            missing = detect_missing(df)
            if not missing.empty:
                st.dataframe(missing, hide_index=True)
            else:
                st.success("No missing values detected.")
            if "Loan_Number" in df.columns:
                dupes = detect_duplicates(df, "Loan_Number")
                if not dupes.empty:
                    st.warning(f"⚠ {len(dupes)} duplicate loan numbers")
                    st.dataframe(dupes, hide_index=True)
        else:
            st.info("No data imported yet. Upload files or load demo data.")

        st.subheader("Validation Report")
        errors = st.session_state.get("validation_errors", [])
        if errors:
            err_df = pd.DataFrame(errors)
            st.dataframe(err_df, use_container_width=True, hide_index=True)
        else:
            st.success("No validation errors.")

    with tab3:
        st.subheader("Download Excel Templates")
        from utils.exporters import create_excel_template
        from utils.helpers import TEMPLATES_DIR

        for name, cols in SHEET_CONFIG.items():
            tpl = TEMPLATES_DIR / f"{name}_template.xlsx"
            if tpl.exists():
                with open(tpl, "rb") as f:
                    st.download_button(f"📄 {name.replace('_', ' ').title()} Template", f.read(),
                                       file_name=f"{name}_template.xlsx", key=f"tpl_{name}")
            else:
                data = create_excel_template(cols, name)
                st.download_button(f"📄 {name.replace('_', ' ').title()} Template", data,
                                   file_name=f"{name}_template.xlsx", key=f"tpl_{name}")
