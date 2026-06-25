"""Financial calculations for loan audit analytics."""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd


def compute_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate EMI using reducing balance method."""
    if tenure_months <= 0 or principal <= 0:
        return 0.0
    if annual_rate <= 0:
        return principal / tenure_months
    r = annual_rate / 12 / 100
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def compute_interest(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    compounding: str = "monthly",
    moratorium_months: int = 0,
) -> pd.DataFrame:
    """Generate amortization schedule with interest breakdown."""
    freq_map = {"monthly": 12, "quarterly": 4, "half-yearly": 2, "yearly": 1}
    periods_per_year = freq_map.get(compounding.lower(), 12)
    period_rate = annual_rate / periods_per_year / 100
    total_periods = max(1, int(tenure_months * periods_per_year / 12))

    rows = []
    balance = principal
    emi = compute_emi(principal, annual_rate, tenure_months)

    for period in range(1, total_periods + 1):
        if period <= moratorium_months:
            interest = balance * period_rate
            principal_paid = 0
        else:
            interest = balance * period_rate
            principal_paid = min(emi - interest, balance) if emi > interest else 0
        balance = max(0, balance - principal_paid)
        rows.append({
            "Period": period,
            "Opening_Balance": round(balance + principal_paid, 2),
            "Interest": round(interest, 2),
            "Principal": round(principal_paid, 2),
            "EMI": round(interest + principal_paid, 2),
            "Closing_Balance": round(balance, 2),
        })
    return pd.DataFrame(rows)


def verify_interest_variance(
    bank_interest: float,
    calculated_interest: float,
    tolerance_pct: float = 2.0,
) -> dict:
    diff = bank_interest - calculated_interest
    pct = (abs(diff) / calculated_interest * 100) if calculated_interest else 0
    if pct <= tolerance_pct:
        status = "Compliant"
    elif pct <= tolerance_pct * 2:
        status = "Warning"
    else:
        status = "Breached"
    charge_type = "Overcharge" if diff > 0 else "Undercharge" if diff < 0 else "Matched"
    return {
        "Bank_Interest": bank_interest,
        "Calculated_Interest": calculated_interest,
        "Difference": round(diff, 2),
        "Variance_Pct": round(pct, 2),
        "Status": status,
        "Charge_Type": charge_type,
    }


def compute_dscr(ebitda: float, total_debt_service: float) -> float:
    if total_debt_service <= 0:
        return float("inf")
    return round(ebitda / total_debt_service, 2)


def compute_current_ratio(current_assets: float, current_liabilities: float) -> float:
    if current_liabilities <= 0:
        return float("inf")
    return round(current_assets / current_liabilities, 2)


def compute_debt_equity(total_debt: float, net_worth: float) -> float:
    if net_worth <= 0:
        return float("inf")
    return round(total_debt / net_worth, 2)


def compute_interest_coverage(ebit: float, interest_expense: float) -> float:
    if interest_expense <= 0:
        return float("inf")
    return round(ebit / interest_expense, 2)


def compute_working_capital_ratio(wc: float, total_assets: float) -> float:
    if total_assets <= 0:
        return 0.0
    return round(wc / total_assets * 100, 2)


def evaluate_covenant(actual: float, sanctioned: float, higher_is_better: bool = True) -> str:
    """Evaluate covenant compliance status."""
    if math.isinf(actual) or math.isnan(actual):
        return "Warning"
    if higher_is_better:
        if actual >= sanctioned:
            return "Compliant"
        if actual >= sanctioned * 0.9:
            return "Warning"
        return "Breached"
    else:
        if actual <= sanctioned:
            return "Compliant"
        if actual <= sanctioned * 1.1:
            return "Warning"
        return "Breached"


def compute_risk_score(factors: dict[str, bool]) -> tuple[str, int]:
    """Compute aggregate risk score from boolean risk factors."""
    weights = {
        "interest_mismatch": 20,
        "covenant_breach": 25,
        "roc_pending": 15,
        "security_missing": 20,
        "end_use_deviation": 15,
        "delayed_repayment": 10,
        "expired_charge": 15,
    }
    score = sum(weights.get(k, 10) for k, v in factors.items() if v)
    if score >= 70:
        return "Critical", score
    if score >= 50:
        return "High", score
    if score >= 25:
        return "Medium", score
    return "Low", score


def generate_ai_insights(
    loans: pd.DataFrame,
    covenants: pd.DataFrame | None = None,
    roc: pd.DataFrame | None = None,
) -> list[dict]:
    """Generate audit observations and recommendations."""
    insights = []
    if loans.empty:
        return insights

    for _, row in loans.iterrows():
        loan_no = row.get("Loan_Number", row.get("loan_number", "N/A"))

        dscr = row.get("DSCR_Actual", row.get("dscr", None))
        dscr_thresh = row.get("DSCR_Sanctioned", row.get("dscr_threshold", 1.25))
        if dscr is not None and pd.notna(dscr) and dscr < dscr_thresh:
            insights.append({
                "Loan": loan_no,
                "Category": "Covenant",
                "Severity": "High",
                "Observation": f"DSCR ({dscr:.2f}) below sanctioned threshold ({dscr_thresh}).",
                "Recommendation": "Review cash flow projections and discuss restructuring with lender.",
            })

        cr = row.get("Current_Ratio_Actual", row.get("current_ratio", None))
        cr_thresh = row.get("Current_Ratio_Sanctioned", row.get("cr_threshold", 1.33))
        if cr is not None and pd.notna(cr) and cr < cr_thresh:
            insights.append({
                "Loan": loan_no,
                "Category": "Covenant",
                "Severity": "Medium",
                "Observation": f"Current ratio ({cr:.2f}) deteriorated below {cr_thresh}.",
                "Recommendation": "Improve working capital management; monitor receivables aging.",
            })

        int_diff = row.get("Interest_Difference", row.get("interest_difference", 0))
        if int_diff and abs(float(int_diff)) > 0:
            insights.append({
                "Loan": loan_no,
                "Category": "Interest",
                "Severity": "High" if abs(float(int_diff)) > 50000 else "Medium",
                "Observation": f"Interest variance of ₹{abs(float(int_diff)):,.0f} detected.",
                "Recommendation": "Obtain interest computation from bank and reconcile.",
            })

        risk = row.get("Risk_Level", row.get("risk_level", ""))
        if str(risk).lower() in ("high", "critical"):
            insights.append({
                "Loan": loan_no,
                "Category": "Risk",
                "Severity": str(risk).title(),
                "Observation": f"Loan classified as {risk} risk.",
                "Recommendation": "Escalate to engagement partner; prepare management representation.",
            })

    if roc is not None and not roc.empty:
        pending = roc[roc.get("Filing_Status", roc.get("status", pd.Series())) == "Pending"]
        for _, r in pending.iterrows():
            insights.append({
                "Loan": r.get("Loan_Number", "N/A"),
                "Category": "ROC",
                "Severity": "High",
                "Observation": f"ROC filing pending for {r.get('Form_Type', 'CHG-1')}.",
                "Recommendation": "Verify charge creation with MCA portal; obtain board resolution.",
            })

    return insights


def compare_schedules(uploaded: pd.DataFrame, calculated: pd.DataFrame, key_cols: list[str]) -> pd.DataFrame:
    """Compare uploaded schedule with calculated schedule."""
    if uploaded.empty or calculated.empty:
        return pd.DataFrame()
    merged = uploaded.merge(calculated, on=key_cols, how="outer", suffixes=("_Uploaded", "_Calculated"), indicator=True)
    merged["Mismatch"] = merged["_merge"] != "both"
    for col in ["Interest", "Principal", "EMI", "Outstanding"]:
        u, c = f"{col}_Uploaded", f"{col}_Calculated"
        if u in merged.columns and c in merged.columns:
            merged[f"{col}_Variance"] = merged[u].fillna(0) - merged[c].fillna(0)
    return merged
