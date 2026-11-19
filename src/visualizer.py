"""
visualizer.py
-------------
Creates and saves all charts as PNG files in the images/ folder.

Charts:
1. Category-wise spending (horizontal bar)
2. Monthly spending trend (line) with income reference line
3. Payment method share (donut / pie)
4. Daily spending trend (bars + 7-day rolling average)
5. Budget vs actual - average month (grouped bar)
6. Category x month heatmap
"""

import matplotlib
matplotlib.use("Agg")          # draw charts without opening a window (works everywhere)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from src.config import (IMAGES_DIR, CURRENCY, MONTHLY_INCOME, PRIMARY_COLOR, LIGHT_PRIMARY,
                        DARK_PRIMARY, NEUTRAL_COLOR, ALERT_COLOR, TEXT_COLOR, CATEGORICAL_PALETTE)

# One consistent, clean style for every chart
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": "#d6d4ce",
    "grid.color": "#ebe9e4",
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "font.size": 10,
})

money_fmt = mticker.FuncFormatter(lambda x, _: f"{CURRENCY}{x:,.0f}")


def _save(fig, filename):
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGES_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"   saved images/{filename}")
    return path


def plot_category_bar(category_df):
    """Horizontal bar chart: easiest way to compare categories with long names."""
    data = category_df.sort_values("total")
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data["category"], data["total"], color=PRIMARY_COLOR, height=0.6)
    for bar, share in zip(bars, data["share_pct"]):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                f"  {CURRENCY}{bar.get_width():,.0f} ({share:.1f}%)",
                va="center", fontsize=9, color=TEXT_COLOR)
    ax.set_title("Category-wise Spending (Jan - Jun 2026)")
    ax.set_xlabel("Total spent")
    ax.xaxis.set_major_formatter(money_fmt)
    ax.set_xlim(0, data["total"].max() * 1.25)
    ax.grid(axis="y", visible=False)
    return _save(fig, "01_category_spending_bar.png")


def plot_monthly_trend(monthly_df):
    """Line chart of total spending per month, compared with income."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = pd.to_datetime(monthly_df["month"]).dt.strftime("%b %Y")   # 2026-03 -> Mar 2026
    y = monthly_df["total_spent"]
    ax.plot(x, y, marker="o", markersize=8, linewidth=2, color=PRIMARY_COLOR, label="Total spent")
    ax.axhline(MONTHLY_INCOME, color=NEUTRAL_COLOR, linestyle="--", linewidth=1.5,
               label=f"Monthly income ({CURRENCY}{MONTHLY_INCOME:,})")
    for xi, yi, chg in zip(x, y, monthly_df["change_pct"]):
        label = f"{CURRENCY}{yi:,.0f}" if chg != chg else f"{CURRENCY}{yi:,.0f}\n({chg:+.0f}%)"  # chg!=chg -> NaN
        # put the label above the point if it is above income, else below (avoids the income line)
        offset, va = ((0, 12), "bottom") if yi >= MONTHLY_INCOME else ((0, -14), "top")
        ax.annotate(label, (xi, yi), textcoords="offset points", xytext=offset,
                    ha="center", va=va, fontsize=9, color=TEXT_COLOR)
    ax.set_title("Monthly Spending Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.yaxis.set_major_formatter(money_fmt)
    ax.set_ylim(0, max(y.max(), MONTHLY_INCOME) * 1.2)
    ax.legend(loc="lower right", frameon=False)
    return _save(fig, "02_monthly_spending_trend.png")


def plot_payment_pie(payment_df):
    """Donut chart of money share by payment method (few slices -> pie is readable)."""
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = CATEGORICAL_PALETTE[:len(payment_df)]
    wedges, _, autotexts = ax.pie(
        payment_df["total"], colors=colors,
        autopct=lambda p: f"{p:.1f}%" if p >= 3 else "", startangle=90, counterclock=False, pctdistance=0.78,
        wedgeprops={"width": 0.45, "edgecolor": "#fcfcfb", "linewidth": 2},
        textprops={"color": TEXT_COLOR, "fontsize": 10},
    )
    for t in autotexts:
        t.set_color("#0b0b0b")
        t.set_fontsize(9)
    total = payment_df["total"].sum()
    ax.text(0, 0, f"Total\n{CURRENCY}{total:,.0f}", ha="center", va="center",
            fontsize=12, fontweight="bold", color="#0b0b0b")
    legend_labels = [f"{m}  ({s:.1f}%)" for m, s in zip(payment_df["payment_method"], payment_df["share_pct"])]
    ax.legend(wedges, legend_labels, title="Payment method", loc="center left",
              bbox_to_anchor=(1.0, 0.5), frameon=False)
    ax.set_title("Spending by Payment Method", pad=16)
    ax.axis("equal")
    return _save(fig, "03_payment_method_pie.png")


def plot_daily_trend(daily_df, avg_daily):
    """Daily spending bars + 7-day rolling average line to show the real trend."""
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.bar(daily_df["date"], daily_df["amount"], color=LIGHT_PRIMARY, width=0.9, label="Daily spending")
    ax.plot(daily_df["date"], daily_df["rolling_7d_avg"], color=DARK_PRIMARY, linewidth=2,
            label="7-day rolling average")
    ax.axhline(avg_daily, color=NEUTRAL_COLOR, linestyle="--", linewidth=1.2,
               label=f"Overall daily average ({CURRENCY}{avg_daily:,.0f})")
    ax.set_title("Daily Spending Trend (tall spikes on the 1st = monthly rent)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount")
    ax.yaxis.set_major_formatter(money_fmt)
    ax.legend(loc="upper right", frameon=False)
    return _save(fig, "04_daily_spending_trend.png")


def plot_budget_vs_actual(budget_df):
    """Average monthly spending per category vs its budget; red = over budget."""
    avg = budget_df.groupby("category")[["budget", "actual"]].mean().sort_values("budget")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    y = range(len(avg))
    h = 0.38
    ax.barh([i + h / 2 for i in y], avg["budget"], height=h, color=NEUTRAL_COLOR, label="Monthly budget")
    colors = [ALERT_COLOR if a > b else PRIMARY_COLOR for a, b in zip(avg["actual"], avg["budget"])]
    ax.barh([i - h / 2 for i in y], avg["actual"], height=h, color=colors, label="Average actual")
    for i, (a, b) in enumerate(zip(avg["actual"], avg["budget"])):
        tag = "  OVER" if a > b else ""
        ax.text(max(a, b), i - h / 2, f"  {CURRENCY}{a:,.0f}{tag}", va="center", fontsize=8.5,
                color=ALERT_COLOR if a > b else TEXT_COLOR)
    ax.set_yticks(list(y))
    ax.set_yticklabels(avg.index)
    ax.xaxis.set_major_formatter(money_fmt)
    ax.set_xlim(0, avg[["budget", "actual"]].max().max() * 1.25)
    ax.set_title("Budget vs Actual (average per month)")
    ax.set_xlabel("Amount per month")
    ax.grid(axis="y", visible=False)
    # Custom legend so 'over budget' red is explained (not colour alone - also the OVER text)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=NEUTRAL_COLOR, label="Monthly budget"),
                       Patch(color=PRIMARY_COLOR, label="Actual (within budget)"),
                       Patch(color=ALERT_COLOR, label="Actual (over budget)")],
              loc="lower right", frameon=False)
    return _save(fig, "05_budget_vs_actual.png")


def plot_category_heatmap(matrix_df):
    """Heatmap: which category was expensive in which month (one-hue blue scale)."""
    data = matrix_df.drop(index="Rent", errors="ignore")      # fixed rent would flatten the colour scale
    data.columns = pd.to_datetime(data.columns).strftime("%b %Y")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    sns.heatmap(data, annot=True, fmt=",.0f", cmap="Blues", linewidths=2,
                linecolor="#fcfcfb", cbar_kws={"label": f"Amount ({CURRENCY})"}, ax=ax,
                annot_kws={"fontsize": 8.5})
    ax.set_title("Category Spending by Month (excluding rent)")
    ax.set_xlabel("Month")
    ax.set_ylabel("")
    return _save(fig, "06_category_month_heatmap.png")


def create_all_charts(results):
    """Generate every chart from the analysis results dictionary."""
    print("[..] Creating charts")
    paths = [
        plot_category_bar(results["category"]),
        plot_monthly_trend(results["monthly"]),
        plot_payment_pie(results["payment"]),
        plot_daily_trend(results["daily"], results["avg_daily"]),
        plot_budget_vs_actual(results["budget"]),
        plot_category_heatmap(results["matrix"]),
    ]
    print(f"[OK] {len(paths)} charts saved to images/")
    return paths
