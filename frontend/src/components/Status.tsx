// Status badges: always icon + text + colour (never colour alone).
import type { ApplicabilityStatus, ApplicationStatus, AssessmentStatus, OverallStatus } from "../api/types";
import { APPLICABILITY_LABEL, FIT_LABEL, OVERALL_LABEL } from "../lib/labels";
import { useId, useState } from "react";
import { IconAlert, IconCheck, IconInfo, IconLock, IconQuestion, IconX } from "./Icons";

export function FitBadge({ status }: { status: AssessmentStatus }) {
  const cls = status === "met" ? "badge-met" : status === "not_met" ? "badge-no" : "badge-q";
  const Icon = status === "met" ? IconCheck : status === "not_met" ? IconX : IconQuestion;
  return <span className={`badge ${cls}`}><Icon size={16} />{FIT_LABEL[status]}</span>;
}

export function OverallBadge({ status }: { status: OverallStatus }) {
  const cls = status === "meets_published_requirements_checked" ? "badge-met" : status === "not_met" ? "badge-no" : "badge-q";
  const Icon = status === "meets_published_requirements_checked" ? IconCheck : status === "not_met" ? IconX : IconQuestion;
  return <span className={`badge ${cls}`}><span className="visually-hidden">Fit: </span><Icon size={16} />{OVERALL_LABEL[status]}</span>;
}

export const AVAILABILITY_EXPLANATION = "The source does not clearly state whether applications are being accepted. Check the organization’s volunteer page or contact them.";

/** Application status is shown separately from fit and never implies an opening. "Availability not confirmed" is
 *  informational text (not a button), with a keyboard-accessible explanation. */
export function AppStatusBadge({ status, label }: { status: ApplicationStatus; label?: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const text = label ?? ({
    explicitly_accepting_applications: "Accepting applications",
    explicitly_closed: "Applications closed",
    needs_confirmation: "Availability not confirmed",
  } as const)[status];
  if (status === "needs_confirmation") {
    return (
      <span className="status-info">
        <IconInfo size={15} /><span><span className="visually-hidden">Application status: </span>{text}</span>
        <button type="button" className="status-why" aria-expanded={open} aria-controls={id} onClick={() => setOpen(!open)}>
          <span aria-hidden>?</span><span className="visually-hidden">What “{text}” means</span>
        </button>
        {open && <span id={id} className="status-explain" role="note">{AVAILABILITY_EXPLANATION}</span>}
      </span>
    );
  }
  const cls = status === "explicitly_accepting_applications" ? "badge-open" : "badge-closed";
  const Icon = status === "explicitly_accepting_applications" ? IconInfo : IconLock;
  return (
    <span className={`badge ${cls}`}>
      <Icon size={16} /><span><span className="visually-hidden">Application status: </span>{text}</span>
    </span>
  );
}

export function UncertaintyBadge({ status }: { status: ApplicabilityStatus | "not_published" }) {
  if (status === "published_applicable") return null;
  if (status === "not_published") return <span className="badge badge-closed"><IconInfo size={15} />Not published</span>;
  return <span className="badge badge-q"><IconAlert size={15} />{APPLICABILITY_LABEL[status]}</span>;
}
