"""API routes and credential handling. No model calls (the assistant route is tested without credentials)."""
import pytest
from fastapi.testclient import TestClient

from backend import config
from backend.api import app

client = TestClient(app)
FAKE_KEY = "pk-test-FAKE-0123456789abcdef"  # synthetic, never a real credential


def test_health_reports_readiness_without_secret(monkeypatch):
    monkeypatch.setenv(config.KEY_NAME, FAKE_KEY)
    body = client.get("/api/health").text
    assert FAKE_KEY not in body and '"credentials_present":true' in body.replace(" ", "")
    assert "/Users/" not in body  # no absolute local paths


def test_filters_and_default_scope():
    f = client.get("/api/filters").json()
    assert f["geographic_scopes"]["default"] == "greater_new_haven"
    r = client.get("/api/opportunities").json()
    assert r["count"] > 0 and {x["geographic_scope"] for x in r["results"]} == {"greater_new_haven"}
    assert {x["record_type"] for x in r["results"]} == {"described_volunteer_role"}
    allr = client.get("/api/opportunities", params={"scope": "all"}).json()
    assert allr["count"] > r["count"]


def test_detail_has_evidence_sources_and_checklist():
    d = client.get("/api/opportunities/chs_newington_group_trails").json()
    assert d["record"]["commitment_type"] == "one_time"
    assert d["sources"] and all(s["url"].startswith("http") for s in d["sources"])
    assert d["application_checklist"]
    assert client.get("/api/opportunities/nope").status_code == 404


def test_assess_route_and_profile_privacy():
    r = client.post("/api/opportunities/ah_dog_walking/assess", json={"profile": {"age": 19}})
    assert r.status_code == 200 and r.json()["overall_status"] == "not_met"
    for extra in ({"birth_date": "2007-01-01"}, {"address": "1 Main St"}, {"medical_history": "x"}):
        assert client.post("/api/opportunities/ah_dog_walking/assess", json={"profile": {"age": 19, **extra}}).status_code == 422
    assert client.post("/api/opportunities/ah_dog_walking/assess", json={"profile": {"age": -3}}).status_code == 422


def test_assistant_without_credentials_gives_clear_error(monkeypatch):
    import backend.api
    monkeypatch.setattr(config, "api_key", lambda: None)
    monkeypatch.setattr(backend.api, "append_metrics", lambda record: None)  # tests never write run metrics
    r = client.post("/api/assistant", json={"message": "I'm 30 and like cats"})
    body = r.json()
    assert r.status_code == 200 and body["ok"] is False and body["error"] == "credentials_missing"
    assert body["recommendations"] == [] and body["requirement_assessments"] == []


def test_assistant_input_limits():
    assert client.post("/api/assistant", json={"message": "x" * 2001}).status_code == 422
    assert client.post("/api/assistant", json={"message": ""}).status_code == 422


@pytest.mark.parametrize("env_has_key", [True, False])
def test_env_precedence(tmp_path, env_has_key):
    proj, parent = tmp_path / "proj.env", tmp_path / "parent.env"
    proj.write_text(f"{config.KEY_NAME}=from-project\n")
    parent.write_text(f"{config.KEY_NAME}=from-parent\n")
    environ = {config.KEY_NAME: "from-environment"} if env_has_key else {}
    src = config.load_credentials(environ, [("project .env", proj), ("parent-folder .env", parent)])
    if env_has_key:
        assert src == "environment" and environ[config.KEY_NAME] == "from-environment"  # never overridden
    else:
        assert src == "project .env" and environ[config.KEY_NAME] == "from-project"


def test_env_parent_used_when_project_missing(tmp_path):
    parent = tmp_path / "parent.env"
    parent.write_text(f"{config.KEY_NAME}=from-parent\n")
    environ = {}
    assert config.load_credentials(environ, [("project .env", tmp_path / "none.env"),
                                             ("parent-folder .env", parent)]) == "parent-folder .env"


def test_env_nothing_found(tmp_path):
    assert config.load_credentials({}, [("project .env", tmp_path / "a"), ("parent-folder .env", tmp_path / "b")]) is None
