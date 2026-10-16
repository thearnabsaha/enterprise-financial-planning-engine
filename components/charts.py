"""
Interactive Plotly charts styled to match the dark navy / slate enterprise design system.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Design system colors
COLOR_NAVY = "#0f1729"
COLOR_CARD = "#1e293b"
COLOR_GRID = "#334155"
COLOR_TEXT = "#f8fafc"
COLOR_MUTED = "#94a3b8"
COLOR_BLUE = "#3b82f6"
COLOR_CYAN = "#06b6d4"
COLOR_GREEN = "#10b981"
COLOR_RED = "#ef4444"
COLOR_AMBER = "#f59e0b"
COLOR_PURPLE = "#8b5cf6"

CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLOR_TEXT, family="Inter, sans-serif"),
    xaxis=dict(gridcolor=COLOR_GRID, zerolinecolor=COLOR_GRID),
    yaxis=dict(gridcolor=COLOR_GRID, zerolinecolor=COLOR_GRID),
    margin=dict(l=40, r=20, t=40, b=40),
)


def chart_revenue_vs_budget(trend_df: pd.DataFrame) -> go.Figure:
    """Revenue vs Budget monthly comparison bar + line combo chart."""
    fig = go.Figure()

    scenarios = trend_df["scenario"].unique()
    colors = {
        "Actuals": COLOR_BLUE,
        "Original Budget": COLOR_AMBER,
        "Revised Budget": COLOR_CYAN,
        "Forecast v1": COLOR_PURPLE,
    }

    for scn in scenarios:
        sub = trend_df[trend_df["scenario"] == scn].sort_values("period")
        color = colors.get(scn, COLOR_CYAN)
        if scn == "Actuals":
            fig.add_trace(go.Bar(
                x=sub["period"],
                y=sub["revenue"],
                name=f"{scn} Revenue",
                marker_color=color,
                opacity=0.85,
            ))
        else:
            fig.add_trace(go.Scatter(
                x=sub["period"],
                y=sub["revenue"],
                name=f"{scn} Revenue",
                mode="lines+markers",
                line=dict(color=color, width=2.5, dash="dash" if "Budget" in scn else "solid"),
            ))

    fig.update_layout(
        title="Monthly Revenue: Actuals vs Targets",
        yaxis_title="Revenue (€)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_THEME,
    )
    return fig


def chart_monthly_profit_trend(trend_df: pd.DataFrame) -> go.Figure:
    """Monthly Operating Profit trend line chart."""
    fig = go.Figure()

    for scn in trend_df["scenario"].unique():
        sub = trend_df[trend_df["scenario"] == scn].sort_values("period")
        is_actual = scn == "Actuals"
        fig.add_trace(go.Scatter(
            x=sub["period"],
            y=sub["profit"],
            name=f"{scn} Profit",
            mode="lines+markers",
            line=dict(
                color=COLOR_GREEN if is_actual else COLOR_MUTED,
                width=3 if is_actual else 1.5,
                dash="solid" if is_actual else "dash",
            ),
        ))

    # Add zero reference line
    fig.add_hline(y=0, line_dash="dot", line_color="#64748b", annotation_text="Break-even")

    fig.update_layout(
        title="Operating Profit Trend (€)",
        yaxis_title="Profit / (Loss) €",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_THEME,
    )
    return fig


def chart_expense_donut(account_df: pd.DataFrame) -> go.Figure:
    """Donut chart showing breakdown of expenses by account."""
    expenses = account_df[account_df["Category"] == "Expense"].copy()
    if expenses.empty:
        return go.Figure()

    # Expenses are negative numbers, convert to positive magnitudes for donut
    expenses["Magnitude"] = expenses["Actual (€)"].abs()

    fig = px.pie(
        expenses,
        names="Account Name",
        values="Magnitude",
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Dark24,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color=COLOR_CARD, width=2)),
    )
    fig.update_layout(
        title="Operating Expense Composition",
        showlegend=False,
        **CHART_THEME,
    )
    return fig


def chart_department_breakdown(dept_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart comparing Actual vs Budget Profit by department."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=dept_df["Department"],
        y=dept_df["Actual Profit (€)"],
        name="Actual Profit",
        marker_color=COLOR_BLUE,
    ))

    fig.add_trace(go.Bar(
        x=dept_df["Department"],
        y=dept_df["Budget Profit (€)"],
        name="Budget Profit",
        marker_color=COLOR_AMBER,
    ))

    fig.update_layout(
        title="Department Profitability: Actual vs Budget",
        barmode="group",
        yaxis_title="Profit (€)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_THEME,
    )
    return fig


def chart_waterfall_variance(
    budget_profit: float,
    actual_profit: float,
    dept_df: pd.DataFrame,
) -> go.Figure:
    """Waterfall chart explaining walk from Budget Profit to Actual Profit."""
    x = ["Budget Profit"]
    y = [budget_profit]
    measure = ["absolute"]

    for _, row in dept_df.iterrows():
        dept_name = str(row["Department"])
        var = float(row["Profit Variance (€)"])
        x.append(dept_name)
        y.append(var)
        measure.append("relative")

    x.append("Actual Profit")
    y.append(actual_profit)
    measure.append("total")

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measure,
        x=x,
        textposition="outside",
        text=[f"{v/1000:+,.1f}k" if m == "relative" else f"{v/1000:,.1f}k" for v, m in zip(y, measure)],
        y=y,
        connector={"line": {"color": "#64748b"}},
        decreasing={"marker": {"color": COLOR_RED}},
        increasing={"marker": {"color": COLOR_GREEN}},
        totals={"marker": {"color": COLOR_BLUE}},
    ))

    fig.update_layout(
        title="Profit Variance Bridge: Budget to Actual (€k)",
        yaxis_title="Profit (€)",
        **CHART_THEME,
    )
    return fig


def chart_scenario_comparison(comparison_df: pd.DataFrame) -> go.Figure:
    """Multi-scenario comparison area/lines over time."""
    fig = go.Figure()

    colors = [COLOR_BLUE, COLOR_GREEN, COLOR_AMBER, COLOR_PURPLE, COLOR_CYAN, "#ec4899"]
    scenarios = [c for c in comparison_df.columns if c != "Period"]

    for idx, scn in enumerate(scenarios):
        color = colors[idx % len(colors)]
        fig.add_trace(go.Scatter(
            x=comparison_df["Period"],
            y=comparison_df[scn],
            name=scn,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
        ))

    fig.update_layout(
        title="Scenario Projection Trajectories",
        yaxis_title="Amount (€)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_THEME,
    )
    return fig
