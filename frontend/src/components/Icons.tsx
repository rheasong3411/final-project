// Small inline icon set (stroke icons, decorative unless a title is given).
import type { SVGProps } from "react";

type P = SVGProps<SVGSVGElement> & { size?: number };
const base = (size = 18): SVGProps<SVGSVGElement> => ({
  width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor",
  strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true, focusable: false,
});

export const IconCheck = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><circle cx="12" cy="12" r="9" /><path d="m8 12.5 2.6 2.5L16 9.5" /></svg>);
export const IconX = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><circle cx="12" cy="12" r="9" /><path d="m9 9 6 6M15 9l-6 6" /></svg>);
export const IconQuestion = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><circle cx="12" cy="12" r="9" /><path d="M9.6 9.3a2.5 2.5 0 0 1 4.8.9c0 1.7-2.4 2.2-2.4 3.6" /><path d="M12 17h.01" /></svg>);
export const IconInfo = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></svg>);
export const IconAlert = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M12 3 2.5 20h19L12 3Z" /><path d="M12 10v4M12 17h.01" /></svg>);
export const IconExternal = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M14 4h6v6M20 4l-9 9" /><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" /></svg>);
export const IconPin = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21Z" /><circle cx="12" cy="9.5" r="2.5" /></svg>);
export const IconClock = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg>);
export const IconLock = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><rect x="5" y="11" width="14" height="9" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></svg>);
export const IconArrow = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M5 12h14M13 6l6 6-6 6" /></svg>);
export const IconMenu = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M4 7h16M4 12h16M4 17h16" /></svg>);
export const IconPlus = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M12 5v14M5 12h14" /></svg>);
export const IconMinus = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M5 12h14" /></svg>);
export const IconDoc = ({ size, ...p }: P) => (<svg {...base(size)} {...p}><path d="M7 3h7l5 5v12a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" /><path d="M14 3v5h5M9 13h6M9 17h6" /></svg>);
export const IconPaw = ({ size, ...p }: P) => (
  <svg width={size ?? 18} height={size ?? 18} viewBox="0 0 24 24" fill="currentColor" aria-hidden focusable={false} {...p}>
    <ellipse cx="12" cy="15.5" rx="4.6" ry="3.8" /><ellipse cx="6.4" cy="10.4" rx="1.9" ry="2.5" /><ellipse cx="9.8" cy="7.2" rx="1.9" ry="2.5" />
    <ellipse cx="14.2" cy="7.2" rx="1.9" ry="2.5" /><ellipse cx="17.6" cy="10.4" rx="1.9" ry="2.5" />
  </svg>
);
