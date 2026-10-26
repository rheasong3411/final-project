#!/usr/bin/env python3
"""Check that quoted evidence appears in the saved page snapshots.

Run from the animal-volunteer/ folder:

    python scripts/check_evidence_quotes.py
    python scripts/check_evidence_quotes.py --snapshots PATH

Checked text: every field_evidence passage, plus the published wording stored in
recurring_schedule / orientation_info / dated_notices (original_text) and
time_commitment (published_text). Passages are split on "..." and bracketed
editorial notes are removed. Each segment is then searched for in the snapshot of
the cited source, after normalizing whitespace, curly quotes and dashes.
Entries starting with "Derived:", "Interest area listed" or "Apply using" are our
own inferences or labels. They are counted separately and need a manual review.

The snapshots live in local_data/source_snapshots/<date>/, which is gitignored
because the files are full copies of third-party pages. On a fresh clone they
are missing: the script then exits with code 2 and says so. It does not
re-fetch pages, because a new fetch would not be the snapshot the evidence was
taken from.

Exit codes: 0 all quoted segments found, 1 some not found, 2 snapshots unavailable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOTS = ROOT / "local_data" / "source_snapshots" / "2026-10-25"
LABEL_PREFIXES = ("Derived:", "Interest area listed", "Apply using")


def norm(text: str) -> str:
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"),
                 ("​", ""), ("\xa0", " ")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip().lower()


def segments(passage: str):
    passage = re.sub(r"\[[^\]]*\]", "...", passage)
    return [s.strip(" .,;:") for s in passage.split("...") if len(s.strip(" .,;:")) > 6]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check evidence quotes against saved page snapshots.")
    ap.add_argument("--snapshots", type=Path, default=DEFAULT_SNAPSHOTS)
    ap.add_argument("--data-dir", type=Path, default=ROOT / "data")
    ap.add_argument("--per-record", action="store_true", help="also print a Markdown table of checked fields per record")
    args = ap.parse_args(argv)

    manifest_path = args.snapshots / "MANIFEST.json"
    if not manifest_path.exists():
        print(f"Snapshots not available at {args.snapshots}.")
        print("They are kept locally and are not in the repository. Without them the quote check cannot be reproduced;")
        print("output/data_audit.md records the results from the machine that has them.")
        return 2
    manifest = json.loads(manifest_path.read_text())
    pages = {}
    for sid, entry in manifest["files"].items():
        txt = entry.get("txt", {}).get("file")
        if txt and (args.snapshots / txt).exists():
            pages[sid] = norm((args.snapshots / txt).read_text(encoding="utf-8", errors="replace"))

    checked = labels = 0
    missing, no_snapshot = [], []
    per_record: dict[str, dict[str, set]] = {}

    def check(rid, field, sid, passage):
        nonlocal checked, labels
        rec = per_record.setdefault(rid, {}).setdefault(field, set())
        if passage.startswith(LABEL_PREFIXES):
            labels += 1
            rec.add("label_or_derived")
            return
        if sid not in pages:
            no_snapshot.append((rid, field, sid))
            rec.add("no_snapshot")
            return
        bad = [s for s in segments(passage) if norm(s) not in pages[sid]]
        if bad:
            missing.append((rid, field, sid, bad))
            rec.add("NOT_FOUND")
        else:
            checked += 1
            rec.add("verbatim")

    for name, id_field in (("organizations", "organization_id"), ("opportunities", "opportunity_id")):
        for r in json.loads((args.data_dir / f"{name}.json").read_text()):
            rid = r[id_field]
            for e in r.get("field_evidence", []):
                check(rid, e["field"], e["source_id"], e["evidence"])
            for f in ("recurring_schedule", "orientation_info", "dated_notices"):
                for x in r.get(f) or []:
                    check(rid, f, x["source_id"], x["original_text"])
            for x in r.get("time_commitment") or []:
                check(rid, "time_commitment", x["source_id"], x["published_text"])

    total = checked + labels + len(missing) + len(no_snapshot)
    print(f"Snapshots: {args.snapshots}")
    print(f"Passages examined: {total}")
    print(f"  quoted and found verbatim in the cited snapshot: {checked}")
    print(f"  derived statements / labels (manual review, not string-checkable): {labels}")
    print(f"  cited source has no text snapshot: {len(no_snapshot)}")
    print(f"  NOT FOUND: {len(missing)}")
    for m in missing:
        print("NOT FOUND", *m)
    for m in no_snapshot:
        print("NO SNAPSHOT", *m)
    if args.per_record:
        print("\n| Record | Fields with quotes found verbatim | Fields with derived statements or labels (manual review) |")
        print("|---|---|---|")
        for rid, fields in per_record.items():
            v = sorted(f for f, s in fields.items() if "verbatim" in s)
            d = sorted(f for f, s in fields.items() if "label_or_derived" in s)
            print(f"| `{rid}` | {', '.join(v) or '—'} | {', '.join(d) or '—'} |")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
