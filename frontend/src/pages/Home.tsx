import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { OpportunitySummary } from "../api/types";
import { Loading, Notice } from "../components/Common";
import { IconArrow, IconCheck, IconDoc, IconQuestion } from "../components/Icons";
import { HeroIllustration, Sprig } from "../components/Illustrations";
import { OpportunityCard } from "../components/OpportunityCard";
import { formatDate } from "../lib/labels";

interface Stats { roles: number; orgs: number; closed: number; accepting: number; checked: string | null }

export function Home() {
  const [featured, setFeatured] = useState<OpportunitySummary[] | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ctl = new AbortController();
    api.opportunities({}, ctl.signal).then((list) => {
      // Transparent selection: the first role from each organization, in dataset order. Not a ranking.
      // Closed roles are already left out by the backend.
      const seen = new Set<string>();
      const picks: OpportunitySummary[] = [];
      for (const o of list.results) {
        if (seen.has(o.organization_id)) continue;
        seen.add(o.organization_id);
        picks.push(o);
        if (picks.length === 3) break;
      }
      setFeatured(picks);
      const dates = list.results.map((o) => o.source_checked_on).filter(Boolean) as string[];
      setStats({
        roles: list.count, orgs: new Set(list.results.map((o) => o.organization_id)).size,
        closed: list.closed_hidden,
        accepting: list.results.filter((o) => o.application_status === "explicitly_accepting_applications").length,
        checked: dates.sort().at(-1) ?? null,
      });
    }).catch((e) => { if (e.name !== "AbortError") setError(e.message); });
    return () => ctl.abort();
  }, []);

  return (
    <>
      <section className="hero">
        <div className="container hero-inner">
          <div>
            <p className="eyebrow">Greater New Haven, Connecticut</p>
            <h1>Find animal-volunteering opportunities — and know what you need before you apply.</h1>
            <p className="lede">Browse roles at local shelters and rescues, see each requirement with its source, and get help working out which ones might fit your age, schedule and interests.</p>
            <div className="row" style={{ marginTop: 24 }}>
              <Link to="/explore" className="btn btn-primary">Explore opportunities <IconArrow size={16} /></Link>
              <Link to="/find-my-fit" className="btn btn-secondary">Find my fit</Link>
            </div>
          </div>
          <HeroIllustration className="hero-art" />
        </div>
      </section>

      <section className="section">
        <div className="container">
          <p className="eyebrow">How it works</p>
          <h2>Three steps to a well-prepared application</h2>
          <div className="steps" style={{ marginTop: 24 }}>
            <div className="step"><h3>Explore</h3><p>Filter roles by town, activity, animals and commitment. Every listing links back to the organization's own page.</p></div>
            <div className="step"><h3>Check requirements</h3><p>Compare age, guardian, time and training rules side by side. Uncertain or conflicting information is flagged, not hidden.</p></div>
            <div className="step"><h3>Prepare to apply</h3><p>Get a checklist of steps and questions to ask, then apply on the organization's own website.</p></div>
          </div>
        </div>
      </section>

      <section className="section-tight" style={{ background: "var(--sage)" }}>
        <div className="container">
          <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-end" }}>
            <div>
              <p className="eyebrow">A few places to start</p>
              <h2 style={{ marginBottom: 6 }}>Opportunities from local organizations</h2>
              <p className="muted" style={{ maxWidth: 680 }}>Shown here: the first listed role from each organization, in our dataset's order (roles with closed applications aren't listed). This is not a ranking or a recommendation.</p>
            </div>
            <Link to="/explore" className="btn btn-secondary">See all opportunities</Link>
          </div>
          {error && <Notice tone="error" title="Opportunities couldn't be loaded.">{error}</Notice>}
          {!featured && !error && <Loading label="Loading opportunities" />}
          {featured && <div className="grid grid-3" style={{ marginTop: 20 }}>{featured.map((o) => <OpportunityCard key={o.opportunity_id} o={o} />)}</div>}
        </div>
      </section>

      <section className="section">
        <div className="container split">
          <div>
            <p className="eyebrow">About the information</p>
            <h2>Sourced, dated and honest about uncertainty</h2>
            <p>Every requirement comes from an organization's public web page, with a quote you can expand and the date we checked the page. A checked date tells you when we looked — not that the organization confirmed anything that day.</p>
            <p>Most listings say <strong>"Availability not confirmed"</strong>: the page describes the role but doesn't clearly say whether applications are being accepted. Visit the organization's volunteer page or contact them. We never show a listing as a guaranteed opening, and we don't book shifts or approve volunteers.</p>
            {stats && (
              <p className="muted">
                Greater New Haven currently has {stats.roles} described volunteer roles from {stats.orgs} organizations in this guide that aren't closed, checked on {formatDate(stats.checked)}.
                {" "}{stats.closed} more say applications are closed and aren't listed{stats.accepting === 0 ? ". None currently say they're accepting applications, so ask each organization about availability." : "."}
              </p>
            )}
          </div>
          <div className="card card-peach stack">
            <div className="row"><IconCheck /><strong>Meets this published requirement</strong></div>
            <div className="row"><IconQuestion /><strong>Needs confirmation</strong></div>
            <div className="row"><IconDoc /><strong>Evidence and source date for each rule</strong></div>
            <p className="small" style={{ margin: 0 }}>Requirement checks are done by fixed rules, not by AI guesswork. The assistant explains the results and helps you compare options.</p>
          </div>
        </div>
      </section>
      <div className="container" aria-hidden style={{ display: "flex", justifyContent: "space-between", marginTop: -40, opacity: 0.8 }}>
        <Sprig className="" /><Sprig className="" flip />
      </div>
    </>
  );
}
