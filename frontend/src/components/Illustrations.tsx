// Original decorative SVG illustrations (no shelter logos or photos). Hidden from assistive tech.

const F = "#214D3C";
const FD = "#173829";
const PEACH = "#F3D2BD";
const PEACH_D = "#E7B697";
const SAGE = "#E4EBDF";
const SAGE_D = "#B9CBB0";
const CREAM = "#FAF7F0";
const INK = "#24352D";

export function Sprig({ className, flip = false }: { className?: string; flip?: boolean }) {
  return (
    <svg className={`sprig ${className ?? ""}`} viewBox="0 0 80 120" aria-hidden focusable={false} style={flip ? { transform: "scaleX(-1)" } : undefined}>
      <path d="M40 118C40 80 44 46 58 8" stroke={F} strokeWidth="2.5" fill="none" strokeLinecap="round" />
      {[[46, 90, -35], [48, 70, 30], [52, 50, -30], [55, 32, 28], [57, 16, -25]].map(([x, y, r], i) => (
        <ellipse key={i} cx={x} cy={y} rx="11" ry="5" fill={i % 2 ? SAGE_D : "#8FAF8B"} transform={`rotate(${r} ${x} ${y})`} />
      ))}
    </svg>
  );
}

/** Hero composition: a sitting dog, a curled cat and a small rabbit among botanicals on a soft arch. */
export function HeroIllustration({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 520 440" role="presentation" aria-hidden focusable={false}>
      {/* backdrop arch + ground */}
      <path d="M60 400V210c0-110 89-190 200-190s200 80 200 190v190Z" fill={SAGE} />
      <path d="M95 400V222c0-92 74-160 165-160s165 68 165 160v178Z" fill={CREAM} opacity="0.55" />
      <circle cx="372" cy="104" r="34" fill={PEACH} opacity="0.85" />
      <ellipse cx="260" cy="402" rx="235" ry="20" fill={SAGE_D} opacity="0.55" />

      {/* left botanical */}
      <g transform="translate(36 236)">
        <path d="M30 168C28 118 36 70 64 14" stroke={F} strokeWidth="3" fill="none" strokeLinecap="round" />
        {[[34, 140, -40], [38, 116, 32], [44, 92, -36], [52, 66, 30], [60, 40, -30]].map(([x, y, r], i) => (
          <ellipse key={i} cx={x} cy={y} rx="16" ry="7" fill={i % 2 ? SAGE_D : "#8FAF8B"} transform={`rotate(${r} ${x} ${y})`} />
        ))}
      </g>
      {/* right botanical */}
      <g transform="translate(430 270)">
        <path d="M24 136C26 98 18 58 0 22" stroke={F} strokeWidth="3" fill="none" strokeLinecap="round" />
        {[[22, 112, 38], [18, 88, -30], [12, 64, 34], [5, 42, -28]].map(([x, y, r], i) => (
          <ellipse key={i} cx={x} cy={y} rx="14" ry="6" fill={i % 2 ? "#8FAF8B" : SAGE_D} transform={`rotate(${r} ${x} ${y})`} />
        ))}
        <circle cx="0" cy="20" r="7" fill={PEACH_D} />
      </g>

      {/* dog (sitting, three-quarter view) */}
      <g transform="translate(150 150)">
        <path d="M58 250c-30 0-40-30-34-70 6-42 22-76 52-92l40-4c30 18 44 56 44 98 0 40-14 68-44 68Z" fill={PEACH} />
        <path d="M70 250c-10-34-6-70 10-96" stroke={PEACH_D} strokeWidth="3" fill="none" strokeLinecap="round" />
        <path d="M150 238c26 6 44-6 46-22" stroke={PEACH} strokeWidth="14" fill="none" strokeLinecap="round" />
        <ellipse cx="66" cy="246" rx="22" ry="10" fill={PEACH_D} />
        <ellipse cx="128" cy="248" rx="22" ry="10" fill={PEACH_D} />
        {/* head */}
        <path d="M54 52c0-34 26-56 56-56s54 22 54 56c0 30-20 52-54 52S54 82 54 52Z" fill={PEACH} />
        <path d="M58 28C42 22 28 34 30 62c2 22 14 36 26 34 6-18 6-46 2-68Z" fill={F} />
        <path d="M160 28c16-6 30 6 28 34-2 22-14 36-26 34-6-18-6-46-2-68Z" fill={F} />
        <ellipse cx="110" cy="74" rx="26" ry="20" fill={CREAM} />
        <ellipse cx="110" cy="66" rx="9" ry="6.5" fill={INK} />
        <path d="M110 72v8M100 84c4 4 16 4 20 0" stroke={INK} strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <circle cx="88" cy="46" r="5" fill={INK} />
        <circle cx="132" cy="46" r="5" fill={INK} />
        <circle cx="89.5" cy="44.5" r="1.4" fill={CREAM} />
        <circle cx="133.5" cy="44.5" r="1.4" fill={CREAM} />
        {/* collar */}
        <path d="M66 104c26 14 62 14 88 0" stroke={F} strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle cx="110" cy="116" r="7" fill="#D9A441" />
      </g>

      {/* cat (curled, front right) */}
      <g transform="translate(300 300)">
        <path d="M8 96c-6-40 26-70 74-70 46 0 80 26 78 60-2 14-14 20-30 20H30C18 106 10 104 8 96Z" fill={F} />
        <path d="M150 92c22 4 34-8 28-22" stroke={F} strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d="M24 44 30 10l22 26Z" fill={F} />
        <path d="M70 34 82 4l14 32Z" fill={F} />
        <path d="M30 26l3 -8 8 10Z" fill={PEACH} />
        <path d="M80 22l3 -9 7 11Z" fill={PEACH} />
        <ellipse cx="60" cy="58" rx="40" ry="32" fill={F} />
        <path d="M40 58c4 4 10 4 14 0M70 58c4 4 10 4 14 0" stroke={PEACH} strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <path d="M58 70l4 3 4-3" stroke={PEACH} strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M30 70h-16M30 75l-14 4M92 70h16M92 75l14 4" stroke={SAGE_D} strokeWidth="1.5" strokeLinecap="round" />
      </g>

      {/* rabbit (small, front left) */}
      <g transform="translate(92 318)">
        <ellipse cx="42" cy="66" rx="34" ry="24" fill="#FFFDF8" stroke={SAGE_D} strokeWidth="2" />
        <ellipse cx="70" cy="44" rx="18" ry="16" fill="#FFFDF8" stroke={SAGE_D} strokeWidth="2" />
        <path d="M64 30c-6-22-2-34 4-34s8 14 4 34Z" fill="#FFFDF8" stroke={SAGE_D} strokeWidth="2" />
        <path d="M76 30c2-22 10-32 16-30s2 16-8 32Z" fill="#FFFDF8" stroke={SAGE_D} strokeWidth="2" />
        <path d="M67 10c-1-6 0-10 2-10" stroke={PEACH_D} strokeWidth="3" strokeLinecap="round" />
        <circle cx="76" cy="42" r="2.8" fill={INK} />
        <circle cx="86" cy="49" r="2" fill={PEACH_D} />
        <circle cx="10" cy="62" r="7" fill="#FFFDF8" stroke={SAGE_D} strokeWidth="2" />
      </g>

      {/* small grass tufts */}
      {[[40, 398], [236, 404], [470, 398]].map(([x, y], i) => (
        <path key={i} d={`M${x} ${y}c2-10 4-14 8-18M${x + 8} ${y}c0-12 2-18 6-22M${x + 16} ${y}c-2-8-4-12-8-16`} stroke={FD} strokeWidth="2" fill="none" strokeLinecap="round" />
      ))}
    </svg>
  );
}

/** Small decorative cat-and-leaf vignette for empty states. */
export function EmptyIllustration({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 160 110" aria-hidden focusable={false}>
      <ellipse cx="80" cy="100" rx="70" ry="8" fill={SAGE} />
      <path d="M40 96c-4-26 18-44 46-44 28 0 48 16 46 36-1 8-8 10-18 10H52c-6 0-11-1-12-2Z" fill={SAGE_D} />
      <path d="M50 60 54 40l14 16Z M86 54l8-20 8 22Z" fill={SAGE_D} />
      <path d="M62 78c3 2 7 2 10 0M86 78c3 2 7 2 10 0" stroke={F} strokeWidth="2" fill="none" strokeLinecap="round" />
      <path d="M128 98c8-4 14-14 12-26" stroke={F} strokeWidth="2.5" fill="none" strokeLinecap="round" />
      <ellipse cx="138" cy="70" rx="8" ry="4" fill="#8FAF8B" transform="rotate(-50 138 70)" />
    </svg>
  );
}
