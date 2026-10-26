import { Link } from "react-router-dom";
import type { DistanceEstimate, OpportunitySummary } from "../api/types";
import { activityLabel, animalLabel, commitmentLabel, RECORD_TYPE_UI, scopeLabel } from "../lib/labels";
import { CompareToggle } from "./CompareToggle";
import { NextActions } from "./FactLines";
import { IconClock, IconPin } from "./Icons";
import { PlaceLine } from "./Location";
import { AppStatusBadge } from "./Status";

function ageText(o: OpportunitySummary): string {
  if (o.minimum_age_status === "conflicting") return "Age: sources conflict, confirm with organization";
  if (o.minimum_age_status === "needs_confirmation") return "Age: confirm with organization";
  if (o.minimum_age === null) return "Minimum age: Not published";
  return o.minimum_age === 0 ? "All ages (guardian rules may apply)" : `Age ${o.minimum_age}+`;
}

export function OpportunityCard({ o, showScope = false, distance }: { o: OpportunitySummary; showScope?: boolean; distance?: DistanceEstimate | null }) {
  return (
    <article className="card opp-card" aria-labelledby={`t-${o.opportunity_id}`}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          {RECORD_TYPE_UI[o.record_type] && (
            <p className="chip chip-peach" style={{ marginBottom: 8 }}>{RECORD_TYPE_UI[o.record_type].chip}</p>
          )}
          <h3 id={`t-${o.opportunity_id}`}><Link to={`/opportunities/${o.opportunity_id}`}>{o.title}</Link></h3>
          <p className="muted small" style={{ margin: "4px 0 0" }}>{o.organization_name}</p>
        </div>
      </div>
      <div className="meta">
        <span className="meta-place"><IconPin size={15} /><span><PlaceLine loc={o.location} d={distance} />{showScope && <span className="place-note">{scopeLabel(o.geographic_scope)}</span>}</span></span>
        <span><IconClock size={15} />{commitmentLabel(o.commitment_type)}</span>
        <span>{ageText(o)}</span>
      </div>
      <div className="chips" aria-label="Activities and animals">
        {o.activity_tags.slice(0, 3).map((t) => <span key={t} className="chip">{activityLabel(t)}</span>)}
        {o.animal_tags.filter((t) => t !== "not_applicable" && t !== "unspecified").map((t) => (
          <span key={t} className="chip chip-outline">{animalLabel(t)}</span>
        ))}
      </div>
      {o.record_type === "interest_area_only" && (
        <p className="small" style={{ margin: 0 }}>{RECORD_TYPE_UI.interest_area_only.explain}</p>
      )}
      {o.uncertain_requirements.length > 0 && (
        <p className="small muted" style={{ margin: 0 }}>Some requirements are uncertain or conflicting. See details.</p>
      )}
      <div className="card-footer">
        <AppStatusBadge status={o.application_status} />
        <NextActions actions={o.next_actions} compact />
        <CompareToggle id={o.opportunity_id} title={o.title} />
      </div>
    </article>
  );
}
