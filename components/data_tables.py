"""
Financial data table rendering component with number formatting and favourability badges.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st


def render_financial_table(
    df: pd.DataFrame,
    title: str = "",
    use_container_width: bool = True,
    height: int = 400,
) -> None:
    """Render a styled DataFrame with Streamlit column configurations."""
    if title:
        st.subheader(title)

    if df.empty:
        st.info("No data available for the selected filters.")
        return

    # Column configuration map
    col_configs = {}
    for col in df.columns:
        col_lower = str(col).lower()
        if "€" in col or "amount" in col_lower or "revenue" in col_lower or "profit" in col_lower or "expenses" in col_lower:
            col_configs[col] = st.column_config.NumberColumn(
                col,
                format="€ %.2f",
            )
        elif "%" in col or "pct" in col_lower or "margin" in col_lower:
            col_configs[col] = st.column_config.NumberColumn(
                col,
                format="%.2f%%",
            )
        elif "favourability" in col_lower:
            col_configs[col] = st.column_config.TextColumn(
                col,
                help="FAVOURABLE = Exceeds target; UNFAVOURABLE = Under target / overspend",
            )

    st.dataframe(
        df,
        column_config=col_configs,
        use_container_width=use_container_width,
        height=height,
        hide_index=True,
    )
