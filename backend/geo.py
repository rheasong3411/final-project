"""ZIP areas, location categories and approximate straight-line distances.

Everything here is local and deterministic (ordinary Python, no API calls):
- ZIP areas: Census 2026 Gazetteer ZCTA internal points for Connecticut (data/geo/ct_zcta.csv).
  ZCTAs approximate USPS ZIP Code areas; they are not postal boundaries.
- Town reference points: Census 2026 Gazetteer county-subdivision (town) internal points (data/geo/ct_towns.csv).
- Destinations: data/volunteer_locations.json (official-page-verified sites, Census Geocoder coordinates).

Every record gets exactly one location category (`kind`), and any distance says what it measures (`type`).
Destination order for a distance: (1) the verified volunteering site; (2) the organization's verified physical
location when the activity site is unknown (several sites, none assigned: the nearest one, named); (3) none.
  verified_site          an official page places the role at a site with a published street address
                         -> "North Haven · About 6 miles away"
  organization_location  the activity location is unknown, but the organization has verified physical site(s)
                         -> "Organization: New Haven · About 1 mile away" + "Activity location may differ"
                         -> "Nearest organization site: CHS Wilton · About 27 miles away" (several sites)
  town_only              an official source publishes the role's own town, but no address and no organization site
                         -> "<town> town center · About X miles away" + "Activity location may differ"
  home_based             the role happens in the volunteer's own home -> "Help from your home" (+ a related site,
                         such as orientation or supply pickup, only when a source says so; otherwise an organization
                         distance is reference only and never ranked)
  unknown                no reliable basis -> "Location: ask organization" (no distance)
Mailing addresses and P.O. boxes are never destinations.
An organization or town estimate never promotes a record to verified_site, and a role's town is never inferred
from the organization's headquarters. Distances are straight-line (haversine) from the ZIP area's internal point;
they are sorted on the unrounded value and rounded only for display. ZIP codes are never logged.
"""
from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import quote_plus

from .config import DATA_DIR

EARTH_RADIUS_MILES = 3958.8  # mean Earth radius (IUGG), in statute miles
ZIP_RE = re.compile(r"\d{5}")
COVERAGE = ("Distance estimates cover Connecticut ZIP areas only. The listings themselves stay limited to Greater "
            "New Haven, plus other Connecticut locations if you turn that on.")
SHARED_EXPLANATION = ("Distances are straight-line estimates from your ZIP area. For some activities, the distance is to "
                      "the organization; the activity location may differ.")
MAY_DIFFER = "Activity location may differ"
KINDS = ("verified_site", "organization_location", "town_only", "home_based", "unknown")
HEADLINES = {
    "verified_site": "Volunteering site verified",
    "organization_location": "Activity location may differ",
    "town_only": "Actual volunteering location may differ",
    "home_based": "Help from your home",
    "unknown": "Location: ask organization",
}


@dataclass(frozen=True)
class ZipCheck:
    status: str            # supported | invalid_format | not_in_dataset | outside_coverage | not_provided
    message: str
    lat: float | None = None
    lon: float | None = None

    def public(self) -> dict:
        """What the API/agent may see: the status and explanation, never the coordinates."""
        return {"status": self.status, "message": self.message}


@dataclass(frozen=True)
class Site:
    site_id: str
    organization_id: str
    label: str
    address: str
    town: str
    lat: float | None
    lon: float | None

    def public(self) -> dict:
        return {"site_id": self.site_id, "label": self.label, "address": self.address, "town": self.town,
                "maps_url": maps_url(self.address) if self.lat is not None else None,
                "directions_url": directions_url(self.address) if self.lat is not None else None}


class Geo:
    def __init__(self, zcta: dict, towns: dict, meta: dict, sites: dict[str, Site], roles: dict[str, dict],
                 org_locs: dict[str, dict], role_towns: dict[str, str | None], role_orgs: dict[str, str]):
        self.zcta, self.towns, self.meta, self.sites, self.roles = zcta, towns, meta, sites, roles
        self.org_locs, self.role_towns, self.role_orgs = org_locs, role_towns, role_orgs

    # ---------------------------------------------------------------- ZIP areas
    def check_zip(self, zip_code: str | None) -> ZipCheck:
        if zip_code is None or str(zip_code).strip() == "":
            return ZipCheck("not_provided", "No ZIP code given. Distances are optional.")
        z = str(zip_code).strip()
        if not ZIP_RE.fullmatch(z):
            return ZipCheck("invalid_format", "A ZIP code is exactly five digits, for example 06511.")
        if not z.startswith("06"):
            return ZipCheck("outside_coverage", f"{z} is not a Connecticut ZIP code. {COVERAGE}")
        if z not in self.zcta:
            return ZipCheck("not_in_dataset", f"{z} isn't in the Census ZIP-area list this app includes. P.O. Box-only "
                                              "and single-organization ZIP codes usually have no area. Try the ZIP "
                                              "code for your street address, or skip it.")
        lat, lon = self.zcta[z]
        return ZipCheck("supported", "Using the Census area for your ZIP code to estimate distances.", lat, lon)

    # ---------------------------------------------------------------- location categories
    def _town_ref(self, town: str | None) -> tuple[str, float, float] | None:
        """Census internal point for a published town ('Northford (village of North Branford)' -> North Branford)."""
        if not town:
            return None
        names = [town.split("(")[0].strip()]
        m = re.search(r"\(([^)]*)\)", town)
        if m:
            names.append(re.sub(r"^village of\s+", "", m.group(1).strip()))
        for n in names:
            if n in self.towns:
                return (n, *self.towns[n])
        return None

    def location_of(self, opportunity_id: str) -> dict:
        """Where a record takes place, as far as official pages establish it. No distance here."""
        r = self.roles.get(opportunity_id) or {"location_status": "not_published", "note": None}
        status = r["location_status"]
        org_id = self.role_orgs.get(opportunity_id)
        org_loc = self.org_locs.get(org_id, {})
        org_site = self.sites.get(org_loc.get("site_id") or "")
        role_town = self.role_towns.get(opportunity_id)
        out = {"kind": "unknown", "location_status": status, "headline": "", "note": r.get("note"),
               "role_town": role_town, "site": None, "organization_site": None, "related_site": None,
               "other_sites": [], "town_reference": None, "travel_note": r.get("travel_note"),
               "evidence": list(r.get("evidence", [])) + list(r.get("travel_evidence", [])),
               "maps_url": None, "coordinates_verified": False}
        if status == "verified_site":
            site = self.sites[r["site_id"]]
            out.update(kind="verified_site", site=site.public(), maps_url=maps_url(site.address), coordinates_verified=True)
        elif status == "volunteer_home":
            out["kind"] = "home_based"
            rel = self.sites.get(r.get("related_site_id") or "")
            if rel:
                out["related_site"] = {**rel.public(), "purpose": r.get("related_site_purpose") or "Related site"}
        elif org_site is not None and org_site.lat is not None:
            out.update(kind="organization_location", organization_site=org_site.public())
        elif org_loc.get("other_site_ids"):   # several verified sites, none assigned to this role
            out["kind"] = "organization_location"
        elif role_town and self._town_ref(role_town):
            out.update(kind="town_only", town_reference={"town": self._town_ref(role_town)[0],
                                                          "source": "Census 2026 Gazetteer town internal point"})
        if out["kind"] in ("organization_location", "unknown", "home_based") and org_loc.get("other_site_ids"):
            out["other_sites"] = [self.sites[s].public() for s in org_loc["other_site_ids"] if s in self.sites]
        if out["kind"] == "unknown" and not out["note"]:
            out["note"] = org_loc.get("basis")
        out["headline"] = HEADLINES[out["kind"]]
        out["place_label"], out["place_note"] = self._place(out)
        return out

    @staticmethod
    def _place(loc: dict) -> tuple[str, str | None]:
        """Short card text without a ZIP (with a ZIP, the distance label replaces it): place, small note."""
        k = loc["kind"]
        if k == "verified_site":
            return loc["site"]["town"], None
        if k == "organization_location":
            if loc["organization_site"]:
                return f"Organization: {_short_town(loc['organization_site']['town'])}", MAY_DIFFER
            towns = sorted({_short_town(s["town"]) for s in loc["other_sites"]})
            return f"Organization sites: {', '.join(towns)}", MAY_DIFFER
        if k == "town_only":
            return loc["role_town"], MAY_DIFFER
        return HEADLINES[k], None

    # ---------------------------------------------------------------- distances
    def distance(self, opportunity_id: str, zc: ZipCheck) -> dict:
        """One estimate per record. Destination order: (1) the verified volunteering site; (2) the organization's
        verified physical location (for several sites with none assigned: the nearest one, named); (3) none.
        Home-based roles: "Help from your home" stays primary; a sourced travel site (orientation, supply pickup)
        is sortable, an organization distance is reference only (sort_miles null, never "0 miles").
        Sort on `sort_miles` (unrounded; null sorts last); show `place_label` · `display`."""
        loc = self.location_of(opportunity_id)
        base = {"type": None, "miles": None, "sort_miles": None, "display": None, "place_label": None, "label": None,
                "secondary": None, "destination_label": None}
        if zc.status != "supported":
            return {**base, "status": "no_zip_area", "explanation": zc.message}
        kind, role = loc["kind"], self.roles.get(opportunity_id, {})
        org_loc = self.org_locs.get(self.role_orgs.get(opportunity_id), {})
        org_site = self.sites.get(org_loc.get("site_id") or "")
        if kind == "verified_site":
            s = self.sites[role["site_id"]]
            return self._est(zc, s, "volunteering_site", s.town, None)
        if kind == "organization_location":
            if org_site is not None and org_site.lat is not None:
                return self._est(zc, org_site, "organization_location", f"Organization: {_short_town(org_site.town)}", MAY_DIFFER)
            s = self._nearest(zc, org_loc.get("other_site_ids") or [])
            if s is not None:
                return self._est(zc, s, "organization_nearest_site", f"Nearest organization site: {s.label}", MAY_DIFFER)
        if kind == "town_only":
            name, lat, lon = self._town_ref(loc["role_town"])
            town = Site("town_reference", "", f"{name} town center", "", name, lat, lon)
            return self._est(zc, town, "town_reference", f"{name} town center", MAY_DIFFER)
        if kind == "home_based":
            rel = self.sites.get(role.get("related_site_id") or "")
            if rel is not None and rel.lat is not None:   # a source establishes travel to this site
                purpose = role.get("related_site_purpose") or "Related site"
                return self._est(zc, rel, "related_site", f"{purpose.split(',')[0]}: {rel.label}", "Help from your home")
            ref = org_site if org_site is not None and org_site.lat is not None else None
            if ref is not None:   # reference only: no travel is established, so it is not ranked
                est = self._est(zc, ref, "organization_reference", f"Organization: {_short_town(ref.town)}",
                                "Help from your home; no travel is stated")
                return {**est, "sort_miles": None}
            return {**base, "status": "unavailable", "display": "Help from your home",
                    "explanation": loc["travel_note"] or "The activity happens in your own home."}
        return {**base, "status": "unavailable", "display": None,
                "explanation": loc["note"] or "No physical location is published."}

    def _nearest(self, zc: ZipCheck, site_ids: list[str]):
        cands = [self.sites[i] for i in site_ids if i in self.sites and self.sites[i].lat is not None]
        return min(cands, key=lambda s: haversine_miles(zc.lat, zc.lon, s.lat, s.lon)) if cands else None

    def _est(self, zc: ZipCheck, site: "Site", kind: str, place: str, secondary: str | None) -> dict:
        miles = haversine_miles(zc.lat, zc.lon, site.lat, site.lon)
        rounded, text = round_miles(miles)
        display = f"{text} away"
        return {"status": "estimated", "type": kind, "miles": rounded, "sort_miles": round(miles, 3),
                "display": display, "place_label": place, "label": f"{place} · {display}", "secondary": secondary,
                "destination_label": site.label, "explanation": SHARED_EXPLANATION}


def _short_town(town: str) -> str:
    """Card label only: 'Northford (village of North Branford)' -> 'Northford'. Details keep the full text."""
    return town.split(" (")[0]


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def round_miles(miles: float) -> tuple[float, str]:
    """'Less than 1 mile'; nearest half mile below 10; nearest mile from 10. Never more precise than the inputs.

    Returns (rounded value, text such as 'About 6.5 miles'). Sorting uses the unrounded distance instead.
    """
    if miles < 1:
        return 0.5, "Less than 1 mile"
    r = round(miles * 2) / 2 if miles < 10 else float(round(miles))
    return r, f"About {r:g} mile" + ("" if r == 1 else "s")


def maps_url(address: str) -> str:
    """Google Maps search for the destination only (documented Maps URLs; no key, no starting point sent)."""
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(address)


def directions_url(address: str) -> str:
    """Google Maps directions with ONLY the destination filled in: the person enters their own starting point and
    chooses how to travel (walking, transit, cycling or driving). No travel time or transit route is claimed here."""
    return "https://www.google.com/maps/dir/?api=1&destination=" + quote_plus(address)


def town_matches(wanted: str, town_label: str) -> bool:
    """'New Haven' matches 'New Haven'; 'North Branford' matches 'Northford (village of North Branford)'.

    Exact names only, so 'Branford' never matches 'North Branford' and 'Haven' matches nothing.
    """
    w = wanted.strip().lower()
    t = town_label.strip().lower()
    names = {t, t.split("(")[0].strip()}
    m = re.search(r"\(([^)]*)\)", t)
    if m:
        names.add(re.sub(r"^village of\s+", "", m.group(1).strip()))
    return w in names


def load_geo(data_dir=DATA_DIR) -> Geo:
    def points(path, key):
        with path.open(encoding="utf-8") as f:
            return {row[key]: (float(row["intpt_lat"]), float(row["intpt_lon"])) for row in csv.DictReader(f)}
    zcta = points(data_dir / "geo" / "ct_zcta.csv", "zcta")
    towns = points(data_dir / "geo" / "ct_towns.csv", "town")
    meta = json.loads((data_dir / "geo" / "ct_zcta_metadata.json").read_text(encoding="utf-8"))
    loc = json.loads((data_dir / "volunteer_locations.json").read_text(encoding="utf-8"))
    sites = {}
    for s in loc["sites"]:
        g = s.get("geocode") or {}
        sites[s["site_id"]] = Site(s["site_id"], s["organization_id"], s["label"], s["address"], s["town"],
                                   g.get("latitude"), g.get("longitude"))
    roles = {r["opportunity_id"]: r for r in loc["opportunity_locations"]}
    org_locs = {o["organization_id"]: o for o in loc.get("organization_locations", [])}
    opps = json.loads((data_dir / "opportunities.json").read_text(encoding="utf-8"))
    role_towns = {o["opportunity_id"]: o["location_town"] for o in opps}   # the role's OWN town only
    role_orgs = {o["opportunity_id"]: o["organization_id"] for o in opps}
    for r in roles.values():  # a verified role must point at a geocoded site; anything else is a data error
        if r["location_status"] == "verified_site":
            s = sites.get(r.get("site_id") or "")
            if s is None or s.lat is None:
                raise ValueError(f"{r['opportunity_id']}: verified_site without a geocoded site")
    return Geo(zcta, towns, meta, sites, roles, org_locs, role_towns, role_orgs)


@lru_cache(maxsize=1)
def get_geo() -> Geo:
    return load_geo()
