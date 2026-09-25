<div align="center">

# 🔬 RetailLens
### Executive E-Commerce Analytics Platform

*End-to-end Business Intelligence engineered for consulting-grade insight delivery*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

[**View ETL Source**](src/ingest_data.py) · [**View SQL Analytics**](src/sql_analytics.py) · [**Report a Bug**](issues)

</div>

---

## 📌 Overview

**RetailLens** is a production-architected Business Intelligence platform that transforms raw transactional retail data into executive-ready strategic insight. Built across three engineering phases — automated ETL, analytical SQL backend, and a reactive Streamlit frontend — it demonstrates the full consulting analytics stack from raw CSV ingestion to boardroom-ready narrative generation.

The platform ingests **10,000+ rows** of Superstore sales data, runs advanced analytical SQL (including CTEs and LAG-based Year-over-Year window functions), renders five interactive Plotly KPI visualizations, and exposes an on-demand **Automated Strategic Analysis engine**. This engine reads the active dashboard filter state, aggregates live KPIs, and returns a 180-word two-paragraph strategic consulting brief — in under three seconds.

> **Target Use Case:** Retail category managers, regional sales directors, and strategy consultants who need fast, filter-driven performance diagnosis without manual report generation.

---

## 🏗️ System Architecture

```text
RetailLens Platform
├── 1. INGESTION LAYER      (pandas)   : Ingests & sanitizes 10k+ rows from raw CSV
├── 2. ANALYTICS LAYER      (SQLite)   : Executes CTEs, Window Functions, LAG logic
└── 3. PRESENTATION LAYER   (Streamlit): Renders Plotly visuals & Automated Insights
✨ Key Features🔄 Phase 1 — Automated ETL Pipeline (src/ingest_data.py)Ingests raw CSV with full schema validation and column-name normalization to snake_caseEnforces explicit dtype contracts: sales/profit/discount → float64, quantity → int64, date columns → datetime64Deduplicates, null-audits, and logs every transformation step via Python's logging modulePersists to SQLite via a sqlalchemy engine with chunksize=500 batch writesFully modular: four single-responsibility functions with type hints and Google-style docstrings🧮 Phase 2 — Advanced SQL Analytics Backend (src/sql_analytics.py)Query 1 — Regional Profitability: SUM/ROUND aggregations with computed profit margin percentage per regionQuery 2 — Sub-Category Ranking: Top 5 most profitable sub-categories including average discount appliedQuery 3 — YoY Sales Growth: CTE + LAG() window function extracts year-over-year revenue growth percentage across the full date range, with NULL preserved for the base yearQuery 4 — Customer Segmentation: Two-level CTE aggregation computing Average Order Value and Purchase Frequency per customer segmentAll queries fetched via pd.read_sql_query() and printed with formatted terminal headers📊 Phase 3 — Reactive Streamlit Dashboard (src/app.py)Five KPI metric cards with delta comparison against unfiltered baseline (Total Sales, Total Profit, Profit Margin, Total Orders, Average Order Value)Three Plotly charts: Monthly Sales Trend (spline + area fill), Profit by Region (color-scaled bar), Sales Distribution by Category (donut)Sidebar filter panel with st.multiselect widgets for Year, Region, and Category — all filters dynamically propagate to every KPI and chart simultaneouslyTheme-adaptive UI: Zero hardcoded background colors; seamlessly adapts to light and dark modes nativelyCollapsible raw data explorer with one-click CSV export of the current filtered view🧠 Automated Strategic Analysis EngineTriggered by a single "Generate Strategic Insights" button in the dashboardReads live filter state — the engine never summarizes stale or full data, only what the user is currently viewingAggregates eight KPIs into a structured data payload: revenue, margin, AOV, top/bottom sub-category, top region, full category profit breakdownReturns a 180-word, two-paragraph structured brief: Performance Diagnosis + two data-grounded Strategic RecommendationsGraceful degradation: Handles missing API configurations and network failures without crashing the dashboard🛠️ Tech StackLayerTechnologyPurposeData IngestionPython 3.10+, PandasCSV loading, cleaning, validationORM / DB LayerSQLAlchemy, SQLiteType-safe DB engine, persistent storageAnalyticsSQL (CTEs, Window Functions)KPI computation, YoY analysisFrontendStreamlit 1.30+Dashboard UI, layout, state managementVisualisationPlotly Express 5.xInteractive charts, hover templatesInsightsExternal NLP APINatural language KPI narrative generation📁 Project StructurePlaintextRetailLens/
├── data/
│   ├── raw/                 
│   │   └── Superstore.csv       # Source dataset (Kaggle)
│   └── processed/           
│       └── retaillens.db        # SQLite analytical database
├── src/
│   ├── ingest_data.py           # Phase 1: ETL pipeline
│   ├── sql_analytics.py         # Phase 2: SQL KPI queries
│   └── app.py                   # Phase 3: Streamlit dashboard
├── .env                         # API Keys (git-ignored)
├── .gitignore
├── requirements.txt
└── README.md
⚙️ Local InstallationPrerequisitesPython 3.10 or higherpip package managerSteps1. Clone the repositoryBashgit clone [https://github.com/PG1611Bcode/RetailLens-Analytics.git](https://github.com/PG1611Bcode/RetailLens-Analytics.git)
cd RetailLens-Analytics
2. Create and activate a virtual environmentBashpython -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
3. Install dependenciesBashpip install -r requirements.txt
4. Configure environment variablesBash# Create a .env file in the project root to enable the insights engine
echo "GEMINI_API_KEY=your_api_key_here" > .env
5. Run the ETL pipelineBash# Ingests Superstore.csv → cleans → loads into retaillens.db
python src/ingest_data.py
6. (Optional) Verify SQL analyticsBash# Runs all 4 analytical queries and prints results to terminal
python src/sql_analytics.py
7. Launch the dashboardBashstreamlit run src/app.py
Navigate to http://localhost:8501 in your browser.📈 SQL HighlightsThe analytical backbone of RetailLens demonstrates four categories of SQL proficiency evaluated in data consulting technical screens:SQL-- YoY Sales Growth: CTE + LAG() Window Function (Query 3)
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
🗺️ Roadmap[ ] PostgreSQL migration for multi-user deployment[ ] Scheduled ETL via Apache Airflow DAG[ ] Role-based access control (RBAC) for multi-tenant dashboard views[ ] Exportable PDF executive report generation📄 LicenseDistributed under the MIT License. See LICENSE for details.Built for the NeenOpal Data Analytics Internship ApplicationDesigned with precision. Engineered for insight.
