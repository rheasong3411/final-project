// Display-only evidence clean-up (the sourced data itself is never changed). Mirrors backend matching.dedupe_evidence.
const norm = (q: string) => q.replace(/[\u2018\u2019]/g, "'").replace(/[\u201c\u201d]/g, '"')
  .replace(/^[\s*•\-\u2013\u2014"']+|[\s"'.;,:]+$/g, "").replace(/\s+/g, " ").trim().toLowerCase();

/** The smallest useful set of passages: drops exact repeats and any excerpt contained in a longer passage from the
 *  SAME source. Passages from different sources (including conflicting ones) are kept, in their original order. */
export function dedupeQuotes<T extends { source_id: string; quote: string }>(items: T[]): T[] {
  const n = items.map((x) => norm(x.quote));
  return items.filter((x, i) => !items.some((y, j) => j !== i && y.source_id === x.source_id && n[j].includes(n[i])
    && (n[j].length > n[i].length || j < i)));
}
