"""
KPI metric card UI component with comparison delta, variance, and favourability badge.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional, Union
import streamlit as st

from calculations.formatting import format_currency, format_percent


def render_kpi_card(
    title: str,
    value: Union[float, Decimal, str],
    comparison_value: Optional[Union[float, Decimal, str]] = None,
    variance: Optional[Union[float, Decimal]] = None,
    variance_pct: Optional[Union[float, Decimal]] = None,
    favourability: str = "neutral",
    is_percentage: bool = False,
    help_text: Optional[str] = None,
    accent_color: str = "#3b82f6",
    sub_label: Optional[str] = None,
) -> None:
    """Render a single styled executive metric card using st.html."""
    # Format main value
    if is_percentage and isinstance(value, (int, float, Decimal)):
        formatted_val = f"{float(value):.2f}%"
    elif isinstance(value, (int, float, Decimal)):
        formatted_val = format_currency(value)
    else:
        formatted_val = str(value)

    # Delta styling
    favourability_clean = favourability.lower() if favourability else "neutral"
    delta_class = f"kpi-{favourability_clean}"
    badge_class = f"badge-{favourability_clean}"

    # Arrow indicator
    if favourability_clean == "favourable":
        arrow = "▲ "
    elif favourability_clean == "unfavourable":
        arrow = "▼ "
    else:
        arrow = "● "

    delta_html = ""
    if variance is not None:
        if is_percentage:
            var_text = f"{float(variance):+.2f}%"
        else:
            var_text = format_currency(variance, prefix="€")
            if float(variance) > 0:
                var_text = f"+{var_text}"

        pct_str = f" ({float(variance_pct):+.1f}%)" if variance_pct is not None else ""
        delta_html = f"""
        <div class="kpi-delta {delta_class}">
            <span class="{badge_class}">{arrow}{favourability.upper()}</span>
            <span style="font-weight: 600; letter-spacing: -0.01em;">{var_text}{pct_str}</span>
        </div>
        """
    elif variance_pct is not None:
        delta_html = f"""
        <div class="kpi-delta {delta_class}">
            <span class="{badge_class}">{arrow}{favourability.upper()}</span>
            <span style="font-weight: 600;">{float(variance_pct):+.1f}%</span>
        </div>
        """
    elif comparison_value is not None:
        comp_fmt = format_currency(comparison_value) if not is_percentage else f"{float(comparison_value):.2f}%"
        delta_html = f"""
        <div class="kpi-delta kpi-neutral">
            <span class="badge-neutral">TARGET</span>
            <span style="color: #94a3b8; font-size: 12px;">vs Budget: {comp_fmt}</span>
        </div>
        """

    sub_label_html = ""
    if sub_label:
        sub_label_html = f"""
        <div style="font-size: 11px; color: #64748b; margin-top: 6px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 5px;">
            {sub_label}
        </div>
        """

    card_html = f"""
    <div class="kpi-card" style="border-top: 3px solid {accent_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="kpi-title">{title}</span>
            <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background-color: {accent_color}; box-shadow: 0 0 6px {accent_color};"></span>
        </div>
        <div class="kpi-value">{formatted_val}</div>
        {delta_html}
        {sub_label_html}
    </div>
    """
    st.html(card_html)


def render_kpi_row(kpis: dict) -> None:
    """Render standard executive KPI grid (4 primary metrics + 2 secondary ratio cards)."""
    # Primary Metrics (Row 1: 4 columns)
    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)

    with row1_c1:
        render_kpi_card(
            title="Total Revenue",
            value=kpis.get("revenue", 0),
            comparison_value=kpis.get("revenue_budget", 0),
            variance=kpis.get("revenue_variance"),
            variance_pct=kpis.get("revenue_variance_pct"),
            favourability=kpis.get("revenue_favourability", "neutral"),
            accent_color="#3b82f6",
            sub_label=f"Budget: {format_currency(kpis.get('revenue_budget', 0))}",
        )
    with row1_c2:
        render_kpi_card(
            title="Operating Expenses",
            value=kpis.get("expenses", 0),
            comparison_value=kpis.get("expenses_budget", 0),
            variance=kpis.get("expenses_variance"),
            variance_pct=kpis.get("expenses_variance_pct"),
            favourability=kpis.get("expenses_favourability", "neutral"),
            accent_color="#f59e0b",
            sub_label=f"Budget: {format_currency(kpis.get('expenses_budget', 0))}",
        )
    with row1_c3:
        render_kpi_card(
            title="Operating Profit (EBIT)",
            value=kpis.get("profit", 0),
            comparison_value=kpis.get("profit_budget", 0),
            variance=kpis.get("profit_variance"),
            variance_pct=kpis.get("profit_variance_pct"),
            favourability=kpis.get("profit_favourability", "neutral"),
            accent_color="#10b981",
            sub_label=f"Budget: {format_currency(kpis.get('profit_budget', 0))}",
        )
    with row1_c4:
        margin_act = kpis.get("margin_pct", 0)
        margin_bud = kpis.get("margin_budget_pct", 0)
        margin_delta = margin_act - margin_bud if margin_act is not None and margin_bud is not None else None
        render_kpi_card(
            title="Operating Margin",
            value=margin_act,
            comparison_value=margin_bud,
            variance=margin_delta,
            favourability="favourable" if (margin_delta or 0) >= 0 else "unfavourable",
            is_percentage=True,
            accent_color="#8b5cf6",
            sub_label=f"Target Margin: {margin_bud:.1f}%",
        )

    # Secondary Performance Ratios (Row 2: 2 balanced columns)
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        rev = float(kpis.get("revenue", 0))
        bud_rev = float(kpis.get("revenue_budget", 0))
        achievement = (rev / bud_rev * 100) if bud_rev > 0 else 0
        render_kpi_card(
            title="Revenue Attainment Rate",
            value=f"{achievement:.1f}%",
            favourability="favourable" if achievement >= 100 else ("neutral" if achievement >= 95 else "unfavourable"),
            accent_color="#06b6d4",
            sub_label=f"Attainment against original targets ({format_currency(rev)} / {format_currency(bud_rev)})",
        )
    with row2_c2:
        p_var = kpis.get("profit_variance", 0)
        fav = kpis.get("profit_favourability", "neutral")
        render_kpi_card(
            title="Net Profit Variance Walk",
            value=p_var,
            variance=p_var,
            variance_pct=kpis.get("profit_variance_pct"),
            favourability=fav,
            accent_color="#ec4899",
            sub_label="Net signed variance to budget targets (Certified Decimal)",
        )
