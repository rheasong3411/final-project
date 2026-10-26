// Optional comparison control. Never blocks opening details or visiting the organization's website.
import { MAX_COMPARE, useAppState } from "../state/AppState";
import { IconCheck, IconPlus } from "./Icons";

export function CompareToggle({ id, title }: { id: string; title: string }) {
  const { compareIds, toggleCompare } = useAppState();
  const selected = compareIds.includes(id);
  const full = !selected && compareIds.length >= MAX_COMPARE;
  if (selected) {
    return (
      <span className="compare-added" role="status">
        <IconCheck size={16} /> Added to comparison
        <button type="button" className="link-button small" onClick={() => toggleCompare(id)}>
          Remove<span className="visually-hidden"> {title} from comparison</span></button>
      </span>
    );
  }
  return (
    <span className="compare-toggle">
      <button type="button" className="btn btn-ghost btn-small" onClick={() => toggleCompare(id)} disabled={full}
        aria-describedby={full ? `cmp-full-${id}` : undefined}>
        <IconPlus size={16} />Compare requirements<span className="visually-hidden"> for {title}</span>
      </button>
      {full && <span id={`cmp-full-${id}`} className="hint">Up to {MAX_COMPARE}; remove one to add this.</span>}
    </span>
  );
}
