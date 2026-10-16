# Financial Calculations & Accounting Sign Conventions

**Enterprise Financial Planning & Forecasting Engine**  
**Northstar Digital Services GmbH**  

---

## 1. Accounting Sign Convention Standard

To reflect real-world management accounting and corporate controllership practices, the engine enforces strict sign conventions:

### Directional Signs
* **Revenue**: Always positive ($+$).
* **Operating Expenses**: Always negative ($-$).
* **Operating Profit**: Evaluated as $\text{Revenue} + \text{Operating Expenses}$.
  $$\text{Operating Profit} = \sum \text{Revenue} + \sum \text{Operating Expenses}$$
  *(Example: €1,000,000 + (-€700,000) = €300,000)*
* **Operating Margin %**:
  $$\text{Operating Margin} = \left( \frac{\text{Operating Profit}}{\text{Revenue}} \right) \times 100$$
  *(Returns `None` if Revenue is zero or negative to prevent invalid ratios)*

---

## 2. Signed Variance & Favourability Classification

### 2.1 Formula
$$\text{Signed Variance} = \text{Actual} - \text{Budget}$$
$$\text{Variance \%} = \left( \frac{\text{Actual} - \text{Budget}}{|\text{Budget}|} \right) \times 100$$

### 2.2 Favourability Logic by Account Category

#### Revenue & Operating Profit
* When $\text{Actual} > \text{Budget}$, $\text{Variance} > 0 \implies \mathbf{FAVOURABLE}$ (Earned more than budgeted).
* When $\text{Actual} < \text{Budget}$, $\text{Variance} < 0 \implies \mathbf{UNFAVOURABLE}$ (Shortfall in revenue).

#### Operating Expenses (Stored as Negative Amounts)
* When $\text{Actual}$ is *more negative* than $\text{Budget}$ (e.g. Actual $-€55,000$ vs Budget $-€50,000$):
  $$\text{Signed Variance} = -55,000 - (-50,000) = -5,000$$
  Since $\text{Variance} < 0$, this represents an overspend $\implies \mathbf{UNFAVOURABLE}$ (Red).
* When $\text{Actual}$ is *less negative* than $\text{Budget}$ (e.g. Actual $-€45,000$ vs Budget $-€50,000$):
  $$\text{Signed Variance} = -45,000 - (-50,000) = +5,000$$
  Since $\text{Variance} > 0$, this represents an underspend/cost savings $\implies \mathbf{FAVOURABLE}$ (Green).

---

## 3. Edge Case Handling

1. **Zero Budget**:
   - If Budget is 0, $\text{Variance \%}$ is undefined (`None`). The UI renders `"N/A"`, while displaying the absolute signed variance amount.
2. **Missing Actuals**:
   - For future months where actuals have not occurred, actual values are omitted and variance is bypassed.
3. **Division by Zero**:
   - Protected by `safe_divide()` across all margin and growth calculations.
