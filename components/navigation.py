"""
Navigation, header banners, and layout helpers for Streamlit pages.
"""
from __future__ import annotations

import streamlit as st


def render_header(
    title: str,
    subtitle: str = "Northstar Digital Services GmbH • Financial Planning & Analytics",
    period_label: str = "All Available Periods",
    scenario_label: str = "Actuals vs Budget",
) -> None:
    """Render top enterprise header with company branding and metadata."""
    html = f"""
    <div class="northstar-header">
        <div>
            <div class="northstar-title">{title}</div>
            <div class="northstar-subtitle">{subtitle}</div>
        </div>
        <div style="text-align: right;">
            <div style="display: flex; gap: 8px; justify-content: flex-end; margin-bottom: 4px;">
                <span class="northstar-badge" style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4);">
                    Scope: {scenario_label}
                </span>
                <span class="northstar-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);">
                    {period_label}
                </span>
            </div>
            <div style="font-size: 11px; color: #64748b;">IBM TM1 Multidimensional Engine • Precision Decimal</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_footer() -> None:
    """Render standard footer disclaimer."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-size: 12px; color: #64748b; padding: 12px 0;'>"
        "<strong>Northstar Digital Services GmbH</strong> — Enterprise Financial Planning & Forecasting Engine<br>"
        "Architecture: TinyOlap Multidimensional Cube • PostgreSQL/SQLite Relational Store • Streamlit Presentation"
        "</div>",
        unsafe_allow_html=True,
    )
