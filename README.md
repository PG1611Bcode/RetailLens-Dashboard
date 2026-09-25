# RetailLens: Executive E-Commerce Analytics Platform

RetailLens is an end-to-end Business Intelligence (BI) platform designed to ingest, process, and visualize high-volume e-commerce transaction data. Built with a focus on consulting-grade KPIs, it features an automated ETL pipeline, a robust local relational database architecture, and a dynamic frontend integrated with an automated strategic analysis engine.

## 🏗️ System Architecture

* **Data Engineering (ETL):** Automated Python pipeline utilizing `pandas` to ingest, sanitize, and validate 10,000+ rows of raw transactional data.
* **Database Layer:** Local `SQLite` relational database optimized for complex analytical queries (CTEs, Window Functions, LAG) without requiring external server dependencies.
* **Frontend Visualization:** Interactive, theme-adaptive `Streamlit` dashboard featuring multi-parameter reactive filtering and `Plotly` data visualizations.
* **Automated Strategic Analysis:** Integrated generative intelligence engine that synthesizes real-time dashboard state into actionable, human-readable executive insights.

## 🚀 Key Features

* **Real-Time KPI Tracking:** Instant calculation of Total Revenue, Profit Margins, and Average Order Value (AOV).
* **Advanced SQL Analytics:** Year-over-Year (YoY) growth calculations and granular customer segmentation logic executed directly at the database level.
* **Dynamic Filtering:** Multi-select state management for Time Period, Geography, and Product Category.
* **Proprietary Insight Engine:** Automated generation of 2-paragraph strategic consulting summaries based strictly on current UI filter states.

## 💻 Local Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/YourUsername/RetailLens-Analytics.git](https://github.com/YourUsername/RetailLens-Analytics.git)
   cd RetailLens-Analytics
