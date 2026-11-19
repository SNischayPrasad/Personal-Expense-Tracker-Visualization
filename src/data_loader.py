"""
data_loader.py
--------------
Reads the expense CSV file and lets the user add manual expense entries.
"""

import csv
from datetime import datetime

import pandas as pd

from src.config import RAW_DATA_FILE, CATEGORIES, PAYMENT_METHODS, CURRENCY

REQUIRED_COLUMNS = ["date", "category", "amount", "payment_method", "description"]


def load_expenses(file_path=RAW_DATA_FILE):
    """
    Load expenses from a CSV file into a DataFrame.

    Raises a clear error if the file is missing or columns are wrong,
    which is much friendlier than a long pandas traceback.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"{file_path} not found. Run 'python main.py --generate' first "
            f"or add expenses with 'python main.py --add'."
        )

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()   # ' Amount ' -> 'amount'

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    print(f"[OK] Loaded {len(df)} records from {file_path.name}")
    return df


def _ask_choice(prompt, options):
    """Show a numbered menu and return the chosen option."""
    print(prompt)
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  Invalid choice, try again.")


def add_expense_interactive(file_path=RAW_DATA_FILE):
    """
    Manual expense entry from the terminal.
    The new record is APPENDED to the CSV so old data is never lost.
    """
    print("\n=== Add a New Expense ===")

    # Date (press Enter for today)
    while True:
        date_text = input("Date (YYYY-MM-DD, Enter = today): ").strip()
        if not date_text:
            date_text = datetime.today().strftime("%Y-%m-%d")
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            break
        except ValueError:
            print("  Wrong format. Example: 2026-06-15")

    category = _ask_choice("Category:", CATEGORIES)

    while True:
        try:
            amount = float(input(f"Amount ({CURRENCY}): ").strip())
            if amount > 0:
                break
            print("  Amount must be greater than 0.")
        except ValueError:
            print("  Please enter a number, e.g. 250")

    payment = _ask_choice("Payment method:", PAYMENT_METHODS)
    note = input("Note / description: ").strip()

    file_exists = file_path.exists()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(REQUIRED_COLUMNS)
        writer.writerow([date_text, category, amount, payment, note])

    print(f"[OK] Saved: {date_text} | {category} | {CURRENCY}{amount:,.2f} | {payment}")
