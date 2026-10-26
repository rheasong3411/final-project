#!/usr/bin/env python3
"""Cost of the CURRENT agent (Session 11), measured on real runs. Kept separate from the Session 6 experiment.

    python scripts/current_cost.py

The Session 6 experiment (output/cost_eval/comparison.md, tokenomics.md) compared the baseline and compact tool
profiles with 5 tools and the agent as it was then; it is a historical result and is NOT recomputed here.
This script prices a new, small set of fresh runs (Portkey force-refresh, gateway status REFRESH) of the
current agent: 6 tools, location memory, structured replies. Same billing rule and course rates as
scripts/tokenomics.py. Writes output/cost_eval/current_agent_session11.{json,md}.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from tokenomics import RATE_SOURCE, cost, run_tokens  # noqa: E402

RUNS = ROOT / "output" / "agent_runs"
RATES = {"input": 0.10, "cached": 0.01, "cache_write": 0.125, "output": 0.50}
# The measured set (all synthetic inputs, all run on 2026-10-25 with the code of Session 11):
CASES = ["01_normal_match__70752b750789", "02_conflict_animal_haven__52bfc19dfc47", "03_prompt_injection__8d3d0cc4108b",
         "03b_prompt_injection_subtle__b840904b49aa", "04_impossible_request__91b5939fa61f", "05_vague_request__83e8899391a3"]


def main() -> dict:
    groups = {"standard_cases": [RUNS / f"{c}.json" for c in CASES],
              "website_location_conversation": sorted(RUNS.glob("ui_s11__*.json"))}
    out = {"rates_usd_per_1m": RATES, "rate_source": RATE_SOURCE, "groups": {}, "excluded": []}
    allc = []
    for g, files in groups.items():
        rows = []
        for f in files:
            t = json.loads(f.read_text())
            tok = run_tokens(t)
            statuses = sorted({str(c.get("gateway_cache_status")) for c in t.get("provider_calls", [])})
            if tok is None:
                out["excluded"].append({"run": f.stem, "reason": t.get("error") or "no usage (or gateway replay)"})
                continue
            rows.append({"run": f.stem, **tok, "gateway": statuses, "latency_s": t.get("latency_s"),
                         "cost_usd": round(cost(tok, RATES), 6)})
        costs = [r["cost_usd"] for r in rows]
        allc += costs
        out["groups"][g] = {"n": len(rows), "runs": rows,
                            "mean_cost_usd": round(statistics.mean(costs), 6), "median_cost_usd": round(statistics.median(costs), 6),
                            "mean_input": round(statistics.mean(r["input"] for r in rows)),
                            "mean_cached": round(statistics.mean(r["cached"] for r in rows)),
                            "mean_output": round(statistics.mean(r["output"] for r in rows)),
                            "mean_requests": round(statistics.mean(r["requests"] for r in rows), 1)}
    out["all"] = {"n": len(allc), "mean_cost_usd": round(statistics.mean(allc), 6), "median_cost_usd": round(statistics.median(allc), 6),
                  "min_cost_usd": min(allc), "max_cost_usd": max(allc)}
    m = out["all"]["mean_cost_usd"]
    out["scaling_same_assumption_as_session6"] = {"runs_per_user_month": 4, "per_user_month": round(4 * m, 4),
                                                  "users_100": round(400 * m, 2), "users_10000": round(40000 * m, 2)}
    (ROOT / "output" / "cost_eval" / "current_agent_session11.json").write_text(json.dumps(out, indent=1) + "\n")
    lines = ["# Current agent cost (Session 11, 2026-10-25) — measured separately from the Session 6 experiment", "",
             "**What this is:** fresh real runs (Portkey force-refresh; gateway status `REFRESH`) of the agent as it is now:",
             "6 tools (adds `update_location_preferences`), location memory, structured replies. Synthetic inputs.",
             "**What it is not:** the Session 6 baseline-vs-compact experiment (`comparison.md`, `tokenomics.md`), which",
             "measured the 5-tool agent of that time. Those figures are historical and are not mixed with these.", "",
             f"Rates (USD per 1M tokens): input ${RATES['input']}, cached ${RATES['cached']}, cache write ${RATES['cache_write']}, "
             f"output ${RATES['output']}. {RATE_SOURCE}", "",
             "| Group | n | Mean requests | Mean input | Mean cached | Mean output | Mean $/run | Median $/run |", "|---|---|---|---|---|---|---|---|"]
    for g, v in out["groups"].items():
        lines.append(f"| {g} | {v['n']} | {v['mean_requests']} | {v['mean_input']:,} | {v['mean_cached']:,} | {v['mean_output']:,} | "
                     f"${v['mean_cost_usd']:.5f} | ${v['median_cost_usd']:.5f} |")
    a = out["all"]; s = out["scaling_same_assumption_as_session6"]
    lines += ["", f"All {a['n']} priced runs: mean ${a['mean_cost_usd']:.5f}, median ${a['median_cost_usd']:.5f} "
              f"(range ${a['min_cost_usd']:.5f}–${a['max_cost_usd']:.5f}) per run.",
              f"Same scaling assumption as Session 6 (4 runs per active user per month): ${s['per_user_month']:.4f} per user per "
              f"month; ${s['users_100']:.2f} for 100 users; ${s['users_10000']:.2f} for 10,000 users (model cost only, modeled, "
              "not a bill).", "", "Excluded (no tokens were generated): " +
              (", ".join(f"`{e['run']}` ({e['reason']})" for e in out["excluded"]) or "none"), "",
              "Small sample: 18 runs (17 priced), chosen to cover the standard test cases and the location conversation; not a "
              "measurement of real users' traffic."]
    (ROOT / "output" / "cost_eval" / "current_agent_session11.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out


if __name__ == "__main__":
    main()
