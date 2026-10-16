# Enterprise Financial Planning & Forecasting Engine

> A professional-grade financial planning, budgeting, forecasting, and variance analysis application built with Python, Streamlit, PostgreSQL, and TinyOlap.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-88%2B-brightgreen.svg)](#automated-tests)

---

## ⚠️ Portfolio Disclaimer

This project is a **portfolio implementation** built with open-source technologies (TinyOlap, PostgreSQL, Streamlit). It demonstrates multidimensional financial planning concepts that are transferable to enterprise systems like IBM Planning Analytics (TM1).

**This is NOT an IBM-certified or IBM-compatible TM1 application.** It does not use TM1 Rules, TurboIntegrator, MDX, or any IBM proprietary technology.

See [TM1 Concept Comparison](docs/tm1_comparison.md) for a detailed mapping of demonstrated skills versus skills requiring hands-on IBM Planning Analytics access.

---

## 🏢 About

**Northstar Digital Services GmbH** is a fictional company used for demonstration purposes. All financial data is synthetically generated — no real company data is used.

The application enables a finance professional to:

- **Upload** CSV and Excel financial files with guided validation
- **Validate** data structure, types, accounts, departments, and amounts
- **Import** approved records into PostgreSQL with transactional safety
- **Analyse** actuals versus budgets with favourability-aware variance analysis
- **Forecast** future performance using transparent, assumption-driven methods
- **Explore** financial data across multiple dimensions (account, department, period, scenario)
- **Export** filtered reports in CSV and Excel format
- **Audit** import history, validation errors, and system events

---

## ✨ Features

### Data Management
- Multi-file CSV and Excel upload with worksheet selection
- Automatic and manual column mapping
- Comprehensive validation (types, dates, accounts, departments, currencies, duplicates)
- Transactional imports with rollback protection
- Import history and error reporting

### Financial Analysis
- Revenue, operating expenses, operating profit, and margin calculations
- Budget variance with signed convention and favourability classification
- Month-over-month and year-over-year comparisons
- Department and account drill-down
- Decimal-safe financial arithmetic

### Forecasting & Scenarios
- Baseline trend forecasting from historical data
- Assumption-driven forecasting with configurable growth rates
- Multi-scenario comparison (optimistic, conservative, custom)
- Transparent formulas — every result traceable to its inputs

### Multidimensional Modelling
- TinyOlap in-memory OLAP cube with five dimensions
- Account and department hierarchies with consolidation
- Python `@rule` calculations for derived metrics
- PostgreSQL ↔ TinyOlap data synchronisation

### Reporting & Export
- 10+ report types with filter application
- CSV and Excel downloads
- Professional number, currency, and percentage formatting
- Filter metadata included in exports

---

## 🏗️ Architecture

```
Financial CSV/Excel Files
    │
    ▼
┌─────────────────────────┐
│  File Upload & Inspect  │  ← Streamlit UI
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  Column Mapping         │  ← Auto-detect + manual override
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  Validation Engine      │  ← 15+ validation rules
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  ETL Pipeline           │  ← Transform, normalise, deduplicate
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  PostgreSQL             │  ← Source of truth (12 tables)
│  (Neon / Local)         │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  TinyOlap OLAP Model   │  ← In-memory multidimensional cube
│  (5 dimensions)         │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  Calculation Services   │  ← Variance, metrics, forecasting
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  Streamlit Dashboards   │  ← 10 interactive pages
│  & Report Exports       │
└─────────────────────────┘
```

### Layer Separation

| Layer | Responsibility | Technology |
|-------|---------------|------------|
| **Presentation** | UI pages, charts, filters, exports | Streamlit, Plotly |
| **Service** | Business logic, orchestration | Python services |
| **Calculation** | Financial formulas, forecasting | Pure Python + TinyOlap |
| **OLAP** | Multidimensional modelling | TinyOlap |
| **Data Access** | CRUD, queries, transactions | SQLAlchemy, psycopg |
| **Storage** | Persistent financial data | PostgreSQL (Neon) |

---

## 🖥️ Pages

| # | Page | Description |
|---|------|-------------|
| 1 | **Overview Dashboard** | KPI cards, revenue/profit charts, department comparisons |
| 2 | **Upload & Import** | Multi-file upload, preview, mapping, validation, import |
| 3 | **Data Validation** | Validation rules, error inspection, template download |
| 4 | **Financial Explorer** | Dimension-based drill-down, record-level detail |
| 5 | **Budget & Variance** | Actual vs budget, favourability, variance trends |
| 6 | **Forecasting & Scenarios** | Create/compare scenarios, adjust assumptions |
| 7 | **Reports & Exports** | Filtered CSV/Excel downloads, 10+ report types |
| 8 | **Import History** | Batch tracking, error reports, audit trail |
| 9 | **Data Model & Admin** | Hierarchies, health checks, demo data regeneration |
| 10 | **Settings & Docs** | Configuration, glossary, help |

<!-- Screenshots will be added after UI implementation -->

---

## 📊 Financial Conventions

### Sign Convention

| Item | Sign | Example |
|------|------|---------|
| Revenue | Positive (+) | +€100,000 |
| Operating Expenses | Negative (−) | −€50,000 |
| Operating Profit | Revenue + Expenses | +€50,000 |
| Operating Margin | (Profit / Revenue) × 100 | 50% |

### Variance Calculation

```
Signed Variance = Actual − Budget

Favourability:
  Revenue:   positive variance → Favourable (earned more than planned)
  Expenses:  negative variance → Unfavourable (spent more than planned)
  Profit:    positive variance → Favourable (more profitable than planned)
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web UI | Streamlit | Interactive dashboards and forms |
| Charts | Plotly | Financial visualisations |
| Backend | Python 3.10+ | Application logic |
| Data Processing | Pandas, NumPy | Tabular data and numerical ops |
| OLAP | TinyOlap | Multidimensional modelling |
| ORM | SQLAlchemy | Database abstraction |
| Database | PostgreSQL (Neon) | Persistent storage |
| Validation | Pydantic | Configuration and type validation |
| Migrations | Alembic | Database schema versioning |
| Testing | pytest | Automated test suite |
| Excel | openpyxl, xlsxwriter | Excel read/write |
| Containerisation | Docker | Reproducible deployment |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or later
- PostgreSQL 15+ (local) or a [Neon](https://neon.tech) free-tier database
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/enterprise-financial-planning-engine.git
cd enterprise-financial-planning-engine
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL connection string
```

```env
DATABASE_URL=postgresql://user:password@localhost:5432/northstar_financial
APP_ENV=development
DEBUG=true
DEMO_MODE=true
DATA_SEED=42
```

### 5. Run Database Migrations

```bash
python scripts/run_migrations.py
```

### 6. Generate Demonstration Data

```bash
python scripts/generate_data.py --seed 42
python scripts/seed_database.py
```

### 7. Start the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

---

## 🧪 Automated Tests

Run the full test suite:

```bash
pytest tests/ -v --tb=short
```

Run specific test categories:

```bash
pytest tests/test_calculations.py -v    # Financial calculations
pytest tests/test_variance.py -v        # Variance & favourability
pytest tests/test_data_generator.py -v  # Synthetic data generator
pytest tests/test_etl.py -v             # ETL pipeline
pytest tests/test_import.py -v          # Import workflow
pytest tests/test_database.py -v        # Database constraints
pytest tests/test_olap.py -v            # TinyOlap model
pytest tests/test_forecasting.py -v     # Forecast methods
```

### Test Coverage

| Category | Tests | Coverage |
|----------|-------|----------|
| Data Generator | 14 | Determinism, consistency, dimensions |
| Financial Calculations | 15 | Variance, margin, metrics, edge cases |
| Variance Logic | 10 | Favourability, sign convention, zero budget |
| Forecasting | 8 | Baseline, assumption-driven, scenario |
| ETL Pipeline | 12 | Parse, map, validate, transform |
| Import Workflow | 10 | Dedup, rollback, batch tracking |
| Database | 8 | Migrations, constraints, transactions |
| OLAP Model | 6 | Dimensions, rules, adapter |
| Export | 5 | Filters, content, formats |
| **Total** | **88+** | |

---

## 🐳 Docker

Build and run locally:

```bash
docker build -t northstar-financial .
docker run -p 8501:8501 --env-file .env northstar-financial
```

---

## ☁️ Deployment

### Streamlit Community Cloud

1. Push the repository to GitHub
2. Sign in to [share.streamlit.io](https://share.streamlit.io)
3. Connect the repository
4. Set secrets in the Streamlit Cloud dashboard:
   ```toml
   [database]
   url = "postgresql://user:password@host:5432/dbname?sslmode=require"
   ```
5. Deploy

### Neon PostgreSQL Setup

1. Create a free account at [neon.tech](https://neon.tech)
2. Create a new project named `northstar-financial`
3. Copy the connection string
4. Run migrations: `python scripts/run_migrations.py`
5. Seed the database: `python scripts/seed_database.py`

> **Note:** Neon free-tier quotas, compute-hour limits, and sleep behaviour may change. Check [Neon pricing](https://neon.tech/pricing) for current limits.

See [Deployment Guide](docs/deployment_guide.md) for detailed instructions.

---

## 📁 Project Structure

```
enterprise-financial-planning-engine/
├── app.py                    # Streamlit entry point
├── pages/                    # 10 Streamlit pages
├── components/               # Reusable UI components
├── services/                 # Business logic layer
├── models/                   # Pydantic domain models
├── database/                 # ORM, migrations, repository
├── olap/                     # TinyOlap model & adapter
├── calculations/             # Financial formulas & forecasting
├── etl/                      # ETL pipeline (parse → load)
├── data_generator/           # Synthetic data generation
├── data/sample/              # Demo CSV files & data dictionary
├── tests/                    # 88+ automated tests
├── scripts/                  # CLI utilities
├── docs/                     # 15+ documentation files
├── .github/workflows/        # CI pipeline
├── Dockerfile                # Container build
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
└── .gitignore                # Git exclusions
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design and component diagrams |
| [Data Flow](docs/data_flow.md) | End-to-end data pipeline |
| [Database Schema](docs/database_schema.md) | Table definitions, constraints, indexes |
| [Data Dictionary](docs/data_dictionary.md) | Field definitions and permitted values |
| [Financial Calculations](docs/financial_calculations.md) | Formulas, sign conventions, edge cases |
| [Forecasting Methodology](docs/forecasting_methodology.md) | Three forecast methods explained |
| [OLAP Model](docs/olap_model.md) | TinyOlap design and boundaries |
| [Import Workflow](docs/import_workflow.md) | 8-step import pipeline |
| [Test Strategy](docs/test_strategy.md) | Test approach and coverage |
| [Deployment Guide](docs/deployment_guide.md) | Local, Docker, and cloud setup |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |
| [Security Notes](docs/security_notes.md) | Security practices |
| [TM1 Comparison](docs/tm1_comparison.md) | Concept mapping to IBM Planning Analytics |
| [Demo Script](docs/demo_script.md) | Step-by-step demonstration walkthrough |
| [Known Limitations](docs/known_limitations.md) | Honest assessment and future work |

---

## 🔄 IBM TM1 Concept Mapping

This project demonstrates concepts transferable to IBM Planning Analytics (TM1) roles:

| Concept | This Project | IBM TM1 |
|---------|-------------|---------|
| Multidimensional modelling | ✅ TinyOlap | TM1 Cubes |
| Dimensions & hierarchies | ✅ TinyOlap | TM1 Dimensions |
| Financial calculations | ✅ Python `@rule` | TM1 Rules |
| ETL pipelines | ✅ Python ETL | TurboIntegrator |
| Dimensional querying | ✅ Python slicing | MDX |
| Scenario management | ✅ PostgreSQL + UI | Sandboxes / Scenarios |
| Variance analysis | ✅ Calculation engine | Cube views / reports |
| Data validation | ✅ Validation engine | TI error handling |

**Requires IBM TM1 practice:** TM1 Rules syntax, TurboIntegrator scripting, MDX queries, TM1 Server administration, Planning Analytics Workspace.

See [TM1 Comparison](docs/tm1_comparison.md) for the complete analysis.

---

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `APP_ENV` | Environment (`development`/`production`) | `development` |
| `DEBUG` | Enable debug logging | `true` |
| `DEMO_MODE` | Show demo data generation button | `true` |
| `DATA_SEED` | Random seed for reproducible data | `42` |
| `MAX_UPLOAD_SIZE_MB` | Maximum upload file size | `50` |
| `MAX_UPLOAD_ROWS` | Maximum rows per upload | `100000` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## 🔒 Security

- Parameterised SQL (no string concatenation of user input)
- Secrets stored in environment variables / Streamlit secrets
- `.env` and secrets excluded from Git
- File type and size validation on uploads
- Transactional imports with rollback
- No real customer data
- Safe error messages (no connection string exposure)
- Audit trail for data modifications

This is a **portfolio/demo application**. It does not implement production-grade authentication or multi-tenant access controls. See [Security Notes](docs/security_notes.md).

---

## 📋 Known Limitations

- Single-user application (no authentication)
- TinyOlap is not IBM TM1 — no MDX, no TM1 Rules syntax
- Neon free tier has compute-hour and storage limits
- Streamlit Community Cloud may sleep on inactivity
- No machine learning forecasting (deliberate — uses transparent financial methods)
- Excel export limited to ~1M rows (Excel format constraint)

See [Known Limitations](docs/known_limitations.md) for the full list.

---

## 🗺️ Future Improvements

- [ ] Multi-currency conversion with exchange rates
- [ ] Cash flow forecasting module
- [ ] Balance sheet modelling
- [ ] Role-based access control
- [ ] REST API for external integration
- [ ] Advanced statistical forecasting (ARIMA, Prophet)
- [ ] PDF report generation
- [ ] Automated anomaly detection
- [ ] AWS deployment option
- [ ] Real-time collaboration

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Arnab Saha**

Built as a portfolio project demonstrating enterprise financial planning and analytics development skills.

---

<p align="center">
  <em>Northstar Digital Services GmbH is a fictional company. All financial data is synthetically generated.</em>
</p>
