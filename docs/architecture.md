# Architecture Overview & Technical Design

**Enterprise Financial Planning & Forecasting Engine**  
**Company:** Northstar Digital Services GmbH  
**Architect:** Arnab Saha  

---

## 1. System Architecture Diagram

```mermaid
graph TD
    subgraph Client Layer [Executive Presentation Layer]
        UI[Streamlit Web Application]
        P1[01 Overview Dashboard]
        P2[02 Upload & Import]
        P4[04 Financial Explorer]
        P5[05 Budget & Variance]
        P6[06 Forecasting & Scenarios]
        P7[07 Reports & Exports]
    end

    subgraph Service Layer [Business & Financial Services]
        CalcService[Calculation Service]
        ForecastService[Forecast Service]
        ImportService[Import Service]
        ValidService[Validation Service]
        ExportService[Export Service]
        AuditService[Audit Service]
    end

    subgraph Analytical Layer [Multidimensional Core]
        OlapAdapter[OLAP Sync Adapter]
        TinyOlap[TinyOlap 4D Cube: Financials]
        Rules[Rule Engine: Profit & Margin]
    end

    subgraph Persistence Layer [Relational Database]
        Repo[SQLAlchemy 2.0 Repository]
        DB[(PostgreSQL / SQLite)]
    end

    UI --> P1 & P2 & P4 & P5 & P6 & P7
    P1 & P5 --> CalcService
    P6 --> ForecastService
    P2 --> ImportService
    P7 --> ExportService
    P4 --> OlapAdapter

    CalcService --> Repo
    ForecastService --> Repo
    ImportService --> ValidService --> Repo
    ExportService --> CalcService
    AuditService --> Repo

    Repo --> DB
    Repo --> OlapAdapter --> TinyOlap --> Rules
```

---

## 2. Multidimensional Cube Design (IBM TM1 Parity)

The core analytical model is represented as a 4-dimensional hypercube:

$$\mathbf{Cube}(\text{Account}, \text{Department}, \text{Period}, \text{Scenario})$$

### Dimensions & Consolidations

1. **Account Dimension**:
   - `REV` (Numeric Leaf, Weight $+1.0$)
   - `TOTAL_OPEX` (Consolidation, Weight $+1.0$)
     - `SAL` (Salaries and Benefits, Weight $+1.0$)
     - `CLOUD` (Cloud Infrastructure, Weight $+1.0$)
     - `SW` (Software Subscriptions, Weight $+1.0$)
     - `MKT_EXP` (Marketing Expenses, Weight $+1.0$)
     - `RENT` (Rent and Facilities, Weight $+1.0$)
     - `TRAVEL` (Travel & Entertainment, Weight $+1.0$)
     - `PROF` (Professional Services, Weight $+1.0$)
     - `DEPR` (Depreciation, Weight $+1.0$)
     - `INSUR` (Insurance, Weight $+1.0$)
     - `TRAIN` (Training & Development, Weight $+1.0$)
     - `OTHER` (Other Operating Expenses, Weight $+1.0$)
   - `Operating Profit` (Calculated Rule)
   - `Operating Margin` (Calculated Rule)

2. **Department Dimension**:
   - `COMPANY` (Consolidated Parent, Weight $+1.0$)
     - `ENG` (Engineering, Weight $+1.0$)
     - `SALES` (Sales, Weight $+1.0$)
     - `MKT` (Marketing, Weight $+1.0$)
     - `OPS` (Operations, Weight $+1.0$)
     - `FIN` (Finance, Weight $+1.0$)

3. **Period Dimension**:
   - Monthly grain from `2024-01` through `2026-12` (36 months).

4. **Scenario Dimension**:
   - `Actuals`
   - `Original Budget`
   - `Revised Budget`
   - `Forecast v1`
   - `Optimistic Scenario`
   - `Conservative Scenario`

---

## 3. Relational Schema & Constraints

The relational store ensures permanent durability, relational integrity, and auditability:

```mermaid
erDiagram
    DEPARTMENTS ||--o{ FINANCIAL_FACTS : classifies
    ACCOUNTS ||--o{ FINANCIAL_FACTS : classifies
    PERIODS ||--o{ FINANCIAL_FACTS : classifies
    SCENARIOS ||--o{ FINANCIAL_FACTS : classifies
    VERSIONS ||--o{ FINANCIAL_FACTS : classifies
    IMPORT_BATCHES ||--o{ FINANCIAL_FACTS : tracks
    IMPORT_BATCHES ||--o{ IMPORT_FILES : contains
    IMPORT_BATCHES ||--o{ VALIDATION_ERRORS : records

    DEPARTMENTS {
        int id PK
        string code UK
        string name
        string parent_code FK
    }
    ACCOUNTS {
        int id PK
        string code UK
        string name
        string category
        int sign_convention
    }
    PERIODS {
        int id PK
        string period_key UK
        int year
        int month
    }
    FINANCIAL_FACTS {
        bigint id PK
        int period_id FK
        int department_id FK
        int account_id FK
        int scenario_id FK
        int version_id FK
        string currency
        decimal amount
    }
    AUDIT_EVENTS {
        bigint id PK
        string event_type
        text event_description
        timestamp created_at
    }
```
