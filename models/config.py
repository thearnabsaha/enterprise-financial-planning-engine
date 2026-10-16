"""
Application configuration using Pydantic settings.
Loads from environment variables and .env files.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    database_url: str = Field(
        default="sqlite:///northstar_local.db",
        description="PostgreSQL connection string",
    )

    # Application
    app_env: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=True, description="Enable debug logging")
    demo_mode: bool = Field(default=True, description="Show demo data generation in UI")
    app_version: str = Field(default="1.0.0", description="Application version")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # Data generation
    data_seed: int = Field(default=42, description="Random seed for synthetic data")

    # Upload limits
    max_upload_size_mb: int = Field(default=50, description="Max upload file size in MB")
    max_upload_rows: int = Field(default=100_000, description="Max rows per upload")

    # Financial defaults
    default_currency: str = Field(default="EUR", description="Default currency code")

    # Paths
    data_dir: str = Field(default="data", description="Data directory path")
    sample_data_dir: str = Field(default="data/sample", description="Sample data directory")

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "production", "testing"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Get cached application settings. Call once at startup."""
    return AppSettings()


def get_streamlit_settings() -> AppSettings:
    """
    Get settings for Streamlit deployment.
    Tries Streamlit secrets first, then falls back to env vars.
    """
    try:
        import streamlit as st

        overrides = {}
        if hasattr(st, "secrets"):
            # Read from Streamlit secrets
            if "database" in st.secrets:
                overrides["database_url"] = st.secrets["database"]["url"]
            if "app" in st.secrets:
                for key in ["environment", "debug", "demo_mode"]:
                    if key in st.secrets["app"]:
                        mapped_key = "app_env" if key == "environment" else key
                        overrides[mapped_key] = st.secrets["app"][key]
        return AppSettings(**overrides)
    except Exception:
        return get_settings()
