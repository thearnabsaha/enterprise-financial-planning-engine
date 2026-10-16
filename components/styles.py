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
COLOR_FAVOURABLE = "#10b981"       # Emerald green
COLOR_UNFAVOURABLE = "#f43f5e"     # Rose red
COLOR_WARNING = "#f59e0b"          # Amber


CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

/* Main app layout adjustments */
.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 1400px;
}}

/* Global Typography */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

h1, h2, h3, h4 {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {COLOR_TEXT_PRIMARY};
    letter-spacing: -0.025em;
    font-weight: 700;
}}

/* Header Banner */
.northstar-header {{
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 14px;
    padding: 22px 28px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 0 15px rgba(59, 130, 246, 0.08);
    backdrop-filter: blur(12px);
}}

.northstar-title {{
    font-size: 24px;
    font-weight: 800;
    color: #f8fafc;
    margin: 0;
    letter-spacing: -0.02em;
    background: linear-gradient(to right, #ffffff, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.northstar-subtitle {{
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
    font-weight: 400;
}}

.northstar-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
}}

/* Metric Card Design */
.kpi-card {{
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px 22px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    margin-bottom: 12px;
    transition: all 0.22s ease-in-out;
    position: relative;
    overflow: hidden;
}}

.kpi-card:hover {{
    transform: translateY(-3px);
    border-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 12px 28px -4px rgba(0, 0, 0, 0.45), 0 0 16px rgba(59, 130, 246, 0.15);
}}

.kpi-title {{
    font-size: 12px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.kpi-value {{
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
    margin: 8px 0 10px 0;
    line-height: 1.1;
}}

.kpi-delta {{
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
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
    background-color: rgba(16, 185, 129, 0.16);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.04em;
}}

.badge-unfavourable {{
    background-color: rgba(244, 63, 94, 0.16);
    color: #fb7185;
    border: 1px solid rgba(244, 63, 94, 0.35);
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.04em;
}}

.badge-neutral {{
    background-color: rgba(148, 163, 184, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.3);
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.04em;
}}

/* Callout Box */
.info-callout {{
    background-color: rgba(59, 130, 246, 0.08);
    border-left: 4px solid {COLOR_ACCENT};
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    margin: 16px 0;
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.5;
}}

/* Streamlit Tabs Styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background-color: rgba(15, 23, 42, 0.7);
    padding: 6px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 16px;
}}

.stTabs [data-baseweb="tab"] {{
    height: 40px;
    border-radius: 6px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 13px;
    padding: 0 18px;
    transition: all 0.2s;
}}

.stTabs [aria-selected="true"] {{
    background-color: #1e293b !important;
    color: #38bdf8 !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}}
</style>
"""


def apply_theme() -> None:
    """Inject custom CSS tokens into current Streamlit view using st.html."""
    st.html(CUSTOM_CSS)
