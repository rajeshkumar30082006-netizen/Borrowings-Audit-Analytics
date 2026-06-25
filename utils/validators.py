"""Data validation rules for borrowings audit."""

from __future__ import annotations

from datetime import datetime

import pandas as pd


def validate_loan_master(df: pd.DataFrame) -> list[dict]:
    errors = []
    if df.empty:
        errors.append({"Rule": "Empty Dataset", "Severity": "Critical", "Message": "Loan Master is empty"})
        return errors

    required = ["Loan_Number", "Bank", "Sanctioned_Amount", "Interest_Rate", "Loan_Date"]
    for col in required:
        if col not in df.columns:
            alt = col.lower()
            if alt not in df.columns:
                errors.append({"Rule": "Missing Column", "Severity": "Critical", "Message": f"Column '{col}' not found"})

    loan_col = "Loan_Number" if "Loan_Number" in df.columns else "loan_number"
    if loan_col in df.columns:
        if df[loan_col].isna().any():
            errors.append({"Rule": "Missing Loan Number", "Severity": "High", "Message": "Some loans missing loan number"})
        dupes = df[df[loan_col].duplicated(keep=False)]
        if not dupes.empty:
            errors.append({"Rule": "Duplicate Loan", "Severity": "High", "Message": f"{len(dupes)} duplicate loan numbers found"})

    rate_col = next((c for c in ["Interest_Rate", "interest_rate"] if c in df.columns), None)
    if rate_col and df[rate_col].isna().any():
        errors.append({"Rule": "Missing Interest Rate", "Severity": "High", "Message": "Missing interest rate on some loans"})

    amt_col = next((c for c in ["Sanctioned_Amount", "Outstanding_Amount", "sanctioned_amount"] if c in df.columns), None)
    if amt_col is not None:
        neg = df[df[amt_col] < 0]
        if not neg.empty:
            errors.append({"Rule": "Negative Amount", "Severity": "Critical", "Message": f"{len(neg)} records with negative amounts"})

    date_col = next((c for c in ["Loan_Date", "loan_date", "Sanction_Date"] if c in df.columns), None)
    if date_col:
        try:
            dates = pd.to_datetime(df[date_col], errors="coerce")
            future = dates > datetime.now()
            if future.any():
                errors.append({"Rule": "Future Loan Date", "Severity": "Medium", "Message": f"{future.sum()} loans with future dates"})
        except Exception:
            pass

    return errors


def validate_covenants(df: pd.DataFrame, tolerance: float = 0) -> list[dict]:
    errors = []
    if df.empty:
        return errors

    checks = [
        ("DSCR_Actual", "DSCR_Sanctioned", "DSCR Below Threshold", True),
        ("Current_Ratio_Actual", "Current_Ratio_Sanctioned", "Current Ratio Below Threshold", True),
        ("Debt_Equity_Actual", "Debt_Equity_Sanctioned", "Debt Equity Above Threshold", False),
        ("Interest_Coverage_Actual", "Interest_Coverage_Sanctioned", "Interest Coverage Below Threshold", True),
    ]
    for actual, sanctioned, rule, higher_better in checks:
        if actual in df.columns and sanctioned in df.columns:
            for _, row in df.iterrows():
                a, s = row[actual], row[sanctioned]
                if pd.isna(a) or pd.isna(s):
                    continue
                breach = (a < s) if higher_better else (a > s)
                if breach:
                    errors.append({
                        "Rule": rule,
                        "Severity": "High",
                        "Message": f"Loan {row.get('Loan_Number', 'N/A')}: Actual {a} vs Sanctioned {s}",
                        "Loan_Number": row.get("Loan_Number", ""),
                    })
    return errors


def validate_interest(df: pd.DataFrame, tolerance_pct: float = 2.0) -> list[dict]:
    errors = []
    diff_col = next((c for c in ["Interest_Difference", "interest_difference", "Variance"] if c in df.columns), None)
    calc_col = next((c for c in ["Calculated_Interest", "calculated_interest"] if c in df.columns), None)
    if diff_col is None:
        return errors
    for _, row in df.iterrows():
        diff = abs(float(row.get(diff_col, 0) or 0))
        calc = abs(float(row.get(calc_col, 1) or 1))
        pct = (diff / calc * 100) if calc else 0
        if pct > tolerance_pct:
            errors.append({
                "Rule": "Interest Difference > Tolerance",
                "Severity": "High" if pct > tolerance_pct * 2 else "Medium",
                "Message": f"Loan {row.get('Loan_Number', 'N/A')}: Variance {pct:.1f}% exceeds {tolerance_pct}%",
                "Loan_Number": row.get("Loan_Number", ""),
            })
    return errors


def validate_roc(df: pd.DataFrame) -> list[dict]:
    errors = []
    if df.empty:
        errors.append({"Rule": "Missing ROC", "Severity": "High", "Message": "No ROC details uploaded"})
        return errors

    status_col = next((c for c in ["Filing_Status", "status", "Status"] if c in df.columns), None)
    if status_col:
        pending = df[df[status_col].astype(str).str.lower().isin(["pending", "overdue", "not filed"])]
        for _, row in pending.iterrows():
            errors.append({
                "Rule": "ROC Filing Pending",
                "Severity": "High",
                "Message": f"Loan {row.get('Loan_Number', 'N/A')}: {row.get('Form_Type', 'CHG')} filing pending",
                "Loan_Number": row.get("Loan_Number", ""),
            })

    expiry_col = next((c for c in ["Charge_Expiry", "expiry_date"] if c in df.columns), None)
    if expiry_col:
        try:
            expiry = pd.to_datetime(df[expiry_col], errors="coerce")
            expired = expiry < datetime.now()
            for idx in df[expired].index:
                errors.append({
                    "Rule": "Expired Security",
                    "Severity": "Critical",
                    "Message": f"Loan {df.loc[idx].get('Loan_Number', 'N/A')}: Charge expired",
                    "Loan_Number": df.loc[idx].get("Loan_Number", ""),
                })
        except Exception:
            pass
    return errors


def validate_security(df: pd.DataFrame) -> list[dict]:
    errors = []
    if df.empty:
        errors.append({"Rule": "Missing Charge", "Severity": "High", "Message": "No security details uploaded"})
        return errors

    charge_col = next((c for c in ["Charge_Status", "charge_status", "Status"] if c in df.columns), None)
    if charge_col:
        missing = df[df[charge_col].astype(str).str.lower().isin(["not created", "missing", "pending"])]
        for _, row in missing.iterrows():
            errors.append({
                "Rule": "Missing Charge",
                "Severity": "High",
                "Message": f"Loan {row.get('Loan_Number', 'N/A')}: Charge not created",
                "Loan_Number": row.get("Loan_Number", ""),
            })
    return errors


def run_all_validations(session_state: dict, tolerance_pct: float = 2.0) -> list[dict]:
    """Run all validation rules against session data."""
    all_errors = []
    if session_state.get("loan_master") is not None:
        all_errors.extend(validate_loan_master(session_state["loan_master"]))
    if session_state.get("covenant_details") is not None:
        all_errors.extend(validate_covenants(session_state["covenant_details"]))
    if session_state.get("interest_schedule") is not None:
        all_errors.extend(validate_interest(session_state["interest_schedule"], tolerance_pct))
    if session_state.get("roc_details") is not None:
        all_errors.extend(validate_roc(session_state["roc_details"]))
    if session_state.get("security_details") is not None:
        all_errors.extend(validate_security(session_state["security_details"]))
    return all_errors


def detect_duplicates(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    if key_col not in df.columns:
        return pd.DataFrame()
    return df[df[key_col].duplicated(keep=False)].copy()


def detect_missing(df: pd.DataFrame) -> pd.DataFrame:
    missing_counts = df.isna().sum()
    missing_counts = missing_counts[missing_counts > 0]
    return pd.DataFrame({"Column": missing_counts.index, "Missing_Count": missing_counts.values})
