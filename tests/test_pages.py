"""
Automated tests for all Streamlit pages using AppTest.
Ensures zero runtime errors or unhandled exceptions across all 10 dashboard views.
"""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "app.py",
    "pages/01_overview_dashboard.py",
    "pages/02_upload_import.py",
    "pages/03_data_validation.py",
    "pages/04_financial_explorer.py",
    "pages/05_budget_variance.py",
    "pages/06_forecasting_scenarios.py",
    "pages/07_reports_exports.py",
    "pages/08_import_history.py",
    "pages/09_data_model_admin.py",
    "pages/10_settings_docs.py",
]


@pytest.mark.parametrize("page_path", PAGES)
def test_streamlit_page_renders_without_exception(page_path: str):
    """Verify each page executes cleanly without raising any exceptions."""
    abs_path = str(PROJECT_ROOT / page_path)
    at = AppTest.from_file(abs_path, default_timeout=30)
    at.run()
    assert not at.exception, f"Page {page_path} failed with: {[str(e.value) for e in at.exception]}"
