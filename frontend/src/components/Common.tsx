// Small shared building blocks: external links, notices, loading, empty states, safe text.
import { Fragment, type ReactNode } from "react";
import { hostOf } from "../lib/labels";
import { IconAlert, IconExternal, IconInfo } from "./Icons";
import { EmptyIllustration } from "./Illustrations";

/** External links always open in a new tab safely and say where they go. */
export function ExternalLink({ href, children, className, arrow = false, label }:
  { href: string; children: ReactNode; className?: string; arrow?: boolean; label?: string }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={className} aria-label={label}>
      {children}
      {arrow ? <span aria-hidden> ↗</span> : <IconExternal size={15} style={{ marginLeft: 4, verticalAlign: "-2px" }} />}
      <span className="visually-hidden"> (opens {hostOf(href)} in a new tab)</span>
    </a>
  );
}

export function Notice({ tone = "info", title, children }: { tone?: "info" | "warn" | "error"; title?: string; children: ReactNode }) {
  const Icon = tone === "info" ? IconInfo : IconAlert;
  return (
    <div className={`notice notice-${tone}`} role={tone === "error" ? "alert" : undefined}>
      <Icon size={20} />
      <div>{title && <p><strong>{title}</strong></p>}{children}</div>
    </div>
  );
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return <p className="loading" role="status"><span className="spinner" aria-hidden />{label}…</p>;
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="card card-quiet" style={{ textAlign: "center", padding: "40px 24px" }}>
      <EmptyIllustration className="" />
      <h3 style={{ marginTop: 12 }}>{title}</h3>
      {children}
    </div>
  );
}

function inline(text: string): ReactNode[] {
  // **bold** only; everything else is plain text (React escapes it).
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? <strong key={i}>{part.slice(2, -2)}</strong> : <Fragment key={i}>{part}</Fragment>,
  );
}

/** Renders model text safely: paragraphs, "-" bullet lists and **bold**. Never injects HTML. */
export function SafeText({ text }: { text: string }) {
  const blocks = text.replace(/\r/g, "").split(/\n{2,}/);
  return (
    <>
      {blocks.map((block, i) => {
        const lines = block.split("\n").filter((l) => l.trim() !== "");
        if (lines.length && lines.every((l) => /^\s*[-*•]\s+/.test(l))) {
          return <ul key={i}>{lines.map((l, j) => <li key={j}>{inline(l.replace(/^\s*[-*•]\s+/, ""))}</li>)}</ul>;
        }
        return <p key={i}>{lines.map((l, j) => <Fragment key={j}>{j > 0 && <br />}{inline(l)}</Fragment>)}</p>;
      })}
    </>
  );
}
