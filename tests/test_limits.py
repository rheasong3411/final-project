"""Spending and loop limits, demonstrated with a MOCKED model (no gpt-6-luna calls, no cost).

These prove our limits stop a runaway agent and a flooding client. They do not measure real
model behavior.
"""
import asyncio

from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import backend.api
from backend import config
from backend.agent import build_agent, run_assistant
from backend.schemas import AssistantRequest, AssistantResponse


def test_runaway_tool_loop_is_stopped_by_request_limit():
    calls = {"n": 0}

    def looping_model(messages, info: AgentInfo):
        calls["n"] += 1  # a malfunctioning model that never answers, it just keeps searching
        return ModelResponse(parts=[ToolCallPart("search_opportunities", {"query": f"cats {calls['n']}"})])

    resp, trace = asyncio.run(run_assistant(AssistantRequest(message="SYNTHETIC: help me"),
                                            agent=build_agent(FunctionModel(looping_model))))
    assert resp.ok is False and resp.error == "usage_limit_exceeded"
    assert resp.recommendations == [] and "safety limit" in resp.answer
    assert calls["n"] <= config.REQUEST_LIMIT  # stopped at the configured request limit (8), not unbounded


def test_rate_limit_rejects_flooding_client(monkeypatch):
    async def fake_run(body):  # no model call: we only test the API's per-client limit
        return AssistantResponse(run_id="x", ok=False, answer="stub", error="credentials_missing",
                                 requested_model=config.MODEL_NAME), {"latency_s": 0}
    monkeypatch.setattr(backend.api, "run_assistant", fake_run)
    monkeypatch.setattr(backend.api, "append_metrics", lambda r: None)
    backend.api._rate.clear()
    client = TestClient(backend.api.app)
    codes = [client.post("/api/assistant", json={"message": "SYNTHETIC"}).status_code
             for _ in range(config.RATE_LIMIT_PER_MINUTE + 1)]
    assert codes[:config.RATE_LIMIT_PER_MINUTE] == [200] * config.RATE_LIMIT_PER_MINUTE
    assert codes[-1] == 429
    backend.api._rate.clear()
