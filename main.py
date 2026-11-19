"""
main.py
-------
Entry point of the Personal Expense Tracker.

Usage
-----
    python main.py             # run full pipeline (creates data if missing)
    python main.py --generate  # re-create the synthetic dataset, then run
    python main.py --add       # add a manual expense entry, then run

Pipeline:
    data entry -> storage (CSV) -> cleaning -> category analysis ->
    monthly analysis -> visualization -> report generation
"""

import argparse

from src.config import RAW_DATA_FILE, CURRENCY
from src.data_generator import generate_expense_data
from src.data_loader import load_expenses, add_expense_interactive
from src.data_cleaner import clean_data
from src.analyzer import run_full_analysis, generate_insights
from src.visualizer import create_all_charts
from src.report_generator import save_csv_outputs, save_text_report


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Personal Expense Tracker with Data Visualization")
    parser.add_argument("--generate", action="store_true", help="re-create the synthetic dataset")
    parser.add_argument("--add", action="store_true", help="add a manual expense before analysis")
    args = parser.parse_args()

    print_header("PERSONAL EXPENSE TRACKER WITH DATA VISUALIZATION")

    # Step 1: Data entry / creation
    if args.generate or not RAW_DATA_FILE.exists():
        generate_expense_data()
    if args.add:
        add_expense_interactive()

    # Step 2: Load
    raw_df = load_expenses()

    # Step 3: Clean
    clean_df, cleaning_log = clean_data(raw_df)

    # Step 4 + 5: Category, monthly, payment, daily, budget analysis
    results = run_full_analysis(clean_df)
    insights = generate_insights(results)

    # Step 6: Visualize
    create_all_charts(results)

    # Step 7: Reports
    save_csv_outputs(clean_df, results)
    save_text_report(results, insights, cleaning_log)

    # Console summary
    c = CURRENCY
    print_header("QUICK SUMMARY")
    print(f"Period              : {results['start']:%d %b %Y} - {results['end']:%d %b %Y}")
    print(f"Total spending      : {c}{results['total']:,.2f}")
    print(f"Average daily spend : {c}{results['avg_daily']:,.2f}")
    print(f"Highest category    : {results['highest_category']} ({c}{results['highest_category_amount']:,.2f})")

    print("\nMonthly spending:")
    for _, r in results["monthly"].iterrows():
        print(f"  {r['month']}  {c}{r['total_spent']:>10,.2f}   savings {c}{r['savings']:>9,.2f}")

    print_header("KEY INSIGHTS")
    for i, text in enumerate(insights, start=1):
        print(f"{i:>2}. {text}")
    print("\nDone! Check the images/, outputs/ and reports/ folders.\n")


if __name__ == "__main__":
    main()
