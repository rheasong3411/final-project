#!/usr/bin/env python3
"""Build and check the local geography data used for approximate distances.

Run from the animal-volunteer/ folder:

    python scripts/build_geo_data.py zcta PATH/2026_Gaz_zcta_national.zip   # writes data/geo/ct_zcta.csv + metadata
    python scripts/build_geo_data.py towns PATH/2026_Gaz_cousubs_national.zip # writes data/geo/ct_towns.csv + metadata
    python scripts/build_geo_data.py geocode                                # fills site coordinates (Census Geocoder)
    python scripts/build_geo_data.py verify                                 # checks quotes against local snapshots

Sources (no API key, no account, no paid service):
- ZIP areas: U.S. Census Bureau 2026 Gazetteer file for ZIP Code Tabulation Areas (ZCTAs),
  https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2026_Gazetteer/2026_Gaz_zcta_national.zip
  ZCTAs are Census approximations of USPS ZIP Code service areas, not postal ZIP boundaries.
  INTPTLAT/INTPTLONG are each ZCTA's "internal point". Only Connecticut rows (GEOID 06xxx) are kept.
- Site coordinates: U.S. Census Geocoder REST API (onelineaddress, benchmark Public_AR_Current).
  Coordinates are interpolated along TIGER address ranges, so they are approximate.
Both are U.S. Government works (public domain in the U.S., 17 U.S.C. 105).

`geocode` only touches sites whose address was verified on an official organization page
(data/volunteer_locations.json). It never geocodes mailing addresses or guesses an address.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEO_DIR = ROOT / "data" / "geo"
LOCATIONS = ROOT / "data" / "volunteer_locations.json"
SNAPSHOTS = ROOT / "local_data" / "source_snapshots" / "2026-10-25" / "location_verification"
GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2026_Gazetteer/2026_Gaz_zcta_national.zip"
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build_zcta(zip_path: str) -> None:
    raw = Path(zip_path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = next(n for n in z.namelist() if n.endswith(".txt"))
        text = z.read(name).decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text), delimiter="|"))
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in rows]
    ct = sorted((r for r in rows if r["GEOID"].startswith("06")), key=lambda r: r["GEOID"])
    GEO_DIR.mkdir(parents=True, exist_ok=True)
    with (GEO_DIR / "ct_zcta.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["zcta", "intpt_lat", "intpt_lon", "aland_sqmi"])
        for r in ct:
            w.writerow([r["GEOID"], r["INTPTLAT"], r["INTPTLONG"], r["ALAND_SQMI"]])
    meta = {
        "dataset": "U.S. Census Bureau, 2026 Gazetteer Files: ZIP Code Tabulation Areas (national file)",
        "download_url": GAZ_URL,
        "file_inside_zip": name,
        "zip_sha256": hashlib.sha256(raw).hexdigest(),
        "national_rows": len(rows),
        "rows_kept": len(ct),
        "rows_kept_rule": "GEOID starts with '06' (Connecticut ZCTAs)",
        "geography": "2020 Census ZIP Code Tabulation Areas (ZCTAs), as published in the 2026 Gazetteer",
        "postal_zip_or_zcta": "ZCTA. Census approximations of USPS ZIP Code service areas built from census blocks; "
                              "not official postal ZIP boundaries. PO Box-only and single-organization ZIP Codes "
                              "often have no ZCTA.",
        "coordinates": "INTPTLAT/INTPTLONG: the Census 'internal point' of each ZCTA (a point inside the area, "
                       "close to its center). Not a household location.",
        "dataset_date": "2026 Gazetteer; server Last-Modified Tue, 08 Sep 2026 21:00:12 GMT",
        "downloaded_at": "2026-10-25, about 19:24 EDT (file timestamp of the local download)",
        "license": "U.S. Government work; public domain in the U.S. (17 U.S.C. 105). No key or account needed.",
        "documentation": [
            "https://www.census.gov/programs-surveys/geography/technical-documentation/records-layout/gaz-record-layouts.html",
            "https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html",
        ],
    }
    (GEO_DIR / "ct_zcta_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"kept {len(ct)} Connecticut ZCTAs of {len(rows)}")


def build_towns(zip_path: str) -> None:
    """Connecticut towns (county subdivisions) from the Census 2026 Gazetteer: one reference point per town.

    The point is the Census 'internal point' of the town's area (a point inside the town, near its geographic
    middle). It is not the town's downtown, town hall or any volunteering location.
    """
    raw = Path(zip_path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = next(n for n in z.namelist() if n.endswith(".txt"))
        text = z.read(name).decode("utf-8")
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(io.StringIO(text), delimiter="|")]
    ct = sorted((r for r in rows if r["USPS"] == "CT" and r["NAME"].endswith(" town")), key=lambda r: r["NAME"])
    with (GEO_DIR / "ct_towns.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["town", "geoid", "intpt_lat", "intpt_lon"])
        for r in ct:
            w.writerow([r["NAME"][: -len(" town")], r["GEOID"], r["INTPTLAT"], r["INTPTLONG"]])
    meta = {
        "dataset": "U.S. Census Bureau, 2026 Gazetteer Files: County Subdivisions (national file)",
        "download_url": GAZ_URL.replace("zcta_national", "cousubs_national"),
        "zip_sha256": hashlib.sha256(raw).hexdigest(),
        "rows_kept": len(ct),
        "rows_kept_rule": "USPS = CT and NAME ends with ' town' (Connecticut's 169 towns)",
        "reference_point": "INTPTLAT/INTPTLONG: the Census internal point of the town's area. Used as the 'town center' "
                           "reference for towns published without an address. Not a downtown, a town hall or a "
                           "volunteering location.",
        "dataset_date": "2026 Gazetteer; server Last-Modified Tue, 08 Sep 2026 21:00:12 GMT",
        "downloaded_at": "2026-10-25 (Session 12)",
        "license": "U.S. Government work; public domain in the U.S. (17 U.S.C. 105). No key or account needed.",
    }
    (GEO_DIR / "ct_towns_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"kept {len(ct)} Connecticut towns")


def geocode() -> None:
    import httpx  # project dependency (requirements.txt)

    data = json.loads(LOCATIONS.read_text(encoding="utf-8"))
    for site in data["sites"]:
        r = httpx.get(GEOCODER_URL, params={"address": site["geocoder_query"], "benchmark": "Public_AR_Current",
                                            "format": "json"}, timeout=60).json()
        matches = r["result"]["addressMatches"]
        if len(matches) != 1:
            print(f"{site['site_id']}: {len(matches)} matches; coordinates left null")
            site["geocode"] = None
            continue
        m = matches[0]
        site["geocode"] = {
            "latitude": round(m["coordinates"]["y"], 6),
            "longitude": round(m["coordinates"]["x"], 6),
            "matched_address": m["matchedAddress"],
            "match_count": 1,
            "tiger_line_id": m["tigerLine"]["tigerLineId"],
            "street_side": m["tigerLine"]["side"],
            "benchmark": r["result"]["input"]["benchmark"]["benchmarkName"],
            "geocoded_at": _now(),
        }
        print(site["site_id"], site["geocode"]["matched_address"])
    LOCATIONS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.replace("’", "'").replace("​", "")).strip().lower()


def verify() -> int:
    """Every address and role quote must appear in the saved page text (local, gitignored snapshots)."""
    data = json.loads(LOCATIONS.read_text(encoding="utf-8"))
    if not SNAPSHOTS.is_dir():
        print("No local snapshots; skipping quote check (structure is covered by tests/test_geo.py).")
        return 0
    bad = 0
    quotes = [(s["site_id"], e) for s in data["sites"] for e in s["address_evidence"]]
    quotes += [(o["opportunity_id"], e) for o in data["opportunity_locations"]
               for e in o.get("evidence", []) + o.get("travel_evidence", [])]
    for rid, e in quotes:
        page = SNAPSHOTS / f"{e['source_id']}.txt"
        if not page.is_file():  # quotes from the original fetch live one folder up
            page = SNAPSHOTS.parent / f"{e['source_id']}.txt"
        ok = page.is_file() and _norm(e["quote"]) in _norm(page.read_text(encoding="utf-8"))
        bad += not ok
        print(("ok  " if ok else "MISSING ") + f"{rid} [{e['source_id']}] {e['quote'][:70]}")
    print(f"{len(quotes) - bad}/{len(quotes)} quotes found in snapshots")
    return 1 if bad else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "zcta" and len(sys.argv) == 3:
        build_zcta(sys.argv[2])
    elif cmd == "towns" and len(sys.argv) == 3:
        build_towns(sys.argv[2])
    elif cmd == "geocode":
        geocode()
    elif cmd == "verify":
        sys.exit(verify())
    else:
        print(__doc__)
        sys.exit(2)
