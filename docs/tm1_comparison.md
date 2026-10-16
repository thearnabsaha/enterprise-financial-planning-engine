# IBM Planning Analytics (TM1) vs. Northstar Python Engine

A comprehensive architectural comparison between traditional **IBM Planning Analytics (TM1)** and the modern Python multidimensional architecture implemented in this repository.

---

## 1. High-Level Concept Mapping

| Feature / Concept | IBM Planning Analytics (TM1) | Northstar Python Planning Engine |
|---|---|---|
| **Multidimensional Storage** | In-memory proprietary TM1 Cubes (.cub) | **TinyOlap 4D In-Memory Cubes** |
| **Dimension Hierarchy** | N-Level (Numeric), C-Level (Consolidation), S-Level (String) | **Leaf Members, Consolidation Weights (+1.0), Parent References** |
| **Calculations / Rules** | TM1 Rules Language (`.rux`) with Feeders | **Python `@rule` Decorated Functions on Cell Objects** |
| **ETL & Data Movement** | TurboIntegrator (TI) Processes (`.pro`) | **8-Step Transactional Python ETL Pipeline (`etl/`)** |
| **Data Types & Precision** | 64-bit IEEE 754 Floating-Point Doubles | **Arbitrary-Precision `decimal.Decimal` (Zero Rounding Errors)** |
| **Persistence / Storage** | Proprietary Flat Files (`.cub`, `.dim`) on disk | **PostgreSQL (Production) & SQLite (Testing/Local)** |
| **Presentation / UI** | Planning Analytics Workspace (PAW), TM1 Web, Excel PAX | **Streamlit Multi-Page App with Custom Enterprise CSS & Plotly** |
| **Audit Logging** | TM1 Transaction Log (`tm1s.log`) | **Relational `audit_events` and `import_batches` Tables** |
| **Automation & Chores** | TM1 Chores / Server Schedules | **Python CLI Scripts (`scripts/`) & Cron Jobs** |

---

## 2. In-Depth Architectural Comparison

### 2.1 Multidimensional Modeling & Hierarchy
* **In TM1**: Dimensions are created with elements assigned types (`N` for leaf numbers, `C` for consolidated parents). Rollups are defined with weights (usually $1.0$ or $-1.0$).
* **In Northstar Engine**: Modeled in `olap/model.py` using TinyOlap:
  ```python
  acc_dim = db.add_dimension("Account").edit()
  acc_dim.add("REV", None, 1.0, "Revenue")
  acc_dim.add("TOTAL_OPEX", None, 1.0, "Total Operating Expenses")
  for acc in LEAF_EXPENSES:
      acc_dim.add(acc.code, "TOTAL_OPEX", 1.0, acc.name)
  acc_dim.commit()
  ```
  Consolidations roll up in memory in sub-millisecond execution times.

### 2.2 Business Rules & Dynamic Calculations
* **In TM1**: Written in `.rux` files using brackets:
  ```tm1
  ['Operating Profit'] = N: ['REV'] + ['TOTAL_OPEX'];
  ['Operating Margin'] = N: (['Operating Profit'] \ ['REV']) * 100;
  FEEDERS;
  ['REV'] => ['Operating Profit'];
  ['TOTAL_OPEX'] => ['Operating Profit'];
  ```
* **In Northstar Engine**: Written as type-safe Python rule functions:
  ```python
  @rule("Financials", ["Operating Profit"])
  def rule_operating_profit(c: Cell) -> float:
      dept = c.member("Department")
      period = c.member("Period")
      scenario = c.member("Scenario")
      return float(c.cube["REV", dept, period, scenario] + c.cube["TOTAL_OPEX", dept, period, scenario])
  ```
  TinyOlap automatically coordinates rule injection and dependencies.

### 2.3 ETL Pipeline (TurboIntegrator vs Python ETL)
* **In TM1**: TurboIntegrator processes define Prolog, Metadata, Data, and Epilog tabs. Mappings and error handling are often rigid and prone to silent failures.
* **In Northstar Engine**: An 8-step pipeline (`etl/`):
  1. `file_parser.py`: Safe parsing of CSV/Excel with byte inspection and preview.
  2. `column_mapper.py`: Fuzzy alias detection and confidence scoring.
  3. `validator.py`: Domain validation checking foreign keys, date ranges, and currencies.
  4. `loader.py`: Atomic transactional database commits with configurable duplicate policies (`REJECT`, `SKIP`, `REPLACE`).

---

## 3. Advantages of the Python Hybrid Approach

1. **Precision Decimal Arithmetic**: Unlike TM1's floating-point math, Python's `Decimal` ensures accounts balance to the exact cent across large enterprise data sets.
2. **Modern Developer Experience**: Version control via Git, automated unit tests with `pytest`, standard CI/CD pipelines, and Python ecosystem libraries (Pandas, Plotly, SQLAlchemy).
3. **Open Standards & Cost**: Zero vendor lock-in, zero per-seat licensing fees, and easy deployment to container platforms (Docker, Kubernetes) and cloud SQL databases.
