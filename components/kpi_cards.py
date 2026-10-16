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
) -> None:
    """Render a single styled executive metric card."""
    # Format main value
    if is_percentage and isinstance(value, (int, float, Decimal)):
        formatted_val = f"{float(value):.2f}%"
    elif isinstance(value, (int, float, Decimal)):
        formatted_val = format_currency(value)
    else:
        formatted_val = str(value)

    # Delta styling
    delta_class = f"kpi-{favourability.lower()}"
    badge_class = f"badge-{favourability.lower()}"

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
            <span class="{badge_class}">{favourability.upper()}</span>
            <span>{var_text}{pct_str}</span>
        </div>
        """
    elif variance_pct is not None:
        delta_html = f"""
        <div class="kpi-delta {delta_class}">
            <span class="{badge_class}">{favourability.upper()}</span>
            <span>{float(variance_pct):+.1f}%</span>
        </div>
        """
    elif comparison_value is not None:
        comp_fmt = format_currency(comparison_value) if not is_percentage else f"{float(comparison_value):.2f}%"
        delta_html = f"<div class='kpi-delta kpi-neutral'>vs Budget: {comp_fmt}</div>"

    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{formatted_val}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_kpi_row(kpis: dict) -> None:
    """Render the standard executive 6-KPI row."""
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        render_kpi_card(
            title="Total Revenue",
            value=kpis.get("revenue", 0),
            comparison_value=kpis.get("revenue_budget", 0),
            variance=kpis.get("revenue_variance"),
            variance_pct=kpis.get("revenue_variance_pct"),
            favourability=kpis.get("revenue_favourability", "neutral"),
        )
    with col2:
        render_kpi_card(
            title="Operating Expenses",
            value=kpis.get("expenses", 0),
            comparison_value=kpis.get("expenses_budget", 0),
            variance=kpis.get("expenses_variance"),
            variance_pct=kpis.get("expenses_variance_pct"),
            favourability=kpis.get("expenses_favourability", "neutral"),
        )
    with col3:
        render_kpi_card(
            title="Operating Profit",
            value=kpis.get("profit", 0),
            comparison_value=kpis.get("profit_budget", 0),
            variance=kpis.get("profit_variance"),
            variance_pct=kpis.get("profit_variance_pct"),
            favourability=kpis.get("profit_favourability", "neutral"),
        )
    with col4:
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
        )
    with col5:
        p_var = kpis.get("profit_variance", 0)
        fav = kpis.get("profit_favourability", "neutral")
        render_kpi_card(
            title="Profit Variance",
            value=p_var,
            variance_pct=kpis.get("profit_variance_pct"),
            favourability=fav,
        )
    with col6:
        # Budget fulfillment ratio
        rev = float(kpis.get("revenue", 0))
        bud_rev = float(kpis.get("revenue_budget", 0))
        achievement = (rev / bud_rev * 100) if bud_rev > 0 else 0
        render_kpi_card(
            title="Revenue Attainment",
            value=f"{achievement:.1f}%",
            favourability="favourable" if achievement >= 100 else ("neutral" if achievement >= 95 else "unfavourable"),
        )
