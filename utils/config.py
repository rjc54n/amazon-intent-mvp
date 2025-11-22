"""Configuration and secret loading for the Amazon Intent MVP.

Priority:
1. Streamlit secrets for the active context (APP_CONTEXT section if present; else root).
2. Environment variables (optionally loaded from .env).
"""

import os
from typing import Any, Mapping

from dotenv import load_dotenv

# Try to import Streamlit, but do not require it (tests / CLI may not use it).
try:
    import streamlit as st

    _HAS_STREAMLIT = True
except Exception:
    st = None  # type: ignore
    _HAS_STREAMLIT = False

# Load .env if present (safe no-op if not)
load_dotenv()

# Logical grouping / namespace for secrets, e.g. "amazon_intent", "bbx", etc.
APP_CONTEXT = os.getenv("APP_CONTEXT", "amazon_intent")


def _streamlit_context_secrets() -> Mapping[str, Any]:
    """Return a mapping of secrets for the active context, or empty if unavailable.

    Rules:
    - If Streamlit is not present, or st.secrets not available, return {}.
    - If st.secrets has a section matching APP_CONTEXT, use that.
    - Otherwise, use st.secrets as a flat mapping.
    """
    if not _HAS_STREAMLIT:
        return {}

    try:
        secrets_obj = st.secrets  # type: ignore[attr-defined]
    except Exception:
        return {}

    # secrets_obj can behave like a dict-of-dicts (toml sections)
    if APP_CONTEXT in secrets_obj:
        return secrets_obj[APP_CONTEXT]  # type: ignore[index]
    return secrets_obj  # type: ignore[return-value]


def _get_secret(name: str, default: str | None = None) -> str:
    """Get a secret by name, with priority: Streamlit -> env -> default -> error."""
    ctx_secrets = _streamlit_context_secrets()

    # 1) Try Streamlit (context section or flat)
    if name in ctx_secrets:
        value = ctx_secrets[name]
        if isinstance(value, str):
            return value
        return str(value)

    # 2) Fallback to environment variables
    env_value = os.getenv(name)
    if env_value is not None:
        return env_value

    # 3) Use default if provided
    if default is not None:
        return default

    # 4) Hard fail – required secret is missing
    raise RuntimeError(
        f"Missing required secret '{name}' in Streamlit secrets "
        f"(context '{APP_CONTEXT}') or environment variables."
    )


# Public configuration values
DATAFORSEO_API_KEY: str = _get_secret("DATAFORSEO_API_KEY")
OPENAI_API_KEY: str = _get_secret("OPENAI_API_KEY")

