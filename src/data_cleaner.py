"""
data_cleaner.py
---------------
Turns messy raw expense data into clean, analysis-ready data.

Cleaning steps (in order):
1. Remove exact duplicate rows
2. Fix text columns (trim spaces, consistent capitalisation)
3. Convert amount to a number; drop missing / invalid / negative amounts
4. Convert date text to real datetime; drop invalid dates
5. Fill missing payment method and description
6. Add helper columns (month, weekday, weekend flag) for analysis
"""

import pandas as pd

from src.config import CATEGORIES, PAYMENT_METHODS


def clean_data(df):
    """
    Clean the raw expense DataFrame.

    Returns
    -------
    clean_df : pandas.DataFrame
    log      : dict  -> how many rows each step fixed or removed (shown in the report)
    """
    df = df.copy()
    log = {"raw_rows": len(df)}

    # 1) Duplicates ----------------------------------------------------
    before = len(df)
    df = df.drop_duplicates()
    log["duplicates_removed"] = before - len(df)

    # 2) Text cleanup --------------------------------------------------
    # Map lowercase name -> official name, e.g. 'food & dining' -> 'Food & Dining'
    category_map = {c.lower(): c for c in CATEGORIES}
    cleaned_cat = df["category"].astype(str).str.strip().str.lower()
    log["categories_fixed"] = int((df["category"].astype(str) != cleaned_cat.map(category_map)).sum())
    df["category"] = cleaned_cat.map(category_map).fillna("Other")

    payment_map = {p.lower(): p for p in PAYMENT_METHODS}
    df["payment_method"] = df["payment_method"].astype("string").str.strip().str.lower().map(payment_map)
    log["missing_payment_filled"] = int(df["payment_method"].isna().sum())
    df["payment_method"] = df["payment_method"].fillna("Unknown")

    df["description"] = df["description"].fillna("No description").astype(str).str.strip()

    # 3) Amount --------------------------------------------------------
    # errors='coerce' turns 'N/A' or other junk into NaN instead of crashing
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    invalid_amount = df["amount"].isna() | (df["amount"] <= 0)
    log["invalid_amounts_removed"] = int(invalid_amount.sum())
    df = df[~invalid_amount]

    # 4) Date ----------------------------------------------------------
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    log["invalid_dates_removed"] = int(df["date"].isna().sum())
    df = df.dropna(subset=["date"])

    # 5) Helper columns for analysis ------------------------------------
    df["month"] = df["date"].dt.to_period("M").astype(str)   # '2026-03'
    df["month_name"] = df["date"].dt.strftime("%b %Y")       # 'Mar 2026'
    df["day_of_week"] = df["date"].dt.day_name()             # 'Saturday'
    df["is_weekend"] = df["date"].dt.dayofweek >= 5

    df = df.sort_values("date").reset_index(drop=True)
    log["clean_rows"] = len(df)
    log["rows_removed_total"] = log["raw_rows"] - log["clean_rows"]

    print(f"[OK] Data cleaned: {log['raw_rows']} -> {log['clean_rows']} rows "
          f"({log['rows_removed_total']} removed)")
    return df, log
