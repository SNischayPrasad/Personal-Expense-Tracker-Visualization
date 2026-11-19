# GitHub Upload Guide and Proof-Building Strategy

## 10. GitHub Upload Steps

### Repository details (copy-paste)

| Field | Value |
|-------|-------|
| **Repo name** | `Personal-Expense-Tracker-Visualization` |
| **Description** | Python data analysis project that cleans expense data, analyses spending by category, month and payment method, detects overspending, and generates charts and reports using Pandas, Matplotlib and Seaborn. |
| **Topics / tags** | `python` `pandas` `numpy` `matplotlib` `seaborn` `data-analysis` `data-visualization` `data-cleaning` `expense-tracker` `personal-finance` `budget-tracker` `streamlit` `automation` `eda` `student-project` |

### Step 1: Create the repository on GitHub
1. Go to github.com and click **+** → **New repository**
2. Enter the name and description from the table above
3. Choose **Public**
4. **Do not** tick "Add a README" (you already have one, and ticking it causes a push conflict)
5. Click **Create repository**
6. On the repository page, click the ⚙️ next to "About" and add the topics

### Step 2: Connect your local folder and push
Run these inside the project folder:
```bash
git init
git config user.name "Your Name"            # first time only
git config user.email "you@example.com"     # use your GitHub email
git add .
git status                                  # check that venv/ is NOT listed
git commit -m "Initial commit: project structure and expense tracker pipeline"
git branch -M main
git remote add origin https://github.com/<your-username>/Personal-Expense-Tracker-Visualization.git
git push -u origin main
```
GitHub asks you to sign in through the browser the first time (Git Credential Manager), or you can use a Personal Access Token instead of a password.

### Step 3: Later updates
```bash
git add .
git commit -m "Add budget vs actual chart"
git push
```

### Good commit messages
Use the imperative mood ("Add", "Fix", "Update") and say what changed:
```
Add synthetic expense data generator with seasonality
Add data cleaning: duplicates, invalid amounts, date parsing
Add category-wise and monthly spending analysis
Add category bar chart and payment method pie chart
Add monthly trend and daily rolling-average charts
Add text and CSV report generation
Update README with screenshots and insights
Fix overlapping labels on monthly trend chart
```
Avoid commit messages like `update`, `final`, `final2` or `asdf`.

### Uploading screenshots and outputs
1. Save screenshots in `images/screenshots/` (see the checklist in `PROJECT_GUIDE.md` §13)
2. `git add images/ outputs/ reports/`
3. `git commit -m "Add output charts, reports and screenshots"`
4. `git push`
5. Open the repository and check that the README shows every image. If one is broken, check the file name's capitalisation, because GitHub paths are case-sensitive.

### Make the repo stand out
- Pin it on your GitHub profile (Profile → Customize your pins)
- Add the repository link to your resume and LinkedIn Projects section
- Optional: deploy `app.py` free on Streamlit Community Cloud and add the live link to the README

---

## 12. Proof-Building Strategy (6-Day Plan)

Commit every day. A green contribution graph spread over several days looks far more genuine to recruiters than one giant upload.

| Day | Work | Files to commit | Commit message(s) | Screenshots to save |
|-----|------|-----------------|-------------------|---------------------|
| **Day 1: Setup** | Install Python and Git, create the venv, folders, `requirements.txt`, `.gitignore`, `src/config.py`, a starter README. Create the GitHub repository and push | `requirements.txt`, `.gitignore`, `src/__init__.py`, `src/config.py`, `README.md` | `Initial commit: project structure and configuration` | VS Code folder tree; `pip list` output |
| **Day 2: Dataset** | Write `data_generator.py` and `data_loader.py`, generate the CSV, try `--add` | `src/data_generator.py`, `src/data_loader.py`, `data/expenses_raw.csv` | `Add synthetic expense data generator with seasonality` · `Add CSV loader and manual expense entry` | CSV open in Excel/VS Code showing messy rows |
| **Day 3: Cleaning and analysis** | Write `data_cleaner.py` and `analyzer.py`, explore in the notebook | `src/data_cleaner.py`, `src/analyzer.py`, `notebooks/expense_exploration.ipynb` | `Add data cleaning pipeline with cleaning log` · `Add category, monthly, payment and budget analysis` | Notebook showing before/after cleaning counts |
| **Day 4: Category visuals** | Category bar chart, payment pie chart, budget-vs-actual chart, heatmap | `src/visualizer.py`, `images/01_*.png`, `images/03_*.png`, `images/05_*.png`, `images/06_*.png` | `Add category bar, payment pie and budget charts` | The charts themselves |
| **Day 5: Trend visuals** | Monthly line chart, daily trend with rolling average, `main.py` pipeline | `src/visualizer.py`, `main.py`, `images/02_*.png`, `images/04_*.png` | `Add monthly and daily spending trend charts` · `Add main pipeline entry point with CLI options` | Terminal output of `python main.py` |
| **Day 6: Reports and docs** | `report_generator.py`, final README with screenshots, docs, optional `app.py` | `src/report_generator.py`, `outputs/`, `reports/`, `docs/`, `images/screenshots/`, `app.py` | `Add CSV and text report generation` · `Add Streamlit dashboard` · `Update README with screenshots and insights` | Report file, GitHub repository page, dashboard |

**After Day 6:** write a LinkedIn post. Include 2–3 charts, one surprising insight (for example "weekends cost me 60% more per day"), what you learned, and the repository link.
