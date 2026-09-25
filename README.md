<div align="center">

<img src="assets/logo.png" alt="RetailLens Logo" width="120" />

# 🔬 RetailLens
### Executive E-Commerce Analytics Platform

*End-to-end Business Intelligence engineered for consulting-grade insight delivery*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Gemini](https://img.shields.io/badge/Gemini_API-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

![RetailLens Dashboard Preview](assets/dashboard_preview.png)

<br/>

[**Live Demo**](https://your-demo-link.streamlit.app) · [**View ETL Source**](src/ingest_data.py) · [**View SQL Analytics**](src/sql_analytics.py) · [**Report a Bug**](issues)

</div>

---

## 📌 Overview

**RetailLens** is a production-architected Business Intelligence platform that transforms raw transactional retail data into executive-ready strategic insight. Built across three engineering phases — automated ETL, analytical SQL backend, and an AI-augmented Streamlit frontend — it demonstrates the full consulting analytics stack from raw CSV ingestion to boardroom-ready narrative generation.

The platform ingests **10,000+ rows** of Superstore sales data, runs advanced analytical SQL (including CTEs and LAG-based Year-over-Year window functions), renders five interactive Plotly KPI visualizations, and exposes an on-demand **AI Executive Summary engine** powered by the Gemini 1.5 Flash API. The AI engine reads the active dashboard filter state, aggregates live KPIs, and returns a 180-word two-paragraph strategic consulting brief — in under three seconds.

> **Target Use Case:** Retail category managers, regional sales directors, and strategy consultants who need fast, filter-driven performance diagnosis without manual report generation.

---

## 🏗️ System Architecture

┌─────────────────────────────────────────────────────────────────┐
│ RetailLens Platform │
├───────────────────┬─────────────────────┬───────────────────────┤
│ INGESTION LAYER │ ANALYTICS LAYER │ PRESENTATION LAYER │
│ │ │ │
│ Superstore.csv │ retaillens.db │ Streamlit App │
│ (Kaggle, 10k+) │ (SQLite) │ (src/app.py) │
│ │ │ │ │ │ │
│ ▼ │ ▼ │ ▼ │
│ ingest_data.py │ sql_analytics.py │ Plotly Charts (5x) │
│ ┌─────────────┐ │ ┌──────────────┐ │ KPI Metric Cards │
│ │ load_raw() │ │ │ Regional KPI │ │ Sidebar Filters │
│ │ clean_cols()│ │ │ Top SubCats │ │ │ │
│ │ validate() │ │ │ YoY Growth │ │ ▼ │
│ │ push_sql() │ │ │ Seg. Analysis│ │ Gemini 1.5 Flash │
│ └─────────────┘ │ └──────────────┘ │ AI Summary Engine │
│ │ │ │
│ pandas · pathlib │ CTEs · LAG() · │ google-generativeai │
│ sqlalchemy │ Window Functions │ python-dotenv │
└───────────────────┴─────────────────────┴───────────────────────┘


---

## ✨ Key Features

### 🔄 Phase 1 — Automated ETL Pipeline (`src/ingest_data.py`)
- Ingests raw CSV with full schema validation and column-name normalization to `snake_case`
- Enforces explicit dtype contracts: `sales`/`profit`/`discount` → `float64`, `quantity` → `int64`, date columns → `datetime64`
- Deduplicates, null-audits, and logs every transformation step via Python's `logging` module
- Persists to SQLite via a `sqlalchemy` engine with `chunksize=500` batch writes
- Fully modular: four single-responsibility functions with type hints and Google-style docstrings

### 🧮 Phase 2 — Advanced SQL Analytics Backend (`src/sql_analytics.py`)
- **Query 1 — Regional Profitability:** `SUM`/`ROUND` aggregations with computed profit margin percentage per region
- **Query 2 — Sub-Category Ranking:** Top 5 most profitable sub-categories including average discount applied
- **Query 3 — YoY Sales Growth:** CTE + `LAG()` window function extracts year-over-year revenue growth percentage across the full date range, with `NULL` preserved for the base year
- **Query 4 — Customer Segmentation:** Two-level CTE aggregation computing Average Order Value and Purchase Frequency per customer segment
- All queries fetched via `pd.read_sql_query()` and printed with formatted terminal headers

### 📊 Phase 3 — AI-Augmented Streamlit Dashboard (`src/app.py`)
- **Five KPI metric cards** with delta comparison against unfiltered baseline (Total Sales, Total Profit, Profit Margin, Total Orders, Average Order Value)
- **Three Plotly charts:** Monthly Sales Trend (spline + area fill), Profit by Region (color-scaled bar), Sales Distribution by Category (donut)
- **Sidebar filter panel** with `st.multiselect` widgets for Year, Region, and Category — all filters dynamically propagate to every KPI and chart simultaneously
- **Theme-adaptive UI:** Zero hardcoded background colors; all CSS uses `opacity` and `currentColor` to remain readable in both Streamlit light and dark modes
- **Collapsible raw data explorer** with one-click CSV export of the current filtered view

### 🧠 AI Executive Summary Engine
- Triggered by a single "Generate AI Executive Summary" button in the dashboard
- Reads **live filter state** — the AI never summarizes stale or full data, only what the user is currently viewing
- Aggregates eight KPIs into a structured data payload: revenue, margin, AOV, top/bottom sub-category, top region, full category profit breakdown
- Sends payload to **Gemini 1.5 Flash** with a `system_instruction` persona: *Senior Retail Strategy Consultant, 15 years Fortune 500 advisory experience*
- Returns a **180-word, two-paragraph structured brief**: Performance Diagnosis + two data-grounded Strategic Recommendations
- Graceful degradation: missing API key → `st.warning` guidance; API failure → user-friendly error; app never crashes

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Data Ingestion** | Python 3.10+, Pandas, Pathlib | CSV loading, cleaning, validation |
| **ORM / DB Layer** | SQLAlchemy, SQLite | Type-safe DB engine, persistent storage |
| **Analytics** | SQL (CTEs, Window Functions) | KPI computation, YoY analysis |
| **Frontend** | Streamlit 1.30+ | Dashboard UI, layout, state management |
| **Visualisation** | Plotly Express 5.x | Interactive charts, hover templates |
| **AI Layer** | Google Generative AI SDK, Gemini 1.5 Flash | Natural language KPI narrative |
| **Config** | python-dotenv | Secure API key management via `.env` |
| **Dev Standards** | PEP-8, Type Hints, Google Docstrings | Production code quality |

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
│ └── ingest.log # ETL run logs
├── assets/
│ └── logo.png
├── .env # GEMINI_API_KEY (never committed)
├── .gitignore
├── requirements.txt
└── README.md


---

## ⚙️ Local Installation

### Prerequisites
- Python 3.10 or higher
- `pip` package manager
- A [Google AI Studio](https://aistudio.google.com) API key (free tier sufficient)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/RetailLens.git
cd RetailLens
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
# Create a .env file in the project root
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

**5. Run the ETL pipeline**
```bash
# Ingests Superstore.csv → cleans → loads into retaillens.db
python src/ingest_data.py
```

**6. (Optional) Verify SQL analytics**
```bash
# Runs all 4 analytical queries and prints results to terminal
python src/sql_analytics.py
```

**7. Launch the dashboard**
```bash
streamlit run src/app.py
```

Navigate to `http://localhost:8501` in your browser.

---

## 🔐 Security Notes

- The `.env` file containing `GEMINI_API_KEY` is listed in `.gitignore` and is **never committed to version control**
- The API key is logged only as a boolean (`True`/`False`) to confirm presence — the key string is never written to any log file
- All database connections use parameterized queries via SQLAlchemy to prevent SQL injection

---

## 📈 SQL Highlights

The analytical backbone of RetailLens demonstrates four categories of SQL proficiency evaluated in data consulting technical screens:

```sql
-- YoY Sales Growth: CTE + LAG() Window Function (Query 3)
WITH yearly_sales AS (
    SELECT
        STRFTIME('%Y', order_date)  AS order_year,
        ROUND(SUM(sales), 2)        AS total_sales
    FROM superstore_sales
    GROUP BY order_year
)
SELECT
    order_year,
    total_sales,
    LAG(total_sales) OVER (ORDER BY order_year)  AS prior_year_sales,
    ROUND(
        ((total_sales - LAG(total_sales) OVER (ORDER BY order_year))
        / LAG(total_sales) OVER (ORDER BY order_year)) * 100,
    2) AS yoy_growth_pct
FROM yearly_sales
ORDER BY order_year ASC;
```

---

## 🗺️ Roadmap

- [ ] PostgreSQL migration for multi-user deployment
- [ ] Scheduled ETL via Apache Airflow DAG
- [ ] Role-based access control (RBAC) for multi-tenant dashboard views
- [ ] Exportable PDF executive report generation
- [ ] Forecasting module: Prophet-based 90-day sales projection

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

**Built for the NeenOpal Data Analytics Internship Application**

*Designed with precision. Engineered for insight.*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/yourprofile)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-22C55E?style=flat-square)](https://yourportfolio.com)

</div>
