"""
report_generator.py
-------------------
Saves analysis results as CSV files (outputs/) and a readable
text summary report (reports/expense_summary_report.txt).
"""

from datetime import datetime

from src.config import OUTPUT_DIR, REPORTS_DIR, REPORT_FILE, CLEAN_DATA_FILE, CURRENCY, MONTHLY_INCOME


def save_csv_outputs(clean_df, results):
    """Write cleaned data and every summary table to CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(CLEAN_DATA_FILE, index=False)
    results["category"].to_csv(OUTPUT_DIR / "category_summary.csv", index=False)
    results["monthly"].to_csv(OUTPUT_DIR / "monthly_summary.csv", index=False)
    results["payment"].to_csv(OUTPUT_DIR / "payment_method_summary.csv", index=False)
    results["daily"].to_csv(OUTPUT_DIR / "daily_spending.csv", index=False)
    results["budget"].to_csv(OUTPUT_DIR / "budget_vs_actual.csv", index=False)
    results["matrix"].to_csv(OUTPUT_DIR / "category_month_matrix.csv")
    print("[OK] Summary CSV files saved to outputs/")


def _line(char="=", width=64):
    return char * width


def build_text_report(results, insights, cleaning_log):
    """Create the full text report as one string."""
    c = CURRENCY
    lines = [
        _line(),
        "        PERSONAL EXPENSE TRACKER - SUMMARY REPORT",
        _line(),
        f"Generated on : {datetime.now():%Y-%m-%d %H:%M}",
        f"Period       : {results['start']:%d %b %Y} to {results['end']:%d %b %Y}",
        f"Transactions : {results['transactions']}",
        "",
        "1. DATA CLEANING",
        _line("-"),
        f"Raw rows                 : {cleaning_log['raw_rows']}",
        f"Duplicates removed       : {cleaning_log['duplicates_removed']}",
        f"Invalid amounts removed  : {cleaning_log['invalid_amounts_removed']}",
        f"Invalid dates removed    : {cleaning_log['invalid_dates_removed']}",
        f"Category names fixed     : {cleaning_log['categories_fixed']}",
        f"Missing payment -> Unknown: {cleaning_log['missing_payment_filled']}",
        f"Clean rows               : {cleaning_log['clean_rows']}",
        "",
        "2. OVERALL SUMMARY",
        _line("-"),
        f"Total spending           : {c}{results['total']:,.2f}",
        f"Average daily spending   : {c}{results['avg_daily']:,.2f}",
        f"Average monthly spending : {c}{results['monthly']['total_spent'].mean():,.2f}",
        f"Monthly income (assumed) : {c}{MONTHLY_INCOME:,.2f}",
        f"Total savings            : {c}{results['monthly']['savings'].sum():,.2f}",
        f"Highest category         : {results['highest_category']} ({c}{results['highest_category_amount']:,.2f})",
        "",
        "3. CATEGORY-WISE SPENDING",
        _line("-"),
        f"{'Category':<16}{'Total':>14}{'Txns':>7}{'Avg':>11}{'Share':>9}",
    ]
    for _, r in results["category"].iterrows():
        lines.append(f"{r['category']:<16}{c + format(r['total'], ',.0f'):>14}"
                     f"{int(r['transactions']):>7}{c + format(r['average'], ',.0f'):>11}{r['share_pct']:>8.1f}%")

    lines += ["", "4. MONTHLY SUMMARY", _line("-"),
              f"{'Month':<10}{'Spent':>13}{'Change':>9}{'Savings':>13}{'Save %':>9}"]
    for _, r in results["monthly"].iterrows():
        chg = "   -" if r["change_pct"] != r["change_pct"] else f"{r['change_pct']:+.1f}%"
        lines.append(f"{r['month']:<10}{c + format(r['total_spent'], ',.0f'):>13}{chg:>9}"
                     f"{c + format(r['savings'], ',.0f'):>13}{r['savings_rate_pct']:>8.1f}%")

    lines += ["", "5. PAYMENT METHOD ANALYSIS", _line("-")]
    for _, r in results["payment"].iterrows():
        lines.append(f"{r['payment_method']:<14}{c + format(r['total'], ',.0f'):>13}"
                     f"{int(r['transactions']):>6} txns{r['share_pct']:>8.1f}%")

    overs = results["budget"][results["budget"]["over_budget"]]
    lines += ["", "6. OVERSPENDING (month-category over budget)", _line("-")]
    if overs.empty:
        lines.append("None - all categories stayed within budget.")
    for _, r in overs.iterrows():
        lines.append(f"{r['month']}  {r['category']:<15} spent {c}{r['actual']:,.0f} "
                     f"vs budget {c}{r['budget']:,.0f}  (over by {c}{-r['difference']:,.0f})")

    lines += ["", "7. TOP 5 LARGEST EXPENSES (excluding rent)", _line("-")]
    for _, r in results["top"].iterrows():
        lines.append(f"{r['date']:%Y-%m-%d}  {r['category']:<15}{c + format(r['amount'], ',.0f'):>9}  {r['description']}")

    lines += ["", "8. KEY INSIGHTS", _line("-")]
    lines += [f"{i}. {text}" for i, text in enumerate(insights, start=1)]
    lines += ["", _line()]
    return "\n".join(lines)


def save_text_report(results, insights, cleaning_log):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = build_text_report(results, insights, cleaning_log)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"[OK] Text report saved to reports/{REPORT_FILE.name}")
    return report
