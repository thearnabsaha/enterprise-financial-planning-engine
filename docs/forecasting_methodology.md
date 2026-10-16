# Financial Forecasting Methodology

**Enterprise Financial Planning & Forecasting Engine**  
**Northstar Digital Services GmbH**  

---

## 1. Overview of Forecast Methods

The engine provides three complementary forecasting methodologies suited for different operational contexts:

1. **Method 1: Baseline Linear Trend Extrapolation** (Statistical)
2. **Method 2: Assumption-Driven Compounding** (Driver-based)
3. **Method 3: Multi-Account Scenario Modeling** (Enterprise Sensitivity)

---

## 2. Method 1: Baseline Linear Trend Extrapolation

### Mechanics
Calculates an ordinary least squares (OLS) linear regression line across historical periods indexed $t \in [0, n-1]$:

$$\hat{y}_t = \alpha + \beta t$$

Where the slope $\beta$ and intercept $\alpha$ are calculated as:

$$\beta = \frac{\sum_{i=0}^{n-1} (i - \bar{x})(y_i - \bar{y})}{\sum_{i=0}^{n-1} (i - \bar{x})^2}, \quad \alpha = \bar{y} - \beta \bar{x}$$

Future periods are extrapolated by evaluating $\hat{y}_{n+j}$ for $j \in [0, k-1]$.

### Use Case
Ideal for recurring, non-seasonal operational expense accounts (e.g. rent, depreciation, recurring utility overheads).

---

## 3. Method 2: Assumption-Driven Compounding

### Mechanics
Computes future monthly amounts by applying an explicit growth or adjustment rate $g$ against prior period figures:

$$\text{Forecast}_t = \text{Forecast}_{t-1} \times (1 + g)$$

For operating expense lines (stored as negative values), growth applies to the expense magnitude while strictly preserving the negative sign:

$$\text{Forecast}_t = -1 \times \left( |\text{Forecast}_{t-1}| \times (1 + g) \right)$$

### Use Case
Ideal for modeling inflationary cost pressures (e.g., annual 4% salary adjustments, 12% cloud usage growth) and revenue expansion targets.

---

## 4. Method 3: Multi-Account Scenario Modeling

### Mechanics
Combines account-level and department-level drivers into coherent scenarios:

* **Optimistic Scenario**: Higher sales growth (+15%), controlled cloud costs (+5%), moderate salary expansion (+3%).
* **Conservative Scenario**: Moderate sales (+3%), elevated cloud infrastructure (+20%), hiring freeze.
* **Revised Budget**: Mid-year board revision adjusting second-half targets following Q2 performance review.

### Persistence
Assumptions are stored in the relational `forecast_assumptions` table with versioning and foreign key links to scenarios and accounts.
