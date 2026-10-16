"""
Design system, CSS styling tokens, and theme injection for Northstar Streamlit UI.
"""
from __future__ import annotations

import streamlit as st

# Color Palette Tokens
COLOR_BG_PRIMARY = "#0f1729"       # Deep navy
COLOR_BG_SECONDARY = "#1e293b"     # Card slate
COLOR_BG_TERTIARY = "#334155"      # Border / muted
COLOR_TEXT_PRIMARY = "#f8fafc"     # High contrast text
COLOR_TEXT_MUTED = "#94a3b8"       # Secondary text
COLOR_ACCENT = "#3b82f6"           # Corporate blue
COLOR_FAVOURABLE = "#10b981"       # Green
COLOR_UNFAVOURABLE = "#ef4444"     # Red
COLOR_WARNING = "#f59e0b"          # Amber


CUSTOM_CSS = f"""
<style>
/* Main app layout adjustments */
.block-container {{
    padding-top: 1.8rem;
    padding-bottom: 2.5rem;
    max-width: 1400px;
}}

/* Typography */
h1, h2, h3, h4 {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {COLOR_TEXT_PRIMARY};
    letter-spacing: -0.02em;
}}

/* Header Banner */
.northstar-header {{
    background: linear-gradient(135deg, #1e293b 0%, #0f1729 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.northstar-title {{
    font-size: 22px;
    font-weight: 700;
    color: #f8fafc;
    margin: 0;
}}

.northstar-subtitle {{
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
}}

.northstar-badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Metric Card Design */
.kpi-card {{
    background-color: {COLOR_BG_SECONDARY};
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    margin-bottom: 12px;
}}

.kpi-title {{
    font-size: 13px;
    font-weight: 600;
    color: {COLOR_TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}}

.kpi-value {{
    font-size: 26px;
    font-weight: 700;
    color: {COLOR_TEXT_PRIMARY};
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 6px;
}}

.kpi-delta {{
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 4px;
}}

.kpi-favourable {{
    color: {COLOR_FAVOURABLE};
}}

.kpi-unfavourable {{
    color: {COLOR_UNFAVOURABLE};
}}

.kpi-neutral {{
    color: {COLOR_TEXT_MUTED};
}}

/* Financial Badges */
.badge-favourable {{
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}}

.badge-unfavourable {{
    background-color: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}}

.badge-neutral {{
    background-color: rgba(148, 163, 184, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.3);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}}

/* Callout Box */
.info-callout {{
    background-color: rgba(59, 130, 246, 0.08);
    border-left: 4px solid {COLOR_ACCENT};
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    font-size: 13px;
    color: #cbd5e1;
}}
</style>
"""


def apply_theme() -> None:
    """Inject custom CSS tokens into current Streamlit view."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
