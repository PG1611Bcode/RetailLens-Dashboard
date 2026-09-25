<div align="center">

# 🔬 RetailLens
### Executive E-Commerce Analytics Platform

*End-to-end Business Intelligence engineered for consulting-grade insight delivery*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Overview

**RetailLens** is a production-architected Business Intelligence platform that transforms
raw transactional retail data into executive-ready strategic insight. Built across three
engineering phases — automated ETL, analytical SQL backend, and an AI-augmented Streamlit
frontend — it demonstrates the full consulting analytics stack from raw CSV ingestion to
boardroom-ready narrative generation.

The platform ingests **10,000+ rows** of Superstore sales data, runs advanced analytical
SQL (including CTEs and LAG-based Year-over-Year window functions), renders five interactive
Plotly KPI visualizations, and exposes an on-demand **Automated Strategic Analysis engine**
that reads the active dashboard filter state, aggregates live KPIs, and returns a structured
two-paragraph consulting brief in seconds.

> **Target Use Case:** Retail category managers, regional sales directors, and strategy
> consultants who need fast, filter-driven performance diagnosis without manual report
> generation.

---




---

## ✨ Key Features

### 🔄 Phase 1 — Automated ETL Pipeline (`src/ingest_data.py`)

- Ingests raw CSV with full schema validation and column-name normalization to `snake_case`
- Enforces explicit dtype contracts: `sales`/`profit`/`discount` → `float64`,
  `quantity` → `int64`, date columns → `datetime64`
- Deduplicates, null-audits, and logs every transformation step via Python's
  `logging` module — output written to both console and `logs/ingest.log`
- Persists to SQLite via a `sqlalchemy` engine with `chunksize=500` batch writes
- Fully modular: four single-responsibility functions, fully type-hinted with
  Google-style docstrings throughout

### 🧮 Phase 2 — Advanced SQL Analytics Backend (`src/sql_analytics.py`)

- **Query 1 — Regional Profitability:** `SUM`/`ROUND` aggregations with computed
  profit margin percentage per region, ordered by margin descending
- **Query 2 — Sub-Category Ranking:** Top 5 most profitable sub-categories
  including total units sold and average discount applied
- **Query 3 — YoY Sales Growth:** CTE + `LAG()` window function extracts
  year-over-year revenue growth percentage across the full date range, with
  `NULL` correctly preserved for the base year
- **Query 4 — Customer Segmentation:** Two-level CTE aggregation computing
  Average Order Value and Purchase Frequency per customer segment
- All queries fetched via `pd.read_sql_query()` and printed with formatted
  section headers to the terminal

### 📊 Phase 3 — AI-Augmented Streamlit Dashboard (`src/app.py`)

- **Five KPI metric cards** with delta comparison against the unfiltered
  baseline: Total Sales, Total Profit, Profit Margin, Total Orders,
  Average Order Value
- **Three interactive Plotly charts:**
  - Monthly Sales Trend (spline line with area fill)
  - Profit by Region (color-scaled bar chart with margin % on hover)
  - Sales Distribution by Category (donut chart with custom hovertemplate)
- **Sidebar filter panel** with `st.multiselect` widgets for Year, Region,
  and Category — all filters propagate simultaneously to every KPI and chart
- **Theme-adaptive UI:** Zero hardcoded background colors; all CSS uses
  `opacity` and `currentColor` to remain readable in both Streamlit light
  and dark modes natively
- **Collapsible raw data explorer** with one-click CSV export of the current
  filtered view

### 🧠 Automated Strategic Analysis Engine

- Triggered by a single button press directly within the dashboard
- Reads **live filter state** — analysis always reflects exactly what the user
  is currently viewing, never stale or full-dataset aggregates
- Aggregates eight KPIs into a structured data payload: total revenue, profit
  margin, average order value, top and bottom sub-category by profit, leading
  region by sales, and full category profit breakdown
- Returns a structured **two-paragraph brief:** Performance Diagnosis followed
  by two data-grounded Strategic Recommendations
- **Graceful degradation at every failure point:**
  - Missing API key → `st.warning` with setup instructions, no crash
  - API timeout or failure → user-friendly `st.warning`, dashboard unaffected
  - API key is logged only as a boolean presence check — the key string is
    never written to any log file

---

## 🛠️ Tech Stack

| Layer              | Technology                        | Purpose                                      |
|--------------------|-----------------------------------|----------------------------------------------|
| Data Ingestion     | Python 3.10+, Pandas, Pathlib     | CSV loading, cleaning, validation            |
| ORM / DB Layer     | SQLAlchemy, SQLite                | Type-safe DB engine, persistent storage      |
| Analytics          | SQL (CTEs, Window Functions)      | KPI computation, YoY analysis                |
| Frontend           | Streamlit 1.30+                   | Dashboard UI, layout, state management       |
| Visualisation      | Plotly Express 5.x                | Interactive charts, hover templates          |
| AI Layer           | Google Generative AI SDK          | Natural language KPI narrative generation    |
| Config             | python-dotenv                     | Secure API key management via `.env`         |
| Dev Standards      | PEP-8, Type Hints, Google Docs    | Production code quality and maintainability  |

---

## 📁 Project Structure

RetailLens/
├── data/
│ ├── raw/
│ │ └── Superstore.csv # Source dataset (Kaggle)
│ └── processed/
│ └── retaillens.db # SQLite analytical database
├── src/
│ ├── ingest_data.py # Phase 1: ETL pipeline
│ ├── sql_analytics.py # Phase 2: SQL KPI queries
│ └── app.py # Phase 3: Streamlit dashboard
├── notebooks/
│ └── exploration.ipynb # EDA scratch notebook
├── outputs/
│ └── charts/ # Exported chart images
├── logs/
│ └── ingest.log # ETL run logs (auto-generated)
├── .env # API key config (never committed)
├── .gitignore
├── requirements.txt
└── README.md


---

## ⚙️ Local Installation

### Prerequisites

- Python 3.10 or higher
- `pip` package manager
- An AI Studio API key for the Strategic Analysis feature (free tier sufficient)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/RetailLens.git
cd RetailLens
```

### Step 2 — Create and Activate a Virtual Environment

```bash
python -m venv venv
```

On macOS and Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

Create a `.env` file in the project root with the following content:

API_KEY=your_api_key_here


### Step 5 — Run the ETL Pipeline

This step ingests `Superstore.csv`, cleans and validates the data, and loads
it into `data/processed/retaillens.db`.

```bash
python src/ingest_data.py
```

You will see structured log output confirming each pipeline stage. Check
`logs/ingest.log` for the full run record.

### Step 6 — (Optional) Verify SQL Analytics

Runs all four analytical queries and prints formatted results to the terminal.

```bash
python src/sql_analytics.py
```

### Step 7 — Launch the Dashboard

```bash
streamlit run src/app.py
```

Navigate to `http://localhost:8501` in your browser.

---

## 📈 SQL Highlights

RetailLens demonstrates four tiers of analytical SQL proficiency commonly
evaluated in data consulting technical screens.

**Query 1 — Regional Sales and Profit Margin:**

```sql
SELECT
    region,
    ROUND(SUM(sales), 2)                        AS total_sales,
    ROUND(SUM(profit), 2)                        AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2)  AS profit_margin_pct
FROM superstore_sales
GROUP BY region
ORDER BY profit_margin_pct DESC;
```

**Query 3 — Year-over-Year Sales Growth (CTE + LAG Window Function):**

```sql
WITH yearly_sales AS (
    SELECT
        STRFTIME('%Y', order_date)   AS order_year,
        ROUND(SUM(sales), 2)         AS total_sales
    FROM superstore_sales
    GROUP BY order_year
)
SELECT
    order_year,
    total_sales,
    LAG(total_sales) OVER (ORDER BY order_year)  AS prior_year_sales,
    ROUND(
        (
            (total_sales - LAG(total_sales) OVER (ORDER BY order_year))
            / LAG(total_sales) OVER (ORDER BY order_year)
        ) * 100,
    2) AS yoy_growth_pct
FROM yearly_sales
ORDER BY order_year ASC;
```

**Query 4 — Customer Segmentation (Two-Level CTE Aggregation):**

```sql
WITH order_level AS (
    SELECT
        order_id,
        customer_id,
        segment,
        SUM(sales) AS order_value
    FROM superstore_sales
    GROUP BY order_id, customer_id, segment
)
SELECT
    segment,
    COUNT(DISTINCT customer_id)                                    AS unique_customers,
    COUNT(order_id)                                                AS total_orders,
    ROUND(AVG(order_value), 2)                                    AS avg_order_value,
    ROUND(
        CAST(COUNT(order_id) AS FLOAT) / COUNT(DISTINCT customer_id),
    2)                                                             AS purchase_frequency
FROM order_level
GROUP BY segment
ORDER BY avg_order_value DESC;
```

---

## 🔐 Security Notes

- The `.env` file is listed in `.gitignore` and is never committed to version control
- The API key is logged only as a boolean (`True`/`False`) to confirm presence —
  the key string is never written to any log file or printed to the terminal
- All database reads use parameterized queries via SQLAlchemy

---

## 🗺️ Roadmap

- [ ] PostgreSQL migration for multi-user cloud deployment
- [ ] Scheduled ETL automation via Apache Airflow DAG
- [ ] Exportable PDF executive report generation
- [ ] Forecasting module: Prophet-based 90-day sales projection
- [ ] Role-based access control for multi-tenant dashboard views

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">

*Designed with precision. Engineered for insight.*

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/pranay-gupta-93a280355)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-22C55E?style=flat-square)](https://github.com/PG1611Bcode)

</div>

</div>
