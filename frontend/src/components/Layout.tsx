import { useEffect, useState, type ReactNode } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { MAX_COMPARE, useAppState } from "../state/AppState";
import { IconArrow, IconMenu, IconPaw } from "./Icons";

export function Layout({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const { compareIds, clearCompare } = useAppState();
  const loc = useLocation();
  useEffect(() => { setOpen(false); window.scrollTo(0, 0); }, [loc.pathname]);
  // Reserve room below the page for the comparison bar (its height varies with screen width), so the last
  // card's links can always be scrolled above it.
  useEffect(() => {
    const bar = document.querySelector<HTMLElement>(".compare-tray");
    const set = () => document.documentElement.style.setProperty("--tray-space", `${(bar?.offsetHeight ?? 0) + 40}px`);
    set();
    if (!bar) return;
    const ro = new ResizeObserver(set); ro.observe(bar);
    return () => ro.disconnect();
  }, [compareIds.length, loc.pathname]);
  useEffect(() => {
    const titles: Record<string, string> = { "/": "Home", "/explore": "Explore opportunities", "/about": "About",
      "/find-my-fit": "Find my fit", "/compare": "Compare opportunities" };
    const t = titles[loc.pathname] ?? (loc.pathname.startsWith("/opportunities/") ? "Opportunity details" : "Animal Volunteer Finder");
    document.title = `${t} · Animal Volunteer Finder`;
  }, [loc.pathname]);

  return (
    <>
      <a className="skip-link" href="#main">Skip to main content</a>
      <header className="site-header">
        <div className="container header-inner">
          <Link to="/" className="brand" aria-label="Animal Volunteer Finder, home">
            <span style={{ display: "grid", placeItems: "center", width: 40, height: 40, borderRadius: 12, background: "var(--forest)", color: "var(--peach)" }}>
              <IconPaw size={24} />
            </span>
            <span>Animal Volunteer Finder<small>Greater New Haven, Connecticut</small></span>
          </Link>
          <button className="btn btn-ghost nav-toggle" aria-expanded={open} aria-controls="primary-nav" onClick={() => setOpen((o) => !o)}>
            <IconMenu /> <span>Menu</span>
          </button>
          <nav id="primary-nav" className={`nav${open ? " open" : ""}`} aria-label="Primary">
            <NavLink to="/" end className="nav-link">Home</NavLink>
            <NavLink to="/explore" className="nav-link">Explore</NavLink>
            <NavLink to="/about" className="nav-link">About</NavLink>
            {compareIds.length > 0 && <NavLink to="/compare" className="nav-link">Compare ({compareIds.length})</NavLink>}
            <Link to="/find-my-fit" className="btn btn-primary" style={{ marginLeft: 8 }}>Find my fit <IconArrow size={16} /></Link>
          </nav>
        </div>
      </header>
      <main id="main" tabIndex={-1}>{children}</main>
      <footer className="site-footer">
        <div className="container grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
          <div>
            <h2>Animal Volunteer Finder</h2>
            <p className="small">Helps you prepare to apply. It does not approve volunteers, confirm openings, or book shifts. Organizations make all decisions.</p>
          </div>
          <div>
            <h2>About the information</h2>
            <p className="small">Requirements come from organizations' public web pages, checked on the dates shown with each source. Always confirm with the organization.</p>
          </div>
          <div>
            <h2>Explore</h2>
            <p className="small"><Link to="/explore">Browse opportunities</Link><br /><Link to="/find-my-fit">Find my fit</Link><br /><Link to="/about">How this works</Link></p>
          </div>
        </div>
      </footer>
      {/* Not on Compare (already there) or Find my fit (its cards have no compare buttons; the bar would cover the chat
          on phones). The "Compare (N)" link in the menu stays available everywhere. */}
      {compareIds.length > 0 && loc.pathname !== "/compare" && loc.pathname !== "/find-my-fit" && (
        <div className="compare-tray" role="region" aria-label="Comparison selection">
          <span className="compare-tray-text" aria-live="polite">
            <strong>{compareIds.length} {compareIds.length === 1 ? "opportunity" : "opportunities"} selected</strong>
            <span className="compare-tray-hint"> (up to {MAX_COMPARE}). Compare age, hours, commitment and fees side by side.</span>
          </span>
          <Link to="/compare" className="btn btn-peach btn-small">View comparison</Link>
          <button type="button" className="btn btn-small compare-tray-clear" onClick={clearCompare}>Clear<span className="visually-hidden"> comparison selection</span></button>
        </div>
      )}
    </>
  );
}
