"""Load the dataset once (paths relative to the repo) and provide lookups, filters and search.

Nothing here scrapes websites or reads the private snapshots in local_data/.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .config import DATA_DIR
from .geo import town_matches
from .schemas import Opportunity, Organization, Source

RECORD_TYPE_LABELS = {
    "described_volunteer_role": "Volunteer role described by the organization",
    "interest_area_only": "Ask about this activity: mentioned on an application form, without a published role description",
    "independent_support_activity": "Help on your own: something you organize yourself, not a staffed shelter shift",
}
APPLICATION_STATUS_LABELS = {
    "explicitly_accepting_applications": "Accepting applications",
    "explicitly_closed": "Applications closed",
    "needs_confirmation": "Availability not confirmed",
}


@dataclass
class Dataset:
    organizations: dict[str, Organization]
    opportunities: dict[str, Opportunity]
    sources: dict[str, Source]
    order: list[str] = field(default_factory=list)

    # ---------------------------------------------------------------- lookups
    def org(self, opp: Opportunity) -> Organization:
        return self.organizations[opp.organization_id]

    def scope_of(self, opp: Opportunity) -> str:
        return self.org(opp).geographic_scope

    def towns_of(self, opp: Opportunity) -> list[str]:
        """The role's own town if published, else the organization's single published town.

        Multi-site organizations (no single physical address) are never assigned all of their
        sites' towns; a role there has a town only if its own location_town is published.
        """
        if opp.location_town:
            return [opp.location_town]
        org = self.org(opp)
        return [org.town] if org.town else []

    def in_town(self, opp: Opportunity, town: str) -> bool:
        """True if the record's shown town is `town` (exact name). Used by Explore's town filter."""
        return any(town_matches(town, t) for t in self.towns_of(opp))

    def confirmed_in_town(self, opp: Opportunity, town: str) -> bool:
        """Stricter check for a person's explicit limit ("I need to stay in New Haven"): the role's OWN published
        location must be in `town`. An organization's town alone does not count, because many roles happen
        elsewhere (events "throughout the Greater New Haven area", foster homes, unnamed sites)."""
        return bool(opp.location_town) and town_matches(town, opp.location_town)

    def filter_values(self) -> dict:
        opps = [self.opportunities[i] for i in self.order]
        # Town filter = the role's OWN published town (same rule as the assistant), offered only where a
        # role that isn't closed publishes it.
        towns = sorted({o.location_town for o in opps if o.location_town and o.application_status != "explicitly_closed"})
        gnh = sorted({o.location_town for o in opps if o.location_town and o.application_status != "explicitly_closed"
                      and self.scope_of(o) == "greater_new_haven"})
        return {
            "geographic_scopes": {"default": "greater_new_haven", "values": ["greater_new_haven", "wider_connecticut"]},
            "towns": towns,
            # Explore offers only the towns of the selected scope (wider Connecticut towns only when that is on).
            "towns_by_scope": {"greater_new_haven": gnh, "all": towns},
            "organizations": [{"organization_id": o.organization_id, "name": o.name, "geographic_scope": o.geographic_scope}
                              for o in self.organizations.values()],
            "activity_tags": sorted({t for o in opps for t in o.activity_tags}),
            "animal_tags": sorted({t for o in opps for t in o.animal_tags}),
            "record_types": [{"value": k, "label": v} for k, v in RECORD_TYPE_LABELS.items()],
            "application_statuses": [{"value": k, "label": v} for k, v in APPLICATION_STATUS_LABELS.items()],
            "commitment_types": ["recurring", "one_time", "variable", "unknown"],
            "notes": "Town filtering by published town. Records whose applications are explicitly closed are left out "
                     "of lists by default (include_closed=true includes them). With an optional Connecticut ZIP, "
                     "POST /api/location/estimates gives straight-line estimates labelled by what they measure: a "
                     "verified volunteering site, the organization's location, a town center, or a related site for "
                     "home-based roles. No travel times, transit or remote options are available.",
        }

    # ---------------------------------------------------------------- search
    def search(self, *, include_wider_connecticut: bool = False, scope: str | None = None, town: str | None = None,
               town_confirmed: bool = True, organization_id: str | None = None, activities: list[str] | None = None,
               animals: list[str] | None = None, record_types: list[str] | None = None,
               application_status: str | None = None, commitment_type: str | None = None,
               query: str | None = None, limit: int | None = None, include_closed: bool = False) -> list[Opportunity]:
        """THE shared filter for Explore (/api/opportunities) and the assistant's search tool, so the same explicit
        filters give the same candidates. A town filter matches the role's own published town (town_confirmed);
        a commitment filter matches only records whose published commitment type is that value (unknown never
        matches). Defaults: Greater New Haven only, described volunteer roles only, and records whose
        applications are explicitly closed left out (they stay in the dataset for direct questions and detail
        pages; pass include_closed=True to include them)."""
        record_types = record_types or ["described_volunteer_role"]
        if scope is None:
            scopes = {"greater_new_haven", "wider_connecticut"} if include_wider_connecticut else {"greater_new_haven"}
        else:
            scopes = {scope}
        q = (query or "").strip().lower()
        out = []
        for oid in self.order:
            o = self.opportunities[oid]
            if self.scope_of(o) not in scopes or o.record_type not in record_types:
                continue
            if organization_id and o.organization_id != organization_id:
                continue
            if town and not (self.confirmed_in_town(o, town) if town_confirmed else self.in_town(o, town)):
                continue
            if activities and not set(activities) & set(o.activity_tags):
                continue
            if animals and not set(animals) & set(o.animal_tags):
                continue
            if not include_closed and o.application_status == "explicitly_closed":
                continue
            if application_status and o.application_status != application_status:
                continue
            if commitment_type and o.commitment_type != commitment_type:
                continue
            if q and q not in f"{o.title} {o.description} {self.org(o).name}".lower():
                continue
            out.append(o)
        return out[:limit] if limit else out

    def summary(self, o: Opportunity) -> dict:
        """Compact, stable view used by list routes and the search tool."""
        org = self.org(o)
        return {
            "opportunity_id": o.opportunity_id,
            "title": o.title,
            "organization_id": o.organization_id,
            "organization_name": org.name,
            "geographic_scope": org.geographic_scope,
            "towns": self.towns_of(o),
            "record_type": o.record_type,
            "record_type_label": RECORD_TYPE_LABELS[o.record_type],
            "activity_tags": o.activity_tags,
            "animal_tags": o.animal_tags,
            "commitment_type": o.commitment_type,
            "minimum_age": o.minimum_age,
            # Lets list views say "Not published" vs "confirm with the organization" without inventing values.
            "minimum_age_status": (o.requirement_applicability["minimum_age"].status
                                   if "minimum_age" in o.requirement_applicability else "not_published"),
            "uncertain_requirements": sorted(f for f, a in o.requirement_applicability.items()
                                             if a.status != "published_applicable"),
            "application_status": o.application_status,
            "application_status_label": APPLICATION_STATUS_LABELS[o.application_status],
            "short_description": o.description,
            "source_checked_on": max((self.sources[s].accessed_at[:10] for s in o.source_ids), default=None),
        }

    def is_application_page(self, url: str | None) -> bool:
        """True only if the URL is a recorded source that is an application form itself (not a volunteer page)."""
        return any(s.url == url and (s.access_result == "accessible_form_only" or "application" in s.page_title.lower())
                   for s in self.sources.values())

    def next_actions(self, o: Opportunity) -> list[dict]:
        """Links to the organization's own pages, labelled by what the destination actually is.

        "Apply on organization's website" only when the destination is an application page AND the listing is not
        explicitly closed (an application link never establishes an opening); otherwise "Visit volunteer page".
        "Contact organization" uses the recorded contact page when it is a different page. Nothing is submitted.
        """
        org = self.org(o)
        out, url = [], o.application_or_information_url
        if url:
            if self.is_application_page(url) and o.application_status != "explicitly_closed":
                out.append({"label": "Apply on organization's website", "url": url, "kind": "application"})
            else:
                out.append({"label": "Visit volunteer page", "url": url, "kind": "volunteer_page"})
        if org.contact_page_url and org.contact_page_url != url:
            out.append({"label": "Contact organization", "url": org.contact_page_url, "kind": "contact"})
        return out

    def details(self, o: Opportunity) -> dict:
        """Full record plus resolved organization and source links (for the detail page and the agent)."""
        org = self.org(o)
        return {
            **self.summary(o),
            "record": o.model_dump(),
            "organization": org.model_dump(include={"organization_id", "name", "official_website", "physical_address",
                                                   "town", "geographic_scope", "contact_page_url", "locations", "notes"}),
            "sources": [self.source_ref(s) for s in o.source_ids],
            "next_actions": self.next_actions(o),
        }

    def source_ref(self, source_id: str) -> dict:
        s = self.sources[source_id]
        return {"source_id": s.source_id, "organization_id": s.organization_id, "page_title": s.page_title,
                "url": s.url, "accessed_at": s.accessed_at}


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError(f"{path.name} must be a JSON array")
    return rows


def load_dataset(data_dir: Path = DATA_DIR) -> Dataset:
    orgs = [Organization.model_validate(r) for r in _read(data_dir / "organizations.json")]
    opps = [Opportunity.model_validate(r) for r in _read(data_dir / "opportunities.json")]
    srcs = [Source.model_validate(r) for r in _read(data_dir / "sources.json")]
    ds = Dataset({o.organization_id: o for o in orgs}, {o.opportunity_id: o for o in opps},
                 {s.source_id: s for s in srcs}, [o.opportunity_id for o in opps])
    for o in opps:  # references must resolve; the validator checks more, this guards the backend
        if o.organization_id not in ds.organizations:
            raise ValueError(f"{o.opportunity_id}: unknown organization {o.organization_id}")
        missing = [s for s in o.source_ids if s not in ds.sources]
        if missing:
            raise ValueError(f"{o.opportunity_id}: unknown sources {missing}")
    return ds


@lru_cache(maxsize=1)
def get_dataset() -> Dataset:
    return load_dataset()
