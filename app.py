"""
app.py - optional interactive dashboard (Streamlit)

Run:  python -m streamlit run app.py
It reuses the SAME cleaning and analysis code as main.py.
"""

import pandas as pd
import streamlit as st

from src.config import RAW_DATA_FILE, CURRENCY, MONTHLY_INCOME
from src.data_generator import generate_expense_data
from src.data_loader import load_expenses
from src.data_cleaner import clean_data
from src import analyzer

st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("Personal Expense Tracker")


@st.cache_data
def get_clean_data():
    if not RAW_DATA_FILE.exists():
        generate_expense_data()
    clean, _ = clean_data(load_expenses())
    return clean


df = get_clean_data()

# ---- Sidebar filters -------------------------------------------------
st.sidebar.header("Filters")
months = sorted(df["month"].unique())
chosen_months = st.sidebar.multiselect("Month", months, default=months)
categories = sorted(df["category"].unique())
chosen_cats = st.sidebar.multiselect("Category", categories, default=categories)

view = df[df["month"].isin(chosen_months) & df["category"].isin(chosen_cats)]
if view.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---- KPI tiles -------------------------------------------------------
top_cat, top_amt = analyzer.highest_spending_category(view)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total spent", f"{CURRENCY}{analyzer.total_spending(view):,.0f}")
k2.metric("Avg daily spend", f"{CURRENCY}{analyzer.average_daily_spending(view):,.0f}")
k3.metric("Top category", top_cat, f"{CURRENCY}{top_amt:,.0f}", delta_color="off")
k4.metric("Transactions", f"{len(view):,}")

# ---- Charts ----------------------------------------------------------
left, right = st.columns(2)
with left:
    st.subheader("Category-wise spending")
    st.bar_chart(analyzer.category_summary(view).set_index("category")["total"])
with right:
    st.subheader("Monthly spending vs income")
    monthly = analyzer.monthly_summary(view).set_index("month")
    st.line_chart(monthly[["total_spent", "income"]])

left, right = st.columns(2)
with left:
    st.subheader("Payment methods")
    st.bar_chart(analyzer.payment_summary(view).set_index("payment_method")["total"])
with right:
    st.subheader("Daily spending (7-day average)")
    st.line_chart(analyzer.daily_spending(view).set_index("date")["rolling_7d_avg"])

st.subheader("Over-budget months")
budget = analyzer.budget_vs_actual(view)
st.dataframe(budget[budget["over_budget"]], width="stretch", hide_index=True)

st.subheader("Raw transactions")
st.dataframe(view.sort_values("date", ascending=False), width="stretch", hide_index=True)
st.caption(f"Assumed monthly income: {CURRENCY}{MONTHLY_INCOME:,}. Synthetic data for demo purposes.")
