"""Configuration: paths, model, limits and credential loading.

.env precedence (first value found wins; nothing is ever overridden):
  1. A variable already set in the process environment.
  2. <repo root>/.env           (animal-volunteer/.env)
  3. <repo root>/../.env        (the folder one level above the repo; the course staff layout)
No other directories are searched. The key value is never printed, logged or returned.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RUNS_DIR = PROJECT_ROOT / "output" / "agent_runs"          # sanitized evidence runs (synthetic profiles)
LOCAL_METRICS = PROJECT_ROOT / "local_data" / "api_run_metrics.jsonl"  # gitignored; no message text

# ---- model (assignment: course key -> gpt-6-luna only)
MODEL_NAME = "gpt-6-luna"
PROVIDER = "portkey"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"  # Portkey docs: OpenAI-compatible gateway base URL
KEY_NAME = "PORTKEY_API_KEY"

# ---- limits (one conversation cannot loop or run up cost)
MAX_MESSAGE_CHARS = 2000
MAX_HISTORY_TURNS = 10
REQUEST_LIMIT = 8            # model requests per assistant call
TOOL_CALLS_LIMIT = 14        # tool calls per assistant call
TOTAL_TOKENS_LIMIT = 120_000  # input + output tokens per assistant call
MAX_OUTPUT_TOKENS = 4000     # per model response
MODEL_REQUEST_TIMEOUT_S = 60
RUN_TIMEOUT_S = 180
OUTPUT_RETRIES = 2           # retries when the structured output fails validation
RATE_LIMIT_PER_MINUTE = 6    # assistant calls per client per minute
MAX_CONCURRENT_RUNS = 2
MAX_SEARCH_RESULTS = 8

# ---- cost configuration (Session 6 experiment; see output/cost_eval/)
# "baseline": tools/instructions exactly as in Sessions 3-5. "compact" (default): slimmer get_opportunity_details
# (no fields already returned by assess_profile; evidence quotes only on request) + one instruction line.
# Default is "compact" since the Session 6 comparison (equal quality, ~33% lower model cost per run).
TOOL_PROFILE = os.environ.get("AVF_TOOL_PROFILE", "compact")
# Portkey documented header: bypass the gateway cache for a fresh call (response cache status "REFRESH").
CACHE_FORCE_REFRESH = os.environ.get("AVF_CACHE_FORCE_REFRESH") == "1"

_ENV_CANDIDATES = [("project .env", PROJECT_ROOT / ".env"), ("parent-folder .env", PROJECT_ROOT.parent / ".env")]


def load_credentials(environ=os.environ, candidates=None) -> str | None:
    """Return where PORTKEY_API_KEY came from (never its value), loading it into `environ` if needed.

    An existing environment value is never overridden; then <repo>/.env; then <repo>/../.env.
    """
    if environ.get(KEY_NAME):
        return "environment"
    for label, path in (candidates or _ENV_CANDIDATES):
        if Path(path).is_file():
            value = dotenv_values(path).get(KEY_NAME)
            if value:
                environ.setdefault(KEY_NAME, value)
                return label
    return None


CREDENTIAL_SOURCE = load_credentials()


def api_key() -> str | None:
    return os.environ.get(KEY_NAME) or None


def readiness() -> dict:
    return {
        "model": MODEL_NAME,
        "provider": PROVIDER,
        "gateway_base_url": PORTKEY_BASE_URL,
        "credentials_present": api_key() is not None,
        "credential_source": CREDENTIAL_SOURCE if api_key() else None,
        "supported_env_locations": ["process environment", "<repo root>/.env", "<folder above repo root>/.env"],
    }
