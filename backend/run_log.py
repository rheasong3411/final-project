"""Run logging: API-reported usage capture, sanitized traces, and metrics.

Usage provenance: an httpx response hook on the OpenAI client reads the JSON body of each
Portkey response and keeps only `id`, `model`, `status` and `usage`. Headers are never read
or stored. Responses-API `usage.input_tokens` already INCLUDES
`usage.input_tokens_details.cached_tokens`, so uncached input = input - cached. Nothing is
added twice and nothing is estimated. If a response has no usage object, the fields are null.
"""
from __future__ import annotations

import contextvars
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx
from pydantic_ai.messages import (ModelRequest, ModelResponse, RetryPromptPart, TextPart, ThinkingPart, ToolCallPart,
                                  ToolReturnPart, UserPromptPart)

from .config import KEY_NAME, LOCAL_METRICS, api_key

_calls: contextvars.ContextVar[list | None] = contextvars.ContextVar("provider_calls", default=None)

USAGE_PROVENANCE = ("API-reported: summed from the `usage` object in each raw Responses-API body returned by Portkey "
                    "for this run's model requests. input_tokens INCLUDES cached reads (cached_tokens) and cache writes "
                    "(cache_write_tokens); uncached = input - cached - cache_write. (Traces saved before Session 6 "
                    "reported uncached = input - cached, i.e. including cache writes; their raw usage is unchanged.)")


def start_capture() -> list:
    calls: list = []
    _calls.set(calls)
    return calls


async def capture_response(response: httpx.Response) -> None:
    """httpx response hook: record only id/model/status/usage of model responses (no headers, no content)."""
    calls = _calls.get()
    if calls is None or "application/json" not in response.headers.get("content-type", ""):
        return
    await response.aread()
    try:
        body = response.json()
    except ValueError:
        return
    if not isinstance(body, dict):
        return
    calls.append({
        # Portkey's gateway cache can replay a stored response for an identical request; that is recorded
        # here (header value only, e.g. HIT/MISS/DISABLED) so replays are never counted as fresh model runs.
        "gateway_cache_status": response.headers.get("x-portkey-cache-status"),
        "http_status": response.status_code,
        "endpoint": response.request.url.path,
        "response_id": body.get("id"),
        "returned_model": body.get("model"),
        "status": body.get("status"),
        "usage": body.get("usage"),
        "error": (body.get("error") or {}).get("message") if isinstance(body.get("error"), dict) else body.get("error"),
    })


def usage_totals(calls: list) -> dict:
    measured = [c for c in calls if isinstance(c.get("usage"), dict)]
    if not measured:
        return {"requests": len(calls), "input_tokens": None, "cached_input_tokens": None,
                "cache_write_input_tokens": None, "uncached_input_tokens": None, "output_tokens": None, "reasoning_output_tokens": None,
                "provenance": "unavailable: no usage object was returned", "requests_without_usage": len(calls)}

    def det(u, k, sub):
        d = u.get(k) or {}
        return d.get(sub) if isinstance(d, dict) else None

    inp = sum(c["usage"].get("input_tokens", 0) for c in measured)
    cached_vals = [det(c["usage"], "input_tokens_details", "cached_tokens") for c in measured]
    cached = None if any(v is None for v in cached_vals) else sum(cached_vals)
    write = sum(det(c["usage"], "input_tokens_details", "cache_write_tokens") or 0 for c in measured)
    reasoning_vals = [det(c["usage"], "output_tokens_details", "reasoning_tokens") for c in measured]
    return {
        "requests": len(calls),
        "input_tokens": inp,
        "cached_input_tokens": cached,
        "cache_write_input_tokens": write,
        "uncached_input_tokens": None if cached is None else inp - cached - write,
        "output_tokens": sum(c["usage"].get("output_tokens", 0) for c in measured),
        "reasoning_output_tokens": None if any(v is None for v in reasoning_vals) else sum(reasoning_vals),
        "provenance": USAGE_PROVENANCE,
        "requests_without_usage": len(calls) - len(measured),
        "gateway_cache_hits": sum(1 for c in calls if str(c.get("gateway_cache_status") or "").upper() in ("HIT", "SEMANTIC HIT")),
        "gateway_cache_status_values": sorted({str(c.get("gateway_cache_status")) for c in calls}),
    }


# ---------------------------------------------------------------- sanitizing
_SECRET_PATTERNS = [re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{8,}"), re.compile(r"(?i)x-portkey-api-key\s*[:=]\s*\S+")]


def scrub(value):
    """Recursively remove the API key value (and auth-header-looking strings) from any structure."""
    key = api_key()
    if isinstance(value, str):
        if key and key in value:
            value = value.replace(key, "[REDACTED]")
        for p in _SECRET_PATTERNS:
            value = p.sub("[REDACTED]", value)
        return value
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k.lower() not in {"authorization", "x-portkey-api-key", "api_key"}}
    if isinstance(value, (list, tuple)):
        return [scrub(v) for v in value]
    return value


_ZIP_TEXT = re.compile(r"(?<!\w)(?<!\d\.)\d{5}(?:-\d{4})?(?!\w)(?!\.\d)")
ZIP_REDACTED = "[ZIP redacted]"


def redact_locations(value):
    """Remove ZIP codes from anything written to disk: `zip_code` fields and any standalone 5-digit number
    in text (a person's message such as "06511"). Applied to every saved trace, synthetic or not."""
    if isinstance(value, str):
        return _ZIP_TEXT.sub(ZIP_REDACTED, value)
    if isinstance(value, dict):
        return {k: (ZIP_REDACTED if k == "zip_code" and v else redact_locations(v)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_locations(v) for v in value]
    return value


def contains_secret(text: str) -> bool:
    key = api_key()
    return bool(key and key in text) or any(p.search(text) for p in _SECRET_PATTERNS)


# ---------------------------------------------------------------- traces
def _jsonable(content):
    if hasattr(content, "model_dump"):
        return content.model_dump(mode="json")
    try:
        json.dumps(content)
        return content
    except TypeError:
        return str(content)


def messages_to_steps(messages) -> list[dict]:
    """Tool calls, tool results, retries and model responses. Hidden reasoning parts are omitted."""
    steps = []
    for m in messages:
        if isinstance(m, ModelResponse):
            parts = []
            omitted_reasoning = 0
            for p in m.parts:
                if isinstance(p, ToolCallPart):
                    parts.append({"type": "tool_call", "tool_name": p.tool_name, "tool_call_id": p.tool_call_id,
                                  "args": p.args_as_dict()})
                elif isinstance(p, TextPart):
                    parts.append({"type": "text", "content": p.content})
                elif isinstance(p, ThinkingPart):
                    omitted_reasoning += 1
            u = m.usage
            steps.append({"kind": "model_response", "model_name": m.model_name, "provider_name": m.provider_name,
                          "provider_response_id": m.provider_response_id, "finish_reason": m.finish_reason,
                          "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                          "usage_pydantic_ai": {"input_tokens": u.input_tokens, "cache_read_tokens": u.cache_read_tokens,
                                                "output_tokens": u.output_tokens},
                          "parts": parts, "reasoning_parts_omitted": omitted_reasoning})
        elif isinstance(m, ModelRequest):
            parts = []
            for p in m.parts:
                if isinstance(p, ToolReturnPart):
                    outcome = getattr(p, "outcome", None)
                    parts.append({"type": "retry_prompt" if outcome == "retried" else "tool_result",
                                  "tool_name": p.tool_name, "tool_call_id": p.tool_call_id, "outcome": outcome,
                                  "content": _jsonable(p.content)})
                elif isinstance(p, RetryPromptPart):
                    parts.append({"type": "retry_prompt", "tool_name": p.tool_name,
                                  "content": _jsonable(p.content)})
                elif isinstance(p, UserPromptPart):
                    parts.append({"type": "user_prompt", "content": _jsonable(p.content)})
            if parts:
                steps.append({"kind": "model_request", "parts": parts})
    return steps


def save_trace(trace: dict, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{trace['run_id']}.json"
    safe = redact_locations(json.loads(json.dumps(scrub(trace), default=str)))
    path.write_text(json.dumps(safe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def append_metrics(record: dict) -> None:
    """API runs: metrics only (no message text, no profile), local and gitignored."""
    LOCAL_METRICS.parent.mkdir(parents=True, exist_ok=True)
    with LOCAL_METRICS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(scrub(record), default=str) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


assert KEY_NAME  # imported so the key name, never the value, is the only thing referenced here
