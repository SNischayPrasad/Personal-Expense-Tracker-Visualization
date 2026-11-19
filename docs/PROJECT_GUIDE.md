# Project Guide: Personal Expense Tracker with Data Visualization

The full study guide for this project: concept, tech choices, architecture, the phase-wise build, installation, how the simulation works, how to run it, and which screenshots to capture.

---

## 1. Project Explanation

### What is a Personal Expense Tracker?
A system that records every expense (date, category, amount, payment method, note) and then summarises it, so you can see where your money goes.

### What problem does it solve?
People remember big expenses (rent, a phone) but forget small, frequent ones (Rs.80 coffee, Rs.150 auto ride). Those small expenses often add up to more than the big ones. Without tracking, budgets fail quietly, savings fall short, and nobody knows why.

### Who is it useful for?

| User | How it helps |
|------|-------------|
| Students | Make pocket money or a stipend last the whole month and spot food-delivery overspending |
| Employees | Plan monthly savings and investments (SIP), track EMIs and bills |
| Families | Share a household budget, plan groceries, school fees and festival spending |
| Freelancers | Irregular income needs tighter control; separate business and personal costs for taxes |
| Small businesses | Track operating costs, find cost leaks, keep records for accounting/GST |

### How tracking helps
- **Budgeting**: set a limit per category, then compare against actual spending (variance)
- **Savings**: savings = income minus spending. Tracking shows the savings rate every month
- **Spending control**: alerts when a category goes over budget
- **Financial planning**: seasonal patterns (festivals, trips) show which months need extra money set aside

### Simple explanation
> "I write down every expense in a sheet. My Python program reads that sheet, fixes mistakes, adds everything up by category and by month, draws charts, and writes a short report that tells me where I overspent and how much I saved."

### Technical explanation
> "A modular Python ETL and analytics pipeline. Raw CSV records are ingested with Pandas, validated and cleaned (deduplication, type coercion with `pd.to_numeric(errors='coerce')`, categorical normalisation, datetime parsing), enriched with derived features (month, weekday, weekend flag), then aggregated with `groupby` and `pivot_table` into category, monthly, payment-method, daily (with a 7-day rolling mean) and budget-variance views. Results are rendered with Matplotlib/Seaborn, exported as CSV and text reports, and converted into rule-based natural-language insights."

### Workflow
```
Expense data entry ─► Data storage ─► Data cleaning ─► Category-wise analysis
   (synthetic /         (CSV file)      (duplicates,        (groupby category)
    manual --add)                         types, text)               │
                                                                     ▼
       Report generation ◄── Visualization ◄── Monthly analysis
       (TXT + CSV)            (6 PNG charts)     (groupby month, savings, budget)
```

---

## 2. Tech Stack Options

| | Option A: Easy | Option B: Intermediate ✅ | Option C: Advanced |
|---|---|---|---|
| **Tools** | Python, `csv` module, Matplotlib | Python, Pandas, NumPy, Matplotlib, Seaborn, CSV, `datetime`, `pathlib` (+ optional Streamlit) | Option B + SQLite/PostgreSQL, Streamlit/Plotly dashboard, scikit-learn (auto-categorise, forecast), pytest, Docker, CI |
| **Difficulty** | ⭐ Beginner | ⭐⭐ Beginner to intermediate | ⭐⭐⭐⭐ Advanced |
| **Time** | 1–2 days | 5–7 days | 3–4 weeks |
| **Output** | Totals printed in the terminal plus one or two basic charts | Clean dataset, 6 charts, CSV summaries, text report, insights, optional dashboard | Web app with database, login, predictions, deployed online |

**Best for students: Option B.** It uses the libraries every Data Analyst and Python job description lists (Pandas, NumPy, Matplotlib, Seaborn), it is finishable in a week, and the optional Streamlit dashboard gives you an easy upgrade path to Option C later. This repository implements Option B.

---

## 3. Project Architecture

### Input (one row per expense)

| Field | Example | Type |
|-------|---------|------|
| `date` | 2026-03-14 | date (YYYY-MM-DD) |
| `category` | Food & Dining | text (one of 10 categories) |
| `amount` | 245 | number (Rs.) |
| `payment_method` | UPI | text (UPI / Debit Card / Credit Card / Cash / Net Banking) |
| `description` | Swiggy order | text |

### Architecture diagram
```
┌──────────────────────────────── INPUT ────────────────────────────────┐
│  data_generator.py (synthetic)      data_loader.add_expense (manual)  │
│                  └──────────────┬──────────────┘                      │
│                                 ▼                                     │
│                     data/expenses_raw.csv                             │
└─────────────────────────────────┬─────────────────────────────────────┘
                                  ▼
┌────────────────────────────── PROCESSING ─────────────────────────────┐
│  data_loader.load_expenses()   → read CSV, validate columns           │
│  data_cleaner.clean_data()     → dedupe, fix text, numeric amount,    │
│                                  parse dates, add month/weekday       │
│  analyzer.run_full_analysis()  → category | monthly | payment |       │
│                                  daily + rolling | budget vs actual | │
│                                  highest category | top expenses      │
│  analyzer.generate_insights()  → plain-English findings               │
└─────────────────────────────────┬─────────────────────────────────────┘
                                  ▼
┌──────────────────────────────── OUTPUT ───────────────────────────────┐
│  visualizer.py        → images/01..06_*.png  (6 charts)               │
│  report_generator.py  → outputs/*.csv  (clean data + 6 summaries)     │
│                       → reports/expense_summary_report.txt            │
│  main.py              → terminal summary   |   app.py → dashboard     │
└───────────────────────────────────────────────────────────────────────┘
```
`config.py` feeds settings (paths, income, budgets, colours) to every module.

### Data flow
1. **Entry**: records come from the generator or from manual `--add` entries and are appended to `expenses_raw.csv`.
2. **Load**: Pandas reads the CSV. Column names are normalised and required columns are checked.
3. **Clean**: bad rows are removed or fixed, and each step is counted in a `log` dictionary.
4. **Enrich**: `month`, `month_name`, `day_of_week` and `is_weekend` columns are added.
5. **Analyse**: each analysis function takes the clean DataFrame and returns a small summary table.
6. **Output**: the summaries feed the charts, the CSV files, the text report and the insights.

---

## 4. Implementation Plan

| Phase | What to do | Why | Expected output | Common beginner mistakes |
|-------|-----------|-----|-----------------|--------------------------|
| **1. Setup** | Install Python 3.10+, VS Code, Git. Create a venv and install the libraries | Isolated, reproducible environment | `python --version` works and the venv is active | Forgetting to activate the venv; installing into the wrong Python |
| **2. Folders** | Create `data/ src/ outputs/ images/ reports/ docs/ notebooks/` and add `src/__init__.py` | Recruiters judge structure; modules can import each other | Folder tree as in the README | Putting all code in one file; spaces in folder names |
| **3. Expense CSV** | Write `data_generator.py`: daily random transactions, fixed bills, seasonality, injected errors | No real bank data, but you still need realistic data | `data/expenses_raw.csv` with about 380 rows | Perfectly clean fake data (nothing to clean); no random seed (results change every run) |
| **4. Loading** | `pd.read_csv`, normalise column names, check required columns | Fail early with a clear message | "Loaded 382 records" | Hard-coded Windows paths like `C:\Users\...`; use `pathlib` |
| **5. Cleaning** | Drop duplicates, strip and map categories, `to_numeric(errors='coerce')`, drop amounts ≤ 0, `to_datetime`, fill missing values | Garbage in means garbage out | 382 → 364 rows plus a cleaning log | Using `dropna()` on everything (loses good rows); forgetting `.copy()` (SettingWithCopyWarning) |
| **6. Category analysis** | `groupby('category').agg(...)`, % share, highest category | Shows where the money goes | `category_summary.csv` | Counting rows instead of summing amount |
| **7. Monthly trend** | Group by month, `pct_change`, savings and savings rate, budget vs actual | Shows trends and overspending | `monthly_summary.csv`, `budget_vs_actual.csv` | Grouping by month number only (mixes Jan 2025 and Jan 2026); use `to_period('M')` |
| **8. Visualization** | Bar, line, pie, daily trend, budget chart, heatmap | Charts communicate faster than tables | 6 PNG files in `images/` | No titles or axis labels; overlapping labels; calling `plt.show()` in scripts and forgetting `savefig` |
| **9. Reports** | Write CSV summaries and a formatted text report | Shareable, automatable output | `reports/expense_summary_report.txt` | Not using `encoding='utf-8'`; printing results but never saving them |
| **10. GitHub** | `git init`, commit, push, README with screenshots | Proof of work | Public repository | Committing `venv/`; one giant commit; README with no images |

---

## 5. Folder Structure Explained

| Folder / file | Purpose |
|---------------|---------|
| `data/` | Raw input. `expenses_raw.csv` is the messy source data and is never edited by the pipeline (except manual `--add` appends) |
| `notebooks/` | Jupyter notebook for step-by-step exploration. Good for showing your thinking process |
| `src/` | All reusable Python code, split by responsibility (generate → load → clean → analyse → visualize → report) |
| `outputs/` | Machine-readable results: cleaned dataset and summary CSVs (can be opened in Excel or Power BI) |
| `images/` | Generated charts plus a `screenshots/` subfolder for your manual screenshots |
| `reports/` | Human-readable final report |
| `docs/` | This guide, the GitHub guide and interview preparation |
| `README.md` | The project's front page on GitHub |
| `requirements.txt` | Library list so anyone can install with one command |
| `.gitignore` | Stops `venv/`, `__pycache__/` and secrets from being uploaded |
| `main.py` | Single entry point that runs everything |
| `app.py` | Optional Streamlit dashboard |

---

## 6. Installation Guide

### Step 1: Install Python
- **Windows**: download Python 3.10+ from python.org. On the first installer screen, tick **"Add python.exe to PATH"**.
- **Mac**: `brew install python` (or the python.org installer).
- Check: `python --version` (on Mac, use `python3 --version`).

### Step 2: Install Git and VS Code
git-scm.com and code.visualstudio.com (in VS Code, add the "Python" extension).

### Step 3: Virtual environment

**Windows (PowerShell)**
```powershell
cd Personal-Expense-Tracker-Visualization
python -m venv venv
venv\Scripts\activate
```
If PowerShell blocks activation, run this once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Mac / Linux**
```bash
cd Personal-Expense-Tracker-Visualization
python3 -m venv venv
source venv/bin/activate
```
When the venv is active, `(venv)` appears at the start of the prompt.

### Step 4: Install libraries
```bash
pip install -r requirements.txt
```
or, for the core libraries only:
```bash
pip install pandas numpy matplotlib seaborn
```

| Library | Why |
|---------|-----|
| pandas | Tables (DataFrames): read CSV, clean, group |
| numpy | Random numbers for synthetic data |
| matplotlib | Draw and save charts |
| seaborn | Nicer styling and heatmap |
| streamlit *(optional)* | Web dashboard |
| jupyter *(optional)* | Run the notebook |

---

## 7. Full Project Code

All code is in `src/`, `main.py` and `app.py`, and every file is commented line by line. Read the files in this order:

1. [`src/config.py`](../src/config.py): settings (income Rs.36,000, budgets per category, paths, colours)
2. [`src/data_generator.py`](../src/data_generator.py): synthetic dataset creation and dirty-data injection
3. [`src/data_loader.py`](../src/data_loader.py): CSV loading and manual expense entry
4. [`src/data_cleaner.py`](../src/data_cleaner.py): cleaning and date conversion
5. [`src/analyzer.py`](../src/analyzer.py): category, monthly, payment, daily, budget, highest category, average daily spending, insights
6. [`src/visualizer.py`](../src/visualizer.py): bar, line, pie, daily trend, budget vs actual and heatmap charts
7. [`src/report_generator.py`](../src/report_generator.py): CSV and text report
8. [`main.py`](../main.py): runs everything in order
9. [`app.py`](../app.py): optional Streamlit dashboard

How each requirement is covered:

| Requirement | Function |
|-------------|----------|
| Synthetic dataset | `data_generator.generate_expense_data()` |
| CSV loading | `data_loader.load_expenses()` |
| Data cleaning / date conversion | `data_cleaner.clean_data()` |
| Category-wise analysis | `analyzer.category_summary()` |
| Monthly analysis / total monthly spending | `analyzer.monthly_summary()` |
| Payment method analysis | `analyzer.payment_summary()` |
| Highest spending category | `analyzer.highest_spending_category()` |
| Average daily spending | `analyzer.average_daily_spending()` |
| Overspending | `analyzer.budget_vs_actual()` |
| Category bar chart | `visualizer.plot_category_bar()` |
| Monthly line chart | `visualizer.plot_monthly_trend()` |
| Payment pie chart | `visualizer.plot_payment_pie()` |
| Daily trend chart | `visualizer.plot_daily_trend()` |
| Report (CSV + TXT) | `report_generator.save_csv_outputs()`, `save_text_report()` |

---

## 8. Virtual Simulation: How the Tracker Mimics Real Life

| Real-life step | How the simulation does it |
|---------------|---------------------------|
| **Expense records are created** | For every day from 1 Jan to 30 Jun 2026, the generator draws a random number of transactions (Poisson distribution: about 1.6 on weekdays and 2.3 on weekends, because people spend more on weekends). Fixed bills (rent Rs.8,000 on the 1st, Spotify, Netflix, electricity, Wi-Fi, mobile recharge) are added every month. One-off events (Holi shopping, Goa trip, dentist visit) make the story realistic. |
| **Categories are assigned** | Each transaction's category is picked with weighted probability (Food & Dining is most frequent, Health least). Each category has its own amount range and its own payment-method probabilities (rent mostly Net Banking, food mostly UPI, shopping often Credit Card). |
| **Real-world mess** | 2% duplicate entries, missing amounts, `N/A` text, negative amounts, lowercase or space-padded category names, missing payment methods, and two `"unknown"` dates are injected, just like careless manual entry. |
| **Spending is grouped** | `groupby('category')`, `groupby('month')`, `groupby('payment_method')`, `groupby('date')` |
| **Monthly trends are calculated** | Total per month, then `pct_change()` for month-over-month %, then savings = income − spending and savings rate = savings ÷ income |
| **Overspending is identified** | (1) Each month × category is compared with `MONTHLY_BUDGET`. Actual > budget gives `over_budget = True`. (2) Months where total spending > income are flagged as a deficit |
| **Charts are generated** | Matplotlib draws the charts with the `Agg` backend (no window), and `savefig(dpi=150)` writes the PNG files |
| **Final insights** | `generate_insights()` reads the summary tables and fills sentence templates, for example "Peak month was 2026-05 (Rs.39,066)" |

The random seed is fixed (`RANDOM_SEED = 42`), so everyone gets the same dataset and the same results. Change the seed in `config.py` to simulate a different person.

To simulate your own life, edit `MONTHLY_INCOME` and `MONTHLY_BUDGET` in `config.py`, or log your real expenses for two weeks with `python main.py --add`.

**Upload to GitHub:** all 6 charts in `images/`, `reports/expense_summary_report.txt`, the `outputs/*.csv` files, and your screenshots in `images/screenshots/`.

---

## 9. How to Run the Project

```bash
python main.py              # full pipeline
python main.py --generate   # fresh synthetic data
python main.py --add        # manual entry, then analysis
python -m streamlit run app.py   # optional dashboard (opens http://localhost:8501)
```

### Expected terminal output
```
============================================================
  PERSONAL EXPENSE TRACKER WITH DATA VISUALIZATION
============================================================
[OK] Synthetic dataset created: expenses_raw.csv (382 rows)
[OK] Loaded 382 records from expenses_raw.csv
[OK] Data cleaned: 382 -> 364 rows (18 removed)
[..] Creating charts
   saved images/01_category_spending_bar.png
   saved images/02_monthly_spending_trend.png
   saved images/03_payment_method_pie.png
   saved images/04_daily_spending_trend.png
   saved images/05_budget_vs_actual.png
   saved images/06_category_month_heatmap.png
[OK] 6 charts saved to images/
[OK] Summary CSV files saved to outputs/
[OK] Text report saved to reports/expense_summary_report.txt

============================================================
  QUICK SUMMARY
============================================================
Period              : 01 Jan 2026 - 30 Jun 2026
Total spending      : Rs.190,713.00
Average daily spend : Rs.1,053.66
Highest category    : Rent (Rs.48,000.00)

Monthly spending:
  2026-01  Rs. 20,729.00   savings Rs.15,271.00
  2026-02  Rs. 31,798.00   savings Rs. 4,202.00
  2026-03  Rs. 36,514.00   savings Rs.  -514.00
  2026-04  Rs. 34,813.00   savings Rs. 1,187.00
  2026-05  Rs. 39,066.00   savings Rs.-3,066.00
  2026-06  Rs. 27,793.00   savings Rs. 8,207.00
  ... followed by 10 key insights
```
(The first line, "Synthetic dataset created", only appears on the first run or with `--generate`.)

### Generated files

| File | Content |
|------|---------|
| `images/01_category_spending_bar.png` | Total and % share per category |
| `images/02_monthly_spending_trend.png` | Monthly spending vs income line |
| `images/03_payment_method_pie.png` | Donut chart of payment methods |
| `images/04_daily_spending_trend.png` | Daily bars and 7-day rolling average |
| `images/05_budget_vs_actual.png` | Average monthly actual vs budget, over-budget in red |
| `images/06_category_month_heatmap.png` | Category × month spending grid |
| `outputs/expenses_clean.csv` | Cleaned dataset with derived columns |
| `outputs/category_summary.csv`, `monthly_summary.csv`, `payment_method_summary.csv`, `daily_spending.csv`, `budget_vs_actual.csv`, `category_month_matrix.csv` | Summary tables |
| `reports/expense_summary_report.txt` | Full formatted report (cleaning log, summaries, overspending list, top expenses, insights) |

### Sample insight
> "Weekend days average Rs.1,438 vs Rs.899 on weekdays (+60%)." A weekend cap of Rs.1,000 a day would save roughly Rs.3,700 a month (about 8.6 weekend days × Rs.438).

---

## 13. Screenshots / Outputs Checklist

Save manual screenshots in `images/screenshots/` with these exact names, so the README links keep working if you add them:

| # | Capture | How | File name |
|---|---------|-----|-----------|
| 1 | Project folder | VS Code Explorer panel with all folders expanded | `01_project_folder.png` |
| 2 | Expense dataset preview | Open `data/expenses_raw.csv` in Excel or VS Code (show messy rows), or run the notebook's `raw.head(10)` | `02_dataset_preview.png` |
| 3 | Terminal output | Run `python main.py` and capture the full terminal (also saved as text in `outputs/terminal_output.txt`) | `03_terminal_output.png` |
| 4 | Category-wise bar chart | Auto-generated | `images/01_category_spending_bar.png` |
| 5 | Monthly line chart | Auto-generated | `images/02_monthly_spending_trend.png` |
| 6 | Payment method pie chart | Auto-generated | `images/03_payment_method_pie.png` |
| 7 | Daily trend chart | Auto-generated | `images/04_daily_spending_trend.png` |
| 8 | Final summary report | Open `reports/expense_summary_report.txt` in VS Code | `04_summary_report.png` |
| 9 | GitHub repo preview | Your repository home page after the push (README rendered with charts) | `05_github_repo.png` |
| Bonus | Streamlit dashboard | Browser at `localhost:8501` | `06_streamlit_dashboard.png` |

Windows screenshot shortcut: **Win + Shift + S**. On Mac: **Cmd + Shift + 4**.
