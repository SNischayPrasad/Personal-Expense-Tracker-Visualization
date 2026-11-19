# Interview Preparation: Personal Expense Tracker

## HR explanation (30 seconds, non-technical)
> "I built a personal expense tracker in Python. It takes a list of daily expenses, cleans up mistakes in the data, and shows where the money goes: by category, by month and by payment method. It also checks whether spending stayed within budget. It produces six charts and a written report automatically. For example, it showed that weekends cost 60% more per day than weekdays, and that festival and trip months pushed spending above income. The project taught me how to turn raw data into decisions, which is what I want to do in a data or analyst role."

## Technical explanation (60–90 seconds)
> "It's a modular Python pipeline built as a package with separate modules for generation, loading, cleaning, analysis, visualization and reporting, all driven by one `main.py` with argparse options. Because I don't have bank data, I wrote a NumPy-based generator that simulates six months of transactions: Poisson-distributed daily counts with higher weekend rates, category-specific amount ranges and payment probabilities, monthly seasonality, and fixed bills. It also injects realistic errors such as duplicates, `N/A` and negative amounts, inconsistent category casing and invalid dates. The cleaner deduplicates, normalises categories through a lookup map, coerces types with `to_numeric` and `to_datetime(errors='coerce')`, and logs every fix. The analysis uses `groupby`, `pivot_table`, `pct_change` and a 7-day rolling mean on a gap-filled daily series, plus budget-variance flags. Outputs are six Matplotlib/Seaborn charts, seven CSV summaries, a text report and auto-generated insights. There's also an optional Streamlit dashboard that reuses the same functions."

---

## 10 Interview Questions with Strong Answers

### Q1. Explain your project.
**Answer:** "My project is a Personal Expense Tracker with Data Visualization, built in Python with Pandas, NumPy, Matplotlib and Seaborn.

- **Problem:** people lose track of small daily expenses and overshoot their budgets without noticing.
- **Data:** I didn't have real bank data, so I generated six months of realistic synthetic transactions. That came to 382 records across 10 categories and 5 payment methods, with seasonality, weekend effects, and deliberately injected data errors.
- **Pipeline:** load the CSV, then clean it. Cleaning removed 6 duplicates, 10 invalid amounts and 2 bad dates, and fixed 18 category names, leaving 364 clean rows. Then I analyse spending by category, month, payment method and day, compare it with the budget, and generate charts and a report.
- **Results:** total spending was Rs.1.9 lakh. Rent is the largest category at 25%, but Food & Dining is the largest controllable one. Weekends cost 60% more per day. March and May exceeded income because of a festival and a trip. The average savings rate was 11.7%.
- **Outputs:** 6 charts, 7 CSV summaries, a text report, and an optional Streamlit dashboard.

It shows the full analyst workflow: data cleaning, aggregation, visualization and turning numbers into recommendations."

### Q2. Why did you use synthetic data, and how did you make it realistic?
**Answer:** "Real bank data is private and I didn't have access to banking APIs. Synthetic data also lets me control the scenarios and share the project publicly. To make it realistic I:
1. used a Poisson distribution for the number of transactions per day, with a higher rate on weekends
2. gave each category its own frequency weight, amount range and payment-method probabilities (rent mostly by Net Banking, food mostly by UPI)
3. added monthly seasonality (Holi in March, a trip in May) and fixed recurring bills
4. injected real-world errors: duplicates, missing values, `N/A` text, negative amounts, inconsistent capitalisation and invalid dates

I fixed the random seed so the results are reproducible."

### Q3. What data cleaning did you perform, and why in that order?
**Answer:** "In order:
1. **Drop exact duplicates** first, so the same expense isn't counted twice
2. **Normalise text**: strip spaces, lowercase, and map to the official category names (`' food & dining '` becomes `'Food & Dining'`). Unknown names go to `'Other'`
3. **Convert amount** with `pd.to_numeric(errors='coerce')`, so `'N/A'` becomes NaN instead of crashing, then drop NaN and amounts ≤ 0
4. **Parse dates** with an explicit format and `errors='coerce'`, then drop NaT
5. **Fill** missing payment methods with `'Unknown'` (the amount is still valid, so I keep the row) and missing descriptions with a placeholder
6. **Add derived columns**: month, weekday, weekend flag

I count every step in a cleaning log so the report shows exactly what changed. That's important for trust and auditability."

### Q4. Why fill missing payment method but drop missing amounts?
**Answer:** "It depends on what the column is used for. Amount is the core measure: without it the row adds nothing to any total, and guessing it (for example with the mean) would invent spending. A missing payment method only affects one analysis, so I keep the row for category and monthly totals and label the payment method 'Unknown'. That's transparent and loses nothing. Imputation should never create fake financial values."

### Q5. How do you calculate average daily spending, and what's the common mistake?
**Answer:** "Total spending divided by the number of **calendar days** in the period (181 days here), which gives Rs.1,054. The common mistake is to group by date and take the mean, because that only averages days that had transactions and ignores zero-spend days, so it overstates spending. For the daily chart I `reindex` the daily series to the full date range with `fill_value=0` for the same reason."

### Q6. How do you detect overspending?
**Answer:** "At two levels:
1. **Category level:** I pivot spending to month × category and compare each cell with the monthly budget from `config.py`. If actual > budget, the row gets `over_budget = True`. Groceries, for example, went over in 5 of 6 months.
2. **Overall level:** monthly savings = income − spending. A negative value is a deficit, which happened in March and May.

On the budget chart, over-budget bars are red and also labelled 'OVER', so the chart doesn't rely on colour alone."

### Q7. Why did you choose these chart types?
**Answer:** "Each chart answers one question:
- **Horizontal bar** for categories: it's the easiest way to compare magnitudes, and long category names stay readable. Sorted, with value labels.
- **Line chart** for monthly spending: lines show change over time. I added the income level as a dashed reference line.
- **Donut chart** for payment methods: there are only 5–6 parts of one whole, so a pie works. With more categories I'd use a bar.
- **Bars plus a 7-day rolling average** for daily spending: the raw daily values are noisy, and the rolling mean shows the real trend.
- **Grouped bars** for budget vs actual, and a **heatmap** for category × month patterns. I excluded rent from the heatmap because a fixed Rs.8,000 would flatten the colour scale."

### Q8. What is `groupby` vs `pivot_table`, and where did you use each?
**Answer:** "`groupby` splits the data by one or more keys and aggregates. I used it for category totals with `.agg(total='sum', transactions='count', average='mean')`, and for monthly and payment summaries. `pivot_table` reshapes the result into a 2-D grid with one key as rows and another as columns. I used it for the month × category matrix that feeds the budget comparison and the heatmap. `fill_value=0` handles months with no spending in a category, such as Shopping in January."

### Q9. How is your code structured, and why?
**Answer:** "It's a `src/` package with single-responsibility modules: `config`, `data_generator`, `data_loader`, `data_cleaner`, `analyzer`, `visualizer` and `report_generator`. `main.py` only orchestrates them. The benefits are:
- each function takes a DataFrame and returns a result, so it's easy to test and reuse. The Streamlit dashboard reuses the same analysis functions without duplicating code.
- all settings (income, budgets, paths, colours) are in one config file
- `pathlib` paths relative to the project root make it run on Windows, Mac and Linux
- the Matplotlib `Agg` backend lets charts render without a display, so it can run on a server or a scheduler"

### Q10. What would you improve, or how would this work in a real company?
**Answer:**
- "**Real data ingestion:** import bank or UPI statement CSVs with a column-mapping layer
- **Auto-categorisation:** keyword rules on the description first, then a text classifier (TF-IDF + Logistic Regression) trained on labelled history
- **Database:** move from CSV to SQLite or PostgreSQL for multi-user, append-heavy data
- **Forecasting:** predict next month's spending with a moving average or regression and alert early
- **Automation:** schedule a monthly run (cron or Task Scheduler) that emails the PDF report
- **Testing and CI:** pytest unit tests for cleaning rules, plus GitHub Actions

In a company, the same pattern is used for employee expense claims, department cost control and MIS reporting."

---

## Bonus Rapid-Fire Questions

| Question | Short answer |
|----------|-------------|
| What does `errors='coerce'` do? | Converts invalid values to NaN/NaT instead of raising an error |
| `loc` vs `iloc`? | `loc` selects by label or boolean mask; `iloc` by integer position |
| Why `.copy()` in the cleaner? | It avoids changing the caller's DataFrame and prevents SettingWithCopyWarning |
| What is `pct_change()`? | (current − previous) ÷ previous: month-over-month growth |
| Why `to_period('M')`? | It keeps the year with the month, so Jan 2025 ≠ Jan 2026 |
| What is a rolling average? | The mean over a sliding window (7 days here). It smooths noise to show the trend |
| Why a virtual environment? | It isolates project dependencies and makes the project reproducible via `requirements.txt` |
| What's in `.gitignore`? | `venv/`, `__pycache__/`, `.env` (secrets), IDE files |
| Savings rate formula? | (income − spending) ÷ income × 100 |
| Why a fixed random seed? | Same data on every run, so results are reproducible |

## Tips
- Know your numbers: total Rs.1,90,713; 364 clean rows; Rent 25.2%; weekends +60%; savings rate 11.7%.
- Be ready to open the code and explain `clean_data()` line by line. It's the most-asked part.
- Be honest that the data is synthetic, then explain how you made it realistic. Interviewers respect that.
