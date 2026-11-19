"""
analyzer.py
-----------
All the number-crunching: category, monthly, payment-method, daily and
budget analysis, plus plain-English insights.

Every function takes the CLEAN DataFrame and returns a small DataFrame
or number, so each one is easy to test and reuse (e.g. in Streamlit).
"""

import pandas as pd

from src.config import MONTHLY_BUDGET, MONTHLY_INCOME, CURRENCY


def total_spending(df):
    """Sum of all expenses."""
    return float(df["amount"].sum())


def category_summary(df):
    """Total, count, average and % share per category (highest first)."""
    summary = (df.groupby("category")["amount"]
                 .agg(total="sum", transactions="count", average="mean")
                 .sort_values("total", ascending=False))
    summary["share_pct"] = summary["total"] / summary["total"].sum() * 100
    return summary.round(2).reset_index()


def highest_spending_category(df):
    """Return (category_name, amount) of the biggest spending category."""
    totals = df.groupby("category")["amount"].sum()
    return totals.idxmax(), float(totals.max())


def monthly_summary(df, income=MONTHLY_INCOME):
    """Month-wise spending, change vs last month, savings and savings rate."""
    summary = (df.groupby("month")["amount"]
                 .agg(total_spent="sum", transactions="count")
                 .reset_index())
    summary["change_pct"] = summary["total_spent"].pct_change() * 100
    summary["income"] = income
    summary["savings"] = summary["income"] - summary["total_spent"]
    summary["savings_rate_pct"] = summary["savings"] / summary["income"] * 100
    return summary.round(2)


def payment_summary(df):
    """How much money moved through each payment method."""
    summary = (df.groupby("payment_method")["amount"]
                 .agg(total="sum", transactions="count")
                 .sort_values("total", ascending=False))
    summary["share_pct"] = summary["total"] / summary["total"].sum() * 100
    return summary.round(2).reset_index()


def daily_spending(df):
    """
    Spending per calendar day. Days with no expense are filled with 0
    (important! otherwise the average daily spend is overstated).
    Also adds a 7-day rolling average to smooth out noise.
    """
    daily = df.groupby("date")["amount"].sum()
    full_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily = daily.reindex(full_range, fill_value=0)
    out = daily.rename("amount").to_frame()
    out["rolling_7d_avg"] = out["amount"].rolling(window=7, min_periods=1).mean()
    out.index.name = "date"
    return out.round(2).reset_index()


def average_daily_spending(df):
    """Total spending divided by number of calendar days in the period."""
    days = (df["date"].max() - df["date"].min()).days + 1
    return total_spending(df) / days


def weekday_vs_weekend(df):
    """Average spending per day on weekdays vs weekends."""
    daily = daily_spending(df)
    daily["is_weekend"] = daily["date"].dt.dayofweek >= 5
    result = daily.groupby("is_weekend")["amount"].mean()
    return {"weekday_avg": float(result.get(False, 0)), "weekend_avg": float(result.get(True, 0))}


def budget_vs_actual(df, budget=MONTHLY_BUDGET):
    """
    Compare each month's category spending with the monthly budget.
    'over_budget' = True means overspending in that month.
    """
    pivot = df.pivot_table(index="month", columns="category", values="amount",
                           aggfunc="sum", fill_value=0)
    records = []
    for month, row in pivot.iterrows():
        for category, limit in budget.items():
            spent = float(row.get(category, 0))
            records.append({
                "month": month,
                "category": category,
                "budget": limit,
                "actual": round(spent, 2),
                "difference": round(limit - spent, 2),
                "over_budget": spent > limit,
            })
    return pd.DataFrame(records)


def category_month_matrix(df):
    """Category x Month table of spending (used for the heatmap)."""
    return df.pivot_table(index="category", columns="month", values="amount",
                          aggfunc="sum", fill_value=0).round(0)


def top_transactions(df, n=5, exclude=("Rent",)):
    """The n largest single expenses (fixed rent is excluded - it is always the top)."""
    cols = ["date", "category", "amount", "payment_method", "description"]
    flexible = df[~df["category"].isin(exclude)]
    return flexible.nlargest(n, "amount")[cols].reset_index(drop=True)


def run_full_analysis(df):
    """Run every analysis once and return the results in one dictionary."""
    top_cat, top_cat_amt = highest_spending_category(df)
    return {
        "total": total_spending(df),
        "avg_daily": average_daily_spending(df),
        "highest_category": top_cat,
        "highest_category_amount": top_cat_amt,
        "category": category_summary(df),
        "monthly": monthly_summary(df),
        "payment": payment_summary(df),
        "daily": daily_spending(df),
        "weekday_weekend": weekday_vs_weekend(df),
        "budget": budget_vs_actual(df),
        "matrix": category_month_matrix(df),
        "top": top_transactions(df),
        "start": df["date"].min(),
        "end": df["date"].max(),
        "transactions": len(df),
    }


def generate_insights(results):
    """Convert the numbers into short, human-readable insights."""
    c = CURRENCY
    monthly = results["monthly"]
    cat = results["category"]
    pay = results["payment"]
    budget = results["budget"]
    ww = results["weekday_weekend"]

    peak = monthly.loc[monthly["total_spent"].idxmax()]
    low = monthly.loc[monthly["total_spent"].idxmin()]
    avg_savings_rate = monthly["savings_rate_pct"].mean()

    # Ignore Rent (fixed cost) when talking about controllable spending
    flexible = cat[cat["category"] != "Rent"].iloc[0]

    overs = budget[budget["over_budget"]]
    over_counts = overs["category"].value_counts()

    insights = [
        f"Total spending over {len(monthly)} months was {c}{results['total']:,.0f} "
        f"across {results['transactions']} transactions.",
        f"Highest spending category is {results['highest_category']} "
        f"({c}{results['highest_category_amount']:,.0f}, {cat.iloc[0]['share_pct']:.1f}% of total).",
        f"Biggest controllable expense is {flexible['category']} "
        f"({flexible['share_pct']:.1f}% of total) - the best place to cut costs.",
        f"Peak month was {peak['month']} ({c}{peak['total_spent']:,.0f}); "
        f"lowest was {low['month']} ({c}{low['total_spent']:,.0f}).",
        f"Average daily spending is {c}{results['avg_daily']:,.0f}.",
        f"Weekend days average {c}{ww['weekend_avg']:,.0f} vs {c}{ww['weekday_avg']:,.0f} on weekdays "
        f"({(ww['weekend_avg'] / ww['weekday_avg'] - 1) * 100:+.0f}%).",
        f"{pay.iloc[0]['payment_method']} is the most used payment method "
        f"({pay.iloc[0]['share_pct']:.1f}% of money spent).",
        f"Average savings rate is {avg_savings_rate:.1f}% of a {c}{MONTHLY_INCOME:,} monthly income.",
    ]

    if len(overs):
        worst = over_counts.index[0]
        insights.append(
            f"Budget exceeded {len(overs)} times; {worst} went over budget in "
            f"{over_counts.iloc[0]} of {len(monthly)} months."
        )
    else:
        insights.append("No category exceeded its monthly budget - great discipline!")

    negative = monthly[monthly["savings"] < 0]
    if len(negative):
        insights.append(f"Overspending alert: spending exceeded income in {', '.join(negative['month'])}.")
    return insights
