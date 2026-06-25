"""Generate sample data and Excel templates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

APP_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = APP_ROOT / "sample_data"
TEMPLATES_DIR = APP_ROOT / "templates"


def generate_sample_data() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    loan_master = pd.DataFrame([
        {"Loan_Number": "TL-001", "Bank": "HDFC Bank", "Borrower": "ABC Industries Ltd", "Loan_Type": "Term Loan",
         "Sanctioned_Amount": 50000000, "Outstanding_Amount": 38500000, "Interest_Rate": 9.75, "Tenure_Months": 84,
         "Loan_Date": "2022-04-01", "Purpose": "Machinery", "EMI": 825000, "Risk_Level": "Medium",
         "DSCR_Actual": 1.18, "DSCR_Sanctioned": 1.25, "Current_Ratio_Actual": 1.42, "Current_Ratio_Sanctioned": 1.33,
         "Interest_Difference": 125000, "Agreement_Number": "AGR/TL/2022/001"},
        {"Loan_Number": "WC-002", "Bank": "ICICI Bank", "Borrower": "ABC Industries Ltd", "Loan_Type": "Working Capital",
         "Sanctioned_Amount": 25000000, "Outstanding_Amount": 18750000, "Interest_Rate": 10.25, "Tenure_Months": 12,
         "Loan_Date": "2023-01-15", "Purpose": "Working Capital", "EMI": 0, "Risk_Level": "Low",
         "DSCR_Actual": 1.45, "DSCR_Sanctioned": 1.20, "Current_Ratio_Actual": 1.55, "Current_Ratio_Sanctioned": 1.25,
         "Interest_Difference": -45000, "Agreement_Number": "AGR/WC/2023/002"},
        {"Loan_Number": "TL-003", "Bank": "SBI", "Borrower": "ABC Industries Ltd", "Loan_Type": "Term Loan",
         "Sanctioned_Amount": 75000000, "Outstanding_Amount": 62000000, "Interest_Rate": 9.50, "Tenure_Months": 120,
         "Loan_Date": "2021-06-01", "Purpose": "Expansion", "EMI": 975000, "Risk_Level": "High",
         "DSCR_Actual": 1.05, "DSCR_Sanctioned": 1.30, "Current_Ratio_Actual": 1.15, "Current_Ratio_Sanctioned": 1.33,
         "Interest_Difference": 285000, "Agreement_Number": "AGR/TL/2021/003"},
        {"Loan_Number": "CC-004", "Bank": "Axis Bank", "Borrower": "ABC Industries Ltd", "Loan_Type": "Cash Credit",
         "Sanctioned_Amount": 15000000, "Outstanding_Amount": 12300000, "Interest_Rate": 11.00, "Tenure_Months": 12,
         "Loan_Date": "2023-06-01", "Purpose": "Working Capital", "EMI": 0, "Risk_Level": "Critical",
         "DSCR_Actual": 0.95, "DSCR_Sanctioned": 1.20, "Current_Ratio_Actual": 1.08, "Current_Ratio_Sanctioned": 1.25,
         "Interest_Difference": 95000, "Agreement_Number": "AGR/CC/2023/004"},
        {"Loan_Number": "TL-005", "Bank": "Kotak Mahindra", "Borrower": "ABC Industries Ltd", "Loan_Type": "Term Loan",
         "Sanctioned_Amount": 30000000, "Outstanding_Amount": 24500000, "Interest_Rate": 9.85, "Tenure_Months": 60,
         "Loan_Date": "2022-09-01", "Purpose": "Vehicle", "EMI": 635000, "Risk_Level": "Low",
         "DSCR_Actual": 1.62, "DSCR_Sanctioned": 1.25, "Current_Ratio_Actual": 1.78, "Current_Ratio_Sanctioned": 1.33,
         "Interest_Difference": 12000, "Agreement_Number": "AGR/TL/2022/005"},
    ])

    interest_schedule = pd.DataFrame([
        {"Loan_Number": "TL-001", "Period": "Q1-FY25", "Bank_Interest": 945000, "Calculated_Interest": 820000, "Interest_Difference": 125000},
        {"Loan_Number": "WC-002", "Period": "Q1-FY25", "Bank_Interest": 480000, "Calculated_Interest": 525000, "Interest_Difference": -45000},
        {"Loan_Number": "TL-003", "Period": "Q1-FY25", "Bank_Interest": 1475000, "Calculated_Interest": 1190000, "Interest_Difference": 285000},
        {"Loan_Number": "CC-004", "Period": "Q1-FY25", "Bank_Interest": 338000, "Calculated_Interest": 243000, "Interest_Difference": 95000},
        {"Loan_Number": "TL-005", "Period": "Q1-FY25", "Bank_Interest": 602000, "Calculated_Interest": 590000, "Interest_Difference": 12000},
    ])

    repayment_schedule = pd.DataFrame([
        {"Loan_Number": "TL-001", "Installment_No": 1, "Due_Date": "2024-04-01", "EMI": 825000, "Principal": 512000,
         "Interest": 313000, "Outstanding": 37988000, "Status": "Paid"},
        {"Loan_Number": "TL-001", "Installment_No": 2, "Due_Date": "2024-05-01", "EMI": 825000, "Principal": 516000,
         "Interest": 309000, "Outstanding": 37472000, "Status": "Paid"},
        {"Loan_Number": "TL-001", "Installment_No": 3, "Due_Date": "2024-06-01", "EMI": 825000, "Principal": 520000,
         "Interest": 305000, "Outstanding": 36952000, "Status": "Overdue"},
        {"Loan_Number": "TL-003", "Installment_No": 1, "Due_Date": "2024-04-01", "EMI": 975000, "Principal": 485000,
         "Interest": 490000, "Outstanding": 61515000, "Status": "Missed"},
    ])

    covenant_details = pd.DataFrame([
        {"Loan_Number": "TL-001", "Covenant": "DSCR", "Actual": 1.18, "Sanctioned": 1.25, "Status": "Warning"},
        {"Loan_Number": "TL-001", "Covenant": "Current Ratio", "Actual": 1.42, "Sanctioned": 1.33, "Status": "Compliant"},
        {"Loan_Number": "TL-003", "Covenant": "DSCR", "Actual": 1.05, "Sanctioned": 1.30, "Status": "Breached"},
        {"Loan_Number": "TL-003", "Covenant": "Debt Equity", "Actual": 2.8, "Sanctioned": 2.5, "Status": "Breached"},
        {"Loan_Number": "CC-004", "Covenant": "DSCR", "Actual": 0.95, "Sanctioned": 1.20, "Status": "Breached"},
        {"Loan_Number": "CC-004", "Covenant": "Current Ratio", "Actual": 1.08, "Sanctioned": 1.25, "Status": "Breached"},
    ])

    security_details = pd.DataFrame([
        {"Loan_Number": "TL-001", "Security_Type": "Hypothecation", "Asset_Description": "Plant & Machinery",
         "Security_Value": 60000000, "Charge_Status": "Created", "Charge_ID": "CHG-10001"},
        {"Loan_Number": "TL-003", "Security_Type": "Mortgage", "Asset_Description": "Factory Land & Building",
         "Security_Value": 95000000, "Charge_Status": "Created", "Charge_ID": "CHG-10003"},
        {"Loan_Number": "CC-004", "Security_Type": "Hypothecation", "Asset_Description": "Stock & Book Debts",
         "Security_Value": 20000000, "Charge_Status": "Pending", "Charge_ID": ""},
    ])

    roc_details = pd.DataFrame([
        {"Loan_Number": "TL-001", "Form_Type": "CHG-1", "Filing_Date": "2022-05-15", "Filing_Status": "Filed", "ROC_Number": "ROC/2022/001"},
        {"Loan_Number": "TL-003", "Form_Type": "CHG-1", "Filing_Date": "2021-07-20", "Filing_Status": "Filed", "ROC_Number": "ROC/2021/003"},
        {"Loan_Number": "CC-004", "Form_Type": "CHG-1", "Filing_Date": "", "Filing_Status": "Pending", "ROC_Number": ""},
        {"Loan_Number": "TL-003", "Form_Type": "CHG-4", "Filing_Date": "", "Filing_Status": "Overdue", "ROC_Number": ""},
    ])

    drawdown_register = pd.DataFrame([
        {"Loan_Number": "TL-001", "Drawdown_Date": "2022-04-15", "Amount": 25000000, "Purpose": "Machinery Purchase"},
        {"Loan_Number": "TL-001", "Drawdown_Date": "2022-06-01", "Amount": 25000000, "Purpose": "Installation"},
        {"Loan_Number": "TL-003", "Drawdown_Date": "2021-06-15", "Amount": 75000000, "Purpose": "Factory Expansion"},
    ])

    utilization_register = pd.DataFrame([
        {"Loan_Number": "TL-001", "Transaction_Date": "2022-04-20", "Amount": 24000000, "Vendor": "Machinery Corp",
         "Purpose_Mapped": "Machinery", "End_Use_Flag": "Compliant"},
        {"Loan_Number": "WC-002", "Transaction_Date": "2023-02-10", "Amount": 5000000, "Vendor": "Investment Ltd",
         "Purpose_Mapped": "Investment", "End_Use_Flag": "Diversion"},
        {"Loan_Number": "CC-004", "Transaction_Date": "2023-07-15", "Amount": 1000000, "Vendor": "Cash Withdrawal",
         "Purpose_Mapped": "Cash", "End_Use_Flag": "Suspicious"},
    ])

    datasets = {
        "loan_master": loan_master,
        "interest_schedule": interest_schedule,
        "repayment_schedule": repayment_schedule,
        "covenant_details": covenant_details,
        "security_details": security_details,
        "roc_details": roc_details,
        "drawdown_register": drawdown_register,
        "utilization_register": utilization_register,
    }

    for name, df in datasets.items():
        path = SAMPLE_DIR / f"{name}.xlsx"
        df.to_excel(path, index=False)
        tpl_path = TEMPLATES_DIR / f"{name}_template.xlsx"
        df.head(0).to_excel(tpl_path, index=False)


if __name__ == "__main__":
    generate_sample_data()
    print("Sample data generated.")
