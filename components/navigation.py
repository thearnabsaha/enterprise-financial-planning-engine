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
    """Render top enterprise header with company branding and metadata using st.html."""
    html = f"""
    <div class="northstar-header">
        <div>
            <div class="northstar-title">{title}</div>
            <div class="northstar-subtitle">{subtitle}</div>
        </div>
        <div style="text-align: right;">
            <div style="display: flex; gap: 8px; justify-content: flex-end; margin-bottom: 6px; flex-wrap: wrap;">
                <span class="northstar-badge" style="background: rgba(59, 130, 246, 0.16); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35);">
                    🎯 Scope: {scenario_label}
                </span>
                <span class="northstar-badge" style="background: rgba(16, 185, 129, 0.16); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35);">
                    📅 {period_label}
                </span>
            </div>
            <div style="font-size: 11px; color: #94a3b8; font-weight: 500;">
                <span style="display: inline-block; width: 7px; height: 7px; background: #10b981; border-radius: 50%; margin-right: 5px; box-shadow: 0 0 6px #10b981;"></span>
                TinyOlap 4D Multidimensional Cube • Certified Decimal Precision
            </div>
        </div>
    </div>
    """
    st.html(html)


def render_footer() -> None:
    """Render standard footer disclaimer using st.html."""
    html = """
    <div style="margin-top: 36px; padding: 18px 0; border-top: 1px solid rgba(51, 65, 85, 0.7); text-align: center; font-size: 12px; color: #64748b; line-height: 1.6;">
        <strong style="color: #94a3b8;">Northstar Digital Services GmbH</strong> — Enterprise Financial Planning & Forecasting Engine<br>
        <span style="font-size: 11px; color: #475569;">Architecture: TinyOlap Multidimensional Cube • PostgreSQL/SQLite Relational Store • Streamlit Presentation</span>
    </div>
    """
    st.html(html)
