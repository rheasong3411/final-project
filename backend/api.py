"""FastAPI routes. Start with:  uvicorn backend.api:app --port 8000   (from animal-volunteer/)."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import time
from collections import defaultdict, deque
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config
from .agent import run_assistant
from .data import get_dataset
from .geo import get_geo
from .matching import assess, checklist, find_alternatives
from .run_log import append_metrics, save_trace
from .schemas import Assessment, AssistantRequest, AssistantResponse, VolunteerProfile

app = FastAPI(title="Animal Volunteer Finder API", version="0.1.0",
              description="Greater New Haven animal-volunteering data, deterministic matching and an AI assistant. "
                          "Helps people prepare to apply; never approves volunteers or guarantees openings.")

_rate: dict[str, deque] = defaultdict(deque)
_run_slots = asyncio.Semaphore(config.MAX_CONCURRENT_RUNS)


def _ds():
    return get_dataset()


def _opp_or_404(opportunity_id: str):
    o = _ds().opportunities.get(opportunity_id)
    if o is None:
        raise HTTPException(404, f"Unknown opportunity_id '{opportunity_id}'")
    return o


@app.get("/api/health")
def health() -> dict:
    ds = _ds()
    return {"status": "ok", "data": {"organizations": len(ds.organizations), "opportunities": len(ds.opportunities),
                                     "sources": len(ds.sources)},
            "assistant": config.readiness()}


@app.get("/api/organizations")
def organizations() -> list[dict]:
    ds = _ds()
    return [o.model_dump(exclude={"field_evidence"}) for o in ds.organizations.values()]


@app.get("/api/filters")
def filters() -> dict:
    return _ds().filter_values()


RecordTypeParam = Literal["described_volunteer_role", "interest_area_only", "independent_support_activity"]


@app.get("/api/opportunities")
def list_opportunities(
        scope: Literal["greater_new_haven", "wider_connecticut", "all"] = "greater_new_haven",
        town: str | None = Query(None, max_length=60),
        organization_id: str | None = None,
        activity: list[str] | None = Query(None),
        animal: list[str] | None = Query(None),
        record_type: list[RecordTypeParam] | None = Query(None, description="Default: described_volunteer_role only"),
        commitment_type: str | None = None,
        include_closed: bool = Query(False, description="Records whose applications are explicitly closed are left "
                                                        "out by default; detail pages still show them."),
        q: str | None = Query(None, max_length=100)) -> dict:
    ds = _ds()
    args = dict(include_wider_connecticut=(scope == "all"), scope=None if scope == "all" else scope, town=town,
                organization_id=organization_id, activities=activity, animals=animal, record_types=record_type,
                commitment_type=commitment_type, query=q)
    hits = ds.search(**args, include_closed=include_closed)
    hidden_closed = 0 if include_closed else len(ds.search(**args, include_closed=True)) - len(hits)
    geo = get_geo()
    return {"count": len(hits), "scope": scope, "closed_hidden": hidden_closed,
            "record_types": record_type or ["described_volunteer_role"],
            "results": [{**ds.summary(o), "location": geo.location_of(o.opportunity_id),
                         "next_actions": ds.next_actions(o)} for o in hits],
            "note": None if hits else "No records matched. Try fewer filters or another town."}


@app.get("/api/opportunities/{opportunity_id}")
def opportunity_detail(opportunity_id: str) -> dict:
    ds = _ds()
    o = _opp_or_404(opportunity_id)
    return {**ds.details(o), "location": get_geo().location_of(o.opportunity_id),
            "application_checklist": checklist(ds, o)}


class LocationEstimatesRequest(BaseModel):
    """POST (not GET) so a ZIP code never appears in a URL, browser history or server access log."""
    zip_code: str = Field(max_length=10)
    opportunity_ids: list[str] = Field(default_factory=list, max_length=100)


@app.post("/api/location/estimates")
def location_estimates(body: LocationEstimatesRequest) -> dict:
    """Check a ZIP (format / in dataset / Connecticut coverage) and estimate straight-line distances.

    Closeness is reported separately and never changes fit or application status. Nothing is logged.
    """
    ds, geo = _ds(), get_geo()
    zc = geo.check_zip(body.zip_code)
    ids = [i for i in dict.fromkeys(body.opportunity_ids) if i in ds.opportunities]
    return {"zip_area": zc.public(),
            "estimates": {i: {**geo.location_of(i), "distance": geo.distance(i, zc)} for i in ids},
            "method": "Straight-line (great-circle) distance from the Census ZIP Code Tabulation Area's internal point "
                      "to the verified volunteering site, rounded. Not from your home, and not a driving, walking or "
                      "transit distance.",
            "sources": {"zip_areas": geo.meta["dataset"], "sites": "Official organization pages, verified 2026-10-25; "
                                                                  "coordinates from the U.S. Census Geocoder"}}


class AssessRequest(BaseModel):
    profile: VolunteerProfile


@app.post("/api/opportunities/{opportunity_id}/assess", response_model=Assessment)
def assess_opportunity(opportunity_id: str, body: AssessRequest) -> Assessment:
    return assess(_ds(), _opp_or_404(opportunity_id), body.profile)


@app.post("/api/alternatives")
def alternatives(body: AssessRequest, exclude_opportunity_id: str | None = None) -> dict:
    return {"alternatives": find_alternatives(_ds(), body.profile, exclude_id=exclude_opportunity_id)}


@app.post("/api/assistant", response_model=AssistantResponse)
async def assistant(body: AssistantRequest, request: Request) -> AssistantResponse:
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = _rate[client]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= config.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(429, "Too many assistant requests; please wait a minute.")
    window.append(now)
    async with _run_slots:
        resp, trace = await run_assistant(body)
    if os.environ.get("AVF_SAVE_TRACES") == "1":
        # Evidence mode for SYNTHETIC UI testing only (off by default). Ordinary users' conversations are
        # never written to output/; normal runs only append the metrics line below.
        case = os.environ.get("AVF_TRACE_CASE", "ui_integrated")  # label for a scripted synthetic test session
        trace.update(case=f"{case}_synthetic", synthetic_input=True, counts_as_prospective_user_testing=False,
                     workflow="POST /api/assistant from the React frontend",
                     privacy="ZIP codes are redacted from saved traces (run_log.redact_locations).")
        trace["run_id"] = f"{case}__{trace['run_id']}"
        # AVF_TRACE_DIR: a new run-specific folder (e.g. output/owner_testing/<date-time>/traces), so a test session
        # never writes into or over earlier evidence.
        save_trace(trace, Path(os.environ["AVF_TRACE_DIR"]) if os.environ.get("AVF_TRACE_DIR") else config.RUNS_DIR)
    append_metrics({"run_id": resp.run_id, "at": trace.get("started_at"), "ok": resp.ok, "error": resp.error,
                    "latency_s": trace.get("latency_s"), "returned_models": resp.returned_models,
                    "usage": trace.get("usage_api_reported")})
    return resp


# ---------------------------------------------------------------- production frontend (optional)
FRONTEND_DIST = config.PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        """Serve built files; any other non-API path returns index.html so client routes load directly."""
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(404, "Unknown API route")
        candidate = (FRONTEND_DIST / full_path).resolve()
        if full_path and candidate.is_file() and FRONTEND_DIST.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
