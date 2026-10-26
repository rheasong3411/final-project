#!/usr/bin/env python3
"""Tokenomics from REAL, API-reported usage in saved traces.

    python scripts/tokenomics.py                       # default rates (see RATE_SOURCE) and assumptions
    python scripts/tokenomics.py --input 0.10 --cached 0.01 --cache-write 0.125 --output 0.50 --runs-per-user-month 4

Rates are USD per 1M tokens. Billing rule (course Lecture 11, consistent with OpenAI's usage fields):
  input_tokens INCLUDES cached reads and cache writes, so
  uncached = input - cached_read - cache_write, billed at the input rate;
  cached_read at the cached rate; cache_write at the cache-write rate; output_tokens (which include
  reasoning tokens) at the output rate. Nothing is counted twice.
Usage comes from the raw `usage` object of each provider response (provider_calls in each trace).
Gateway-cache replays (cache status HIT) are excluded: they are not fresh generation.
Writes output/cost_eval/tokenomics.json and output/cost_eval/tokenomics.md.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "cost_eval"
RATE_SOURCE = ("Course Lecture 11 (Tokenomics) slides and vibe page, https://zlisto.github.io/mgt_409_fa26/lectures/"
               "slides/lec11-slides.html, which cite https://developers.openai.com/api/docs/pricing; both accessed "
               "2026-10-25. gpt-6-luna, Standard tier, short context (<=272K): input $0.10, cached input $0.01, "
               "30-minute cache write $0.125, output $0.50 per 1M tokens (USD). No date is printed on either page.")


def run_tokens(trace: dict) -> dict | None:
    calls = trace.get("provider_calls", [])
    if any(str(c.get("gateway_cache_status") or "").upper() == "HIT" for c in calls):
        return None  # replay, not fresh generation
    us = [c["usage"] for c in calls if isinstance(c.get("usage"), dict)]
    if not us:
        return None
    det = lambda u, k, s: ((u.get(k) or {}).get(s) or 0)
    inp = sum(u.get("input_tokens", 0) for u in us)
    cached = sum(det(u, "input_tokens_details", "cached_tokens") for u in us)
    write = sum(det(u, "input_tokens_details", "cache_write_tokens") for u in us)
    return {"requests": len(calls), "input": inp, "cached": cached, "cache_write": write,
            "uncached": inp - cached - write, "output": sum(u.get("output_tokens", 0) for u in us)}


def cost(t: dict, r: dict) -> float:
    return (t["uncached"] * r["input"] + t["cached"] * r["cached"] + t["cache_write"] * r["cache_write"]
            + t["output"] * r["output"]) / 1_000_000


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=float, default=0.10)
    ap.add_argument("--cached", type=float, default=0.01)
    ap.add_argument("--cache-write", type=float, default=0.125)
    ap.add_argument("--output", type=float, default=0.50)
    ap.add_argument("--runs-per-user-month", type=float, default=4.0,
                    help="Assumption: 2 Find-my-fit conversations x 2 assistant turns per active user per month")
    a = ap.parse_args(argv)
    rates = {"input": a.input, "cached": a.cached, "cache_write": a.cache_write, "output": a.output}

    groups: dict[str, list[dict]] = {}
    for p in sorted((OUT / "runs").glob("*.json")):
        t = json.loads(p.read_text())
        tok = run_tokens(t)
        if tok and t.get("success"):
            groups.setdefault(f"cost_eval:{t['tool_profile']}", []).append({"run_id": t["run_id"], **tok, "usd": cost(tok, rates)})
    for p in sorted((ROOT / "output" / "agent_runs").glob("*.json")):
        t = json.loads(p.read_text())
        tok = run_tokens(t)
        if tok and t.get("success"):
            groups.setdefault("earlier_real_runs_sessions3to6", []).append({"run_id": t["run_id"], **tok, "usd": cost(tok, rates)})

    summary = {}
    for g, rows in groups.items():
        summary[g] = {"n": len(rows), **{f"mean_{k}": round(statistics.mean(r[k] for r in rows), 1)
                                          for k in ("requests", "input", "cached", "cache_write", "uncached", "output")},
                      "mean_usd_per_run": statistics.mean(r["usd"] for r in rows),
                      "min_usd": min(r["usd"] for r in rows), "max_usd": max(r["usd"] for r in rows)}
    typical = summary.get("cost_eval:compact") or next(iter(summary.values()))
    per_run = typical["mean_usd_per_run"]
    per_user = per_run * a.runs_per_user_month
    proj = {"per_run_usd": per_run, "per_user_month_usd": per_user,
            "users_100_month_usd": per_user * 100, "users_10000_month_usd": per_user * 10_000,
            "sensitivity_per_user_month_usd": {f"{n}_runs": per_run * n for n in (1, 4, 10, 20)}}
    base, comp = summary.get("cost_eval:baseline"), summary.get("cost_eval:compact")
    effect = None
    if base and comp:
        effect = {"baseline_usd_per_run": base["mean_usd_per_run"], "compact_usd_per_run": comp["mean_usd_per_run"],
                  "saving_pct": 100 * (1 - comp["mean_usd_per_run"] / base["mean_usd_per_run"]),
                  "users_10000_month_baseline_usd": base["mean_usd_per_run"] * a.runs_per_user_month * 10_000,
                  "users_10000_month_compact_usd": comp["mean_usd_per_run"] * a.runs_per_user_month * 10_000}
    res = {"rates_usd_per_1M": rates, "rate_source": RATE_SOURCE,
           "assumptions": {"typical_run": "mean of the 6 fresh compact-profile runs (3 synthetic cases x 2 reps)",
                           "runs_per_user_month": a.runs_per_user_month,
                           "excluded": ["hosting/server costs", "Portkey gateway fees", "any course billing arrangement",
                                        "development and testing runs", "provider-filtered requests (0 tokens reported)",
                                        "possible Azure OpenAI price differences (the provider behind Portkey)",
                                        "taxes", "long-context, batch or priority tiers"]},
           "groups": summary, "projection": proj, "optimization_effect": effect}
    (OUT / "tokenomics.json").write_text(json.dumps(res, indent=2) + "\n")
    lines = [f"# Tokenomics (computed {Path(__file__).name}; rates in USD per 1M tokens)", "",
             f"Rates: input ${rates['input']}, cached ${rates['cached']}, cache write ${rates['cache_write']}, "
             f"output ${rates['output']}. Source: {RATE_SOURCE}", "",
             "| Group | n | Mean requests | Mean input | Mean cached | Mean uncached | Mean output | Mean $/run |",
             "|---|---|---|---|---|---|---|---|"]
    for g, s in summary.items():
        lines.append(f"| {g} | {s['n']} | {s['mean_requests']} | {s['mean_input']:,.0f} | {s['mean_cached']:,.0f} | "
                     f"{s['mean_uncached']:,.0f} | {s['mean_output']:,.0f} | ${s['mean_usd_per_run']:.5f} |")
    lines += ["", f"Typical run (compact): ${per_run:.5f}. Per user per month at {a.runs_per_user_month:g} runs: "
              f"${per_user:.4f}. 100 users: ${proj['users_100_month_usd']:.2f}/month. 10,000 users: "
              f"${proj['users_10000_month_usd']:.2f}/month (model cost only)."]
    if effect:
        lines.append(f"Optimization: ${effect['baseline_usd_per_run']:.5f} -> ${effect['compact_usd_per_run']:.5f} per run "
                     f"({effect['saving_pct']:.0f}% lower).")
    (OUT / "tokenomics.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return res


if __name__ == "__main__":
    main()
