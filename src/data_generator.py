"""
data_generator.py
-----------------
Creates a realistic SYNTHETIC expense dataset (no real bank data needed).

How the simulation works:
1. Fixed monthly bills  -> Rent, Subscriptions, Utilities on fixed dates.
2. Daily expenses       -> each day gets a random number of transactions
                           (more on weekends), each with a random category,
                           amount, payment method and description.
3. Seasonal effects     -> some months spend more (festival / travel / sale).
4. "Dirty" records      -> a few duplicates, blanks, typos and invalid values
                           are injected ON PURPOSE so the cleaning step has
                           real work to do (just like real-world data).
"""

import numpy as np
import pandas as pd

from src.config import RANDOM_SEED, START_DATE, END_DATE, RAW_DATA_FILE, DATA_DIR

# Variable (day-to-day) categories:
# (relative frequency, min amount, max amount, sample descriptions)
VARIABLE_CATEGORIES = {
    "Food & Dining": (40, 40, 350, ["Lunch at canteen", "Swiggy order", "Zomato order",
                                    "Coffee with friends", "Dinner outside", "Snacks", "Tea and samosa"]),
    "Groceries":     (12, 100, 900, ["Weekly groceries", "Vegetables and fruits", "Milk and bread",
                                      "BigBasket order", "Blinkit order"]),
    "Transport":     (22, 20, 250, ["Metro card recharge", "Auto rickshaw", "Uber ride",
                                    "Ola ride", "Bus ticket", "Petrol"]),
    "Shopping":      (5, 250, 2000, ["Clothes", "Amazon order", "Flipkart order", "Shoes",
                                     "Phone accessories", "Stationery"]),
    "Entertainment": (7, 100, 800, ["Movie tickets", "Gaming top-up", "Concert ticket",
                                     "Bowling with friends", "Weekend outing"]),
    "Education":     (5, 100, 1500, ["Online course", "Books", "Exam fee", "Printouts",
                                     "Coding bootcamp module"]),
    "Health":        (3, 80, 1000, ["Pharmacy", "Doctor visit", "Gym supplements", "Lab test"]),
}

# Payment method probabilities per category  [UPI, Debit, Credit, Cash, NetBanking]
PAYMENT_PROBS = {
    "Food & Dining": [0.65, 0.08, 0.07, 0.20, 0.00],
    "Groceries":     [0.55, 0.15, 0.15, 0.15, 0.00],
    "Transport":     [0.60, 0.05, 0.05, 0.30, 0.00],
    "Shopping":      [0.35, 0.20, 0.40, 0.05, 0.00],
    "Entertainment": [0.55, 0.15, 0.25, 0.05, 0.00],
    "Education":     [0.30, 0.20, 0.20, 0.05, 0.25],
    "Health":        [0.50, 0.20, 0.10, 0.20, 0.00],
    "Rent":          [0.40, 0.00, 0.00, 0.00, 0.60],
    "Utilities":     [0.50, 0.00, 0.10, 0.00, 0.40],
    "Subscriptions": [0.30, 0.10, 0.60, 0.00, 0.00],
}
PAYMENT_METHODS = ["UPI", "Debit Card", "Credit Card", "Cash", "Net Banking"]

# Month-wise spending multiplier (simulates real life seasonality)
MONTH_FACTOR = {
    1: 1.00,   # January  - normal
    2: 0.90,   # February - short month, saving mode
    3: 1.15,   # March    - Holi festival + exam fees
    4: 1.00,   # April    - normal
    5: 1.30,   # May      - summer trip + sale shopping
    6: 0.95,   # June     - back to routine
}


def _pick_payment(rng, category):
    """Choose a payment method using the category's probability list."""
    return rng.choice(PAYMENT_METHODS, p=PAYMENT_PROBS[category])


def _fixed_monthly_expenses(rng, month_start):
    """Bills that repeat every month (rent, subscriptions, utilities)."""
    rows = []
    rows.append([month_start, "Rent", 8000, _pick_payment(rng, "Rent"), "Monthly room rent"])
    rows.append([month_start + pd.Timedelta(days=4), "Subscriptions", 119,
                 _pick_payment(rng, "Subscriptions"), "Spotify Premium"])
    rows.append([month_start + pd.Timedelta(days=9), "Subscriptions", 299,
                 _pick_payment(rng, "Subscriptions"), "Netflix plan"])
    rows.append([month_start + pd.Timedelta(days=6), "Utilities",
                 int(rng.integers(600, 1300)), _pick_payment(rng, "Utilities"), "Electricity bill"])
    rows.append([month_start + pd.Timedelta(days=11), "Utilities", 599,
                 _pick_payment(rng, "Utilities"), "Wi-Fi bill"])
    rows.append([month_start + pd.Timedelta(days=14), "Utilities", 299,
                 _pick_payment(rng, "Utilities"), "Mobile recharge"])
    return rows


def _inject_dirty_data(rng, df):
    """
    Add realistic data-quality problems:
    - duplicate rows (same expense entered twice)
    - missing amount / payment method / description
    - text typos: lowercase, extra spaces
    - invalid values: negative amount, 'N/A', bad date
    """
    df = df.copy()
    n = len(df)

    # 1) Duplicates (~2%)
    dup_rows = df.sample(n=int(n * 0.02), random_state=RANDOM_SEED)
    df = pd.concat([df, dup_rows], ignore_index=True)

    # Work with amount as text so we can insert 'N/A'
    df["amount"] = df["amount"].astype(object)

    idx = rng.choice(len(df), size=int(n * 0.01), replace=False)
    df.loc[idx, "amount"] = np.nan                       # 2) missing amounts

    idx = rng.choice(len(df), size=4, replace=False)
    df.loc[idx, "amount"] = "N/A"                        # 3) non-numeric amount

    idx = rng.choice(len(df), size=3, replace=False)
    df.loc[idx, "amount"] = -250                         # 4) negative (refund/typo)

    idx = rng.choice(len(df), size=int(n * 0.015), replace=False)
    df.loc[idx, "payment_method"] = np.nan               # 5) missing payment method

    idx = rng.choice(len(df), size=int(n * 0.03), replace=False)
    df.loc[idx, "category"] = df.loc[idx, "category"].str.lower()        # 6) lowercase typo

    idx = rng.choice(len(df), size=int(n * 0.02), replace=False)
    df.loc[idx, "category"] = "  " + df.loc[idx, "category"] + " "       # 7) extra spaces

    idx = rng.choice(len(df), size=int(n * 0.02), replace=False)
    df.loc[idx, "description"] = np.nan                  # 8) missing note

    df["date"] = df["date"].astype(object)
    idx = rng.choice(len(df), size=2, replace=False)
    df.loc[idx, "date"] = "unknown"                      # 9) invalid date

    # Shuffle rows so problems are scattered (like real manual entry)
    return df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)


def generate_expense_data(save=True):
    """
    Build the synthetic dataset and (optionally) save it to data/expenses_raw.csv.

    Returns
    -------
    pandas.DataFrame with columns: date, category, amount, payment_method, description
    """
    rng = np.random.default_rng(RANDOM_SEED)
    dates = pd.date_range(START_DATE, END_DATE, freq="D")

    names = list(VARIABLE_CATEGORIES.keys())
    weights = np.array([VARIABLE_CATEGORIES[c][0] for c in names], dtype=float)
    weights = weights / weights.sum()

    rows = []
    for day in dates:
        # Fixed bills on the 1st of every month
        if day.day == 1:
            rows.extend(_fixed_monthly_expenses(rng, day))

        factor = MONTH_FACTOR.get(day.month, 1.0)
        is_weekend = day.dayofweek >= 5
        avg_txns = 2.3 if is_weekend else 1.6          # people spend more on weekends
        n_txns = rng.poisson(avg_txns)

        for _ in range(n_txns):
            category = rng.choice(names, p=weights)
            _, low, high, notes = VARIABLE_CATEGORIES[category]
            amount = rng.uniform(low, high) * factor
            # Shopping spikes harder during sale / festival months
            if category == "Shopping" and day.month in (3, 5):
                amount *= 1.4
            rows.append([day, category, round(amount), _pick_payment(rng, category),
                         rng.choice(notes)])

    # A few one-off big expenses that make the story realistic
    rows.append([pd.Timestamp("2026-03-14"), "Shopping", 3200, "Credit Card", "Holi festival shopping"])
    rows.append([pd.Timestamp("2026-05-17"), "Entertainment", 4500, "UPI", "Goa trip with friends"])
    rows.append([pd.Timestamp("2026-05-18"), "Transport", 2600, "Credit Card", "Train tickets for trip"])
    rows.append([pd.Timestamp("2026-02-20"), "Health", 1800, "Debit Card", "Dentist visit"])

    df = pd.DataFrame(rows, columns=["date", "category", "amount", "payment_method", "description"])
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    df = _inject_dirty_data(rng, df)

    if save:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(RAW_DATA_FILE, index=False)
        print(f"[OK] Synthetic dataset created: {RAW_DATA_FILE.name} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    generate_expense_data()
