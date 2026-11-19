"""
config.py
---------
Central place for every setting used in the project.

Change values here (income, budgets, date range, folders) instead of
hunting through the code. Every other module imports from this file.
"""

from pathlib import Path

# ------------------------------------------------------------------
# 1. Folder paths (built relative to the project root, so the project
#    works on any computer - Windows, Mac or Linux)
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"          # raw input CSV files
OUTPUT_DIR = BASE_DIR / "outputs"     # cleaned data + summary CSVs
IMAGES_DIR = BASE_DIR / "images"      # charts (PNG)
REPORTS_DIR = BASE_DIR / "reports"    # final text report

RAW_DATA_FILE = DATA_DIR / "expenses_raw.csv"
CLEAN_DATA_FILE = OUTPUT_DIR / "expenses_clean.csv"
REPORT_FILE = REPORTS_DIR / "expense_summary_report.txt"

# ------------------------------------------------------------------
# 2. Synthetic data settings
# ------------------------------------------------------------------
RANDOM_SEED = 42                 # same seed -> same dataset every run
START_DATE = "2026-01-01"
END_DATE = "2026-06-30"

# Currency label. "Rs." is used instead of the rupee symbol because some
# Windows terminals cannot print the symbol.
CURRENCY = "Rs."

# ------------------------------------------------------------------
# 3. Personal finance settings
# ------------------------------------------------------------------
MONTHLY_INCOME = 36000   # e.g. stipend / salary / pocket money per month

# Monthly budget limit for each category (used for overspending checks)
MONTHLY_BUDGET = {
    "Rent": 8000,
    "Food & Dining": 4500,
    "Groceries": 3000,
    "Transport": 1500,
    "Shopping": 2500,
    "Entertainment": 1500,
    "Utilities": 2000,
    "Education": 1500,
    "Health": 1000,
    "Subscriptions": 500,
}

# Official list of categories. Anything else is cleaned into "Other".
CATEGORIES = list(MONTHLY_BUDGET.keys())

PAYMENT_METHODS = ["UPI", "Debit Card", "Credit Card", "Cash", "Net Banking"]

# ------------------------------------------------------------------
# 4. Chart colours (colour-blind-safe palette, fixed order)
# ------------------------------------------------------------------
PRIMARY_COLOR = "#2a78d6"     # main bars / lines
LIGHT_PRIMARY = "#9ec5f4"     # background bars (daily trend)
DARK_PRIMARY = "#184f95"      # emphasis line
NEUTRAL_COLOR = "#b5b3ad"     # budget / reference marks
ALERT_COLOR = "#d03b3b"       # overspending only
TEXT_COLOR = "#52514e"
CATEGORICAL_PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                       "#e87ba4", "#008300", "#6250d6", "#e34948"]
