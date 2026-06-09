# Decision Intelligence Dashboard — Olist Marketplace
 A production-grade decision intelligence platform for 3,000+ sellers on the Brazilian Olist marketplace. Combines dbt data modelling, DuckDB analytics engine, and Claude AI to detect performance anomalies and answer business questions in plain English — before they impact customers.

🔴 **[Live Demo](https://decision-intelligence-olist.onrender.com/)**

---

## What this does

Most dashboards show you what happened. This one tells you what to do about it.

Built on 2 years of Olist marketplace data (Oct 2016 – Aug 2018), the platform monitors 2,970 sellers across 35,383 weekly snapshots — flagging at-risk sellers, explaining anomalies using AI, and letting non-technical users query the data in plain English.

---

## Dashboard pages

**1. Seller Performance Intelligence (Home)**
- Platform-wide KPIs: 92.7% on-time rate · 4.17/5 avg review score · 3,716 at-risk records
- On-time rate trend over time (Oct 2016 – Aug 2018)
- Review score vs on-time rate scatter — correlation analysis across all sellers
- 1,369 sellers flagged below the 80% on-time threshold

**2. Seller Analysis — Leaderboard**
- Interactive leaderboard: filter by minimum orders and at-risk status
- Top 20 sellers ranked by on-time rate with RAG (Red/Amber/Green) colour coding
- Metrics per seller: total orders · on-time % · review score · freight %

**3. AI Analytics Assistant**
- Natural language interface — ask questions about seller performance in plain English
- Powered by Claude AI + DuckDB — queries the actual dataset, not a pre-built summary
- Example queries: *"Who are the worst performing sellers?"* · *"Which month had the lowest on-time rate?"* · *"What is the correlation between delivery and reviews?"*

**4. Anomaly Signals**
- AI-detected performance drops requiring immediate action
- Each alert shows: on-time rate · prior week · change in pp · review score
- AI-generated plain-English explanation of likely root cause per alert
- All flagged sellers visualised by rate change magnitude

---

## Tech stack

- **Frontend** — Streamlit
- **Data modelling** — dbt (staging → mart layer transformations)
- **Analytics engine** — DuckDB (in-process SQL on Parquet/CSV, no server needed)
- **AI layer** — Claude AI (anomaly explanation + natural language query)
- **Language** — Python
- **Data source** — [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle, public)
- **Deploy** — Render (live, always-on)

---

## Architecture

```
Raw Olist CSV files (9 tables)
        │
        ▼
  dbt models
        ├── Staging layer    → clean, typed, renamed source tables
        └── Mart layer       → seller_weekly_metrics, anomaly_signals, kpi_summary
        │
        ▼
  DuckDB (in-process analytics engine)
        └── SQL queries run directly on dbt output at runtime
        │
        ▼
  Streamlit app (4 pages)
        ├── Home             → KPI cards + trend charts (Plotly)
        ├── Seller Analysis  → interactive leaderboard + RAG bar chart
        ├── AI Assistant     → Claude AI + DuckDB natural language queries
        └── Anomaly Signals  → AI-generated alert explanations + flagged sellers
```

---

## Key technical decisions

**Why dbt + DuckDB instead of Pandas?**
dbt enforces a proper transformation layer with tested, documented models — the same pattern used in production analytics engineering at companies like Zalando, HelloFresh, and Auto Trader. DuckDB runs SQL directly on files at millisecond speed without a server, making it ideal for a deployed Streamlit app with no database infrastructure.

**Why Claude AI for anomaly explanation?**
Rule-based anomaly detection flags *what* changed. Claude explains *why* it likely happened and *what to do* — turning a data signal into an actionable recommendation. This is the difference between a monitoring tool and a decision intelligence platform.

**RAG colour coding on seller leaderboard**
Sellers are coloured Green (>90% on-time), Amber (80–90%), Red (<80%) — matching the business threshold used by marketplace operations teams to prioritise interventions.

---

## Skills demonstrated

- **dbt** — multi-layer data modelling (staging + marts), schema tests, documentation
- **DuckDB** — in-process SQL analytics engine, query optimisation
- **Claude AI / LLM integration** — natural language to SQL, anomaly explanation generation
- **Python** — modular Streamlit app architecture, 4-page navigation
- **Plotly** — interactive time series, scatter plots, bar charts with conditional formatting
- **Data pipeline design** — raw CSV → transformed marts → live dashboard
- **Product thinking** — anomaly detection → AI explanation → actionable alert (end-to-end)
- **Deployment** — live production app on Render

---
## How to run locally

**1. Clone the repo**
```bash
git clone https://github.com/shreya-salvi/decision-intelligence-olist
cd decision-intelligence-olist
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set API key**

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_claude_api_key_here
```

**4. Run dbt models**
```bash
dbt run
```

**5. Launch app**
```bash
streamlit run app.py
```

---

## What I'd add next

- **dbt Cloud deployment** — schedule daily model runs automatically
- **Seller email alerts** — trigger notifications when anomaly signals fire
- **Forecasting layer** — predict next-week on-time rate per seller using Prophet
- **Snowflake backend** — replace DuckDB with Snowflake for multi-user scale

---

*Part of a portfolio demonstrating production-grade analytics engineering — dbt · DuckDB · AI integration · live deployment.*
