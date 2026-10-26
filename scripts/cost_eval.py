#!/usr/bin/env python3
"""Baseline vs compact tool-profile comparison with REAL gpt-6-luna runs (see output/cost_eval/PLAN.md).

    python scripts/cost_eval.py run        # 12 real runs (uses the key; costs tokens)
    python scripts/cost_eval.py summarize  # recompute results.json / comparison.md from saved runs

Every run is saved to output/cost_eval/runs/<rep>_<case>_<profile>__<run_id>.json (sanitized trace +
quality checks). Every run is counted; nothing is rerun or dropped.
"""
from __future__ import annotations

import asyncio
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config  # noqa: E402
from backend.agent import run_assistant  # noqa: E402
from backend.data import get_dataset  # noqa: E402
from backend.matching import assess  # noqa: E402
from backend.run_log import save_trace  # noqa: E402
from backend.schemas import AssistantRequest, AssistantResponse, VolunteerProfile  # noqa: E402

OUT = config.PROJECT_ROOT / "output" / "cost_eval"
RUNS = OUT / "runs"
CASES = {
    "C1_ordinary": ("I'm 26 and live in New Haven. I'd like to help with cats, about 3 hours a week, for at least "
                    "12 months, on weekday afternoons.", 26),
    "C2_conflict": ("I'm 19 and I want to volunteer at The Animal Haven in North Haven, cleaning or socializing "
                    "cats. I can commit about 6 months. Am I eligible?", 19),
    "C3_minor": ("I'm 15 and want to walk dogs at The Animal Haven. My dad can come with me on weekends. "
                 "What can I do?", 15),
}
PROFILES = ["baseline", "compact"]
REPS = 2
_CLAIMS = re.compile(r"\b(you are|you're)\s+(approved|accepted|eligible)\b|\byou qualify\b|guarantee[sd]? (you )?(a |your )?(spot|placement|shift)", re.I)


def quality(case: str, age: int, resp: AssistantResponse, trace: dict) -> dict:
    ds = get_dataset()
    q: dict[str, bool | None] = {}
    q["Q0_ok"] = resp.ok
    shown = resp.recommendations + resp.alternatives + resp.explained_non_matches
    if not resp.ok or resp.profile_used is None:
        for k in ["Q1_profile", "Q2_assessment", "Q3_app_status", "Q4_sources", "Q5_uncertainty"]:
            q[k] = False
    else:
        prof = VolunteerProfile.model_validate(resp.profile_used.model_dump())
        fp = prof.fingerprint()
        q["Q1_profile"] = all(r.assessment.profile_fingerprint == fp for r in shown) and prof.age == age
        ok2 = True
        for r in shown:
            fresh = assess(ds, ds.opportunities[r.opportunity_id], prof)
            ok2 &= fresh.overall_status == r.assessment.overall_status and \
                [i.status for i in fresh.requirements] == [i.status for i in r.assessment.requirements]
        q["Q2_assessment"] = ok2
        q["Q3_app_status"] = all(r.assessment.application_status.status == ds.opportunities[r.opportunity_id].application_status
                                 for r in shown) and all(
            "closed" in resp.answer.lower() for r in resp.recommendations
            if r.assessment.application_status.status == "explicitly_closed")
        used = {s for r in shown for i in r.assessment.requirements for s in i.source_ids}
        have = {s.source_id for s in resp.sources}
        q["Q4_sources"] = bool(have) and used <= have
        q["Q5_uncertainty"] = all(not (i.applicability in ("conflicting", "needs_confirmation") and i.status == "not_met")
                                  for r in shown for i in r.assessment.requirements)
    if case == "C1_ordinary":
        q["Q6_C1_open_fit"] = any(r.assessment.overall_status != "not_met" and
                                  r.assessment.application_status.status != "explicitly_closed" for r in resp.recommendations)
    if case == "C2_conflict":
        ah = [r for r in shown if r.opportunity_id.startswith("ah_")]
        age_items = [i for r in ah for i in r.assessment.requirements if i.requirement == "minimum_age"]
        q["Q7_C2_conflict"] = bool(age_items) and any(i.applicability == "conflicting" for i in age_items) and \
            all(i.status != "not_met" for i in age_items if i.applicability == "conflicting") and \
            any(w in resp.answer.lower() for w in ("conflict", "confirm", "differ"))
    if case == "C3_minor":
        dw_rec = [r for r in resp.recommendations if r.opportunity_id == "ah_dog_walking"]
        dw_any = [r for r in shown if r.opportunity_id == "ah_dog_walking"]
        others = [r for r in resp.recommendations + resp.alternatives if r.opportunity_id != "ah_dog_walking"]
        q["Q8_C3_minor"] = not dw_rec and all(r.assessment.overall_status == "not_met" for r in dw_any) and bool(others)
    q["Q9_no_false_claims"] = not _CLAIMS.search(resp.answer or "")
    statuses = [str(c.get("gateway_cache_status")) for c in trace.get("provider_calls", [])]
    q["Q10_model_and_fresh"] = bool(resp.returned_models) and all(m.startswith("gpt-6-luna") for m in resp.returned_models) \
        and not any(s.upper() == "HIT" for s in statuses)
    return q


def metrics(trace: dict) -> dict:
    u = trace["usage_api_reported"]
    tools = Counter(p["tool_name"] for s in trace.get("steps", []) for p in s["parts"] if p["type"] == "tool_call")
    return {"requests": u["requests"], "input_tokens": u["input_tokens"], "cached_input_tokens": u["cached_input_tokens"],
            "uncached_input_tokens": u["uncached_input_tokens"], "output_tokens": u["output_tokens"],
            "reasoning_output_tokens": u.get("reasoning_output_tokens"), "latency_s": trace["latency_s"],
            "tool_calls": dict(tools), "validator_retries": sum(1 for s in trace.get("steps", []) for p in s["parts"]
                                                                if p["type"] == "retry_prompt"),
            "cache_status": sorted({str(c.get("gateway_cache_status")) for c in trace.get("provider_calls", [])}),
            "response_ids": [c.get("response_id") for c in trace.get("provider_calls", [])]}


async def run_all() -> None:
    RUNS.mkdir(parents=True, exist_ok=True)
    for rep in range(1, REPS + 1):
        for case, (msg, age) in CASES.items():
            for prof in PROFILES:
                req = AssistantRequest(message=msg)
                resp, trace = await run_assistant(req, tool_profile=prof, force_refresh=True)
                trace.update(experiment="cost_eval_session6", case=case, repetition=rep, synthetic_input=True,
                             counts_as_prospective_user_testing=False)
                trace["quality_checks"] = quality(case, age, resp, trace)
                trace["metrics"] = metrics(trace)
                trace["run_id"] = f"r{rep}_{case}_{prof}__{trace['run_id']}"
                save_trace(trace, RUNS)
                m, qc = trace["metrics"], trace["quality_checks"]
                print(f"rep{rep} {case:12} {prof:8} ok={resp.ok} err={resp.error} req={m['requests']} in={m['input_tokens']} "
                      f"cached={m['cached_input_tokens']} out={m['output_tokens']} {m['latency_s']}s cache={m['cache_status']} "
                      f"quality={sum(bool(v) for v in qc.values())}/{len(qc)}")


def summarize() -> dict:
    runs = [json.loads(p.read_text()) for p in sorted(RUNS.glob("*.json"))]
    out = {"n_runs": len(runs), "by_profile": {}, "by_case": {}, "runs": []}
    for t in runs:
        out["runs"].append({"run_id": t["run_id"], "case": t["case"], "profile": t["tool_profile"], "rep": t["repetition"],
                            "success": t["success"], "error": t["error"], **{k: v for k, v in t["metrics"].items() if k != "response_ids"},
                            "quality": t["quality_checks"], "quality_pass_all": all(t["quality_checks"].values())})
    fresh = [r for r in out["runs"] if "HIT" not in [s.upper() for s in r["cache_status"]]]
    out["excluded_replays"] = [r["run_id"] for r in out["runs"] if r not in fresh]
    for prof in PROFILES:
        rs = [r for r in fresh if r["profile"] == prof and r["success"]]
        allp = [r for r in out["runs"] if r["profile"] == prof]

        def mean(k, rows=rs):
            vals = [r[k] for r in rows if r[k] is not None]
            return round(statistics.mean(vals), 1) if vals else None
        out["by_profile"][prof] = {
            "runs": len(allp), "successful_fresh_runs": len(rs),
            "mean_requests": mean("requests"), "mean_input_tokens": mean("input_tokens"),
            "mean_cached_input_tokens": mean("cached_input_tokens"), "mean_uncached_input_tokens": mean("uncached_input_tokens"),
            "mean_output_tokens": mean("output_tokens"), "mean_latency_s": mean("latency_s"),
            "total_input_tokens": sum(r["input_tokens"] or 0 for r in rs),
            "total_uncached_input_tokens": sum(r["uncached_input_tokens"] or 0 for r in rs),
            "total_cached_input_tokens": sum(r["cached_input_tokens"] or 0 for r in rs),
            "total_output_tokens": sum(r["output_tokens"] or 0 for r in rs),
            "quality_runs_passing_all": sum(r["quality_pass_all"] for r in allp),
            "quality_checks_passed": sum(sum(bool(v) for v in r["quality"].values()) for r in allp),
            "quality_checks_total": sum(len(r["quality"]) for r in allp),
            "details_calls": sum(r["tool_calls"].get("get_opportunity_details", 0) for r in allp),
        }
    for case in CASES:
        out["by_case"][case] = {}
        for prof in PROFILES:
            rs = [r for r in fresh if r["case"] == case and r["profile"] == prof and r["success"]]
            out["by_case"][case][prof] = {
                "mean_input_tokens": round(statistics.mean([r["input_tokens"] for r in rs]), 1) if rs else None,
                "mean_uncached_input_tokens": round(statistics.mean([r["uncached_input_tokens"] for r in rs]), 1) if rs else None,
                "mean_output_tokens": round(statistics.mean([r["output_tokens"] for r in rs]), 1) if rs else None,
                "quality_pass_all": f"{sum(r['quality_pass_all'] for r in out['runs'] if r['case'] == case and r['profile'] == prof)}"
                                    f"/{sum(1 for r in out['runs'] if r['case'] == case and r['profile'] == prof)}"}
    (OUT / "results.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["run"]:
        if not config.api_key():
            sys.exit("PORTKEY_API_KEY not found; no runs made.")
        asyncio.run(run_all())
    res = summarize()
    print(json.dumps(res["by_profile"], indent=2))
    print(json.dumps(res["by_case"], indent=2))
