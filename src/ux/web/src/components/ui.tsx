import type { ReactNode } from "react";

export const BAND_COLORS: Record<string, string> = {
  pobreza: "#e5484d",
  vulnerable: "#e08a3c",
  media: "#d8c84a",
  acomodado: "#7bbf5a",
  rico: "#30a46c",
};
export const BAND_ORDER = ["pobreza", "vulnerable", "media", "acomodado", "rico"];
export const BAND_LABELS: Record<string, string> = {
  pobreza: "Pobreza",
  vulnerable: "Vulnerable",
  media: "Clase media",
  acomodado: "Acomodado",
  rico: "Rico",
};

/** A titled surface. The visual unit of the dashboard. */
export function Card({
  title,
  subtitle,
  right,
  className = "",
  children,
}: {
  title?: string;
  subtitle?: string;
  right?: ReactNode;
  className?: string;
  children: ReactNode;
}) {
  return (
    <section
      className={
        "rounded-xl border border-zinc-800/80 bg-gradient-to-b from-zinc-900/80 to-zinc-900/40 " +
        "p-4 shadow-lg shadow-black/20 backdrop-blur " +
        className
      }
    >
      {(title || right) && (
        <header className="mb-3 flex items-start justify-between gap-3">
          <div>
            {title && <h3 className="text-sm font-semibold tracking-tight text-zinc-100">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-[11px] leading-tight text-zinc-500">{subtitle}</p>}
          </div>
          {right}
        </header>
      )}
      {children}
    </section>
  );
}

/** A single big number with a label and optional accent + footnote. */
export function Stat({
  label,
  value,
  accent = "text-zinc-100",
  foot,
}: {
  label: string;
  value: ReactNode;
  accent?: string;
  foot?: ReactNode;
}) {
  return (
    <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/50 p-4">
      <div className="text-[11px] uppercase tracking-wide text-zinc-500">{label}</div>
      <div className={"mt-1 text-3xl font-bold tabular-nums " + accent}>{value}</div>
      {foot && <div className="mt-1 text-[11px] text-zinc-500">{foot}</div>}
    </div>
  );
}

/** A 0..1 labelled progress bar (used for eta / q / connectedness comparisons). */
export function Meter({ label, value, color, hint }: { label: string; value: number; color: string; hint?: string }) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <div>
      <div className="flex items-baseline justify-between text-[11px]">
        <span className="text-zinc-400">{label}</span>
        <span className="tabular-nums text-zinc-300">{value.toFixed(2)}{hint}</span>
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-zinc-800">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

export const pct = (x: number | undefined) => (x == null ? "-" : `${(x * 100).toFixed(0)}%`);

/** A hoverable "i" that reveals a small explanation popover (neutral, descriptive). */
export function InfoTip({ title, text }: { title?: string; text: string }) {
  return (
    <span className="group relative inline-flex shrink-0 align-middle">
      <span
        className="flex h-4 w-4 cursor-help items-center justify-center rounded-full border border-zinc-600
          text-[10px] font-semibold leading-none text-zinc-400 hover:border-zinc-400 hover:text-zinc-200"
        aria-hidden
      >
        i
      </span>
      <span
        role="tooltip"
        className="pointer-events-none absolute right-0 top-6 z-50 hidden w-64 rounded-lg border border-zinc-700
          bg-zinc-900 p-2.5 text-[11px] font-normal leading-snug text-zinc-300 shadow-xl group-hover:block"
      >
        {title && <span className="mb-1 block font-semibold text-zinc-100">{title}</span>}
        {text}
      </span>
    </span>
  );
}
