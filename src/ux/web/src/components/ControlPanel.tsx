import type { Controls } from "../lib/useSimulation";

type Props = { c: Controls; set: (c: Controls) => void; regimes: string[] };

const card = "rounded-lg bg-zinc-900/70 border border-zinc-800 p-4";

/** Steer the live simulation: effort, regime, mechanism toggles, seed. */
export function ControlPanel({ c, set, regimes }: Props) {
  const toggle = (k: keyof Controls) => set({ ...c, [k]: !c[k] });
  return (
    <div className={card + " space-y-4"}>
      <div>
        <label className="text-sm text-zinc-400">Esfuerzo (effort): {(c.effort * 100).toFixed(0)}%</label>
        <input type="range" min={0} max={1} step={0.05} value={c.effort}
          onChange={(e) => set({ ...c, effort: +e.target.value })} className="w-full" />
      </div>
      <div>
        <label className="text-sm text-zinc-400">Regime</label>
        <select value={c.regime} onChange={(e) => set({ ...c, regime: e.target.value })}
          className="w-full bg-zinc-800 rounded px-2 py-1 mt-1">
          {regimes.map((r) => (<option key={r} value={r}>{r}</option>))}
        </select>
      </div>
      <div className="flex flex-wrap gap-2 text-sm">
        {(["generational", "opportunity", "network"] as const).map((k) => (
          <button key={k} onClick={() => toggle(k)}
            className={`px-2 py-1 rounded ${c[k] ? "bg-emerald-700" : "bg-zinc-800"}`}>{k}</button>
        ))}
      </div>
      <button onClick={() => set({ ...c, seed: c.seed + 1 })}
        className="w-full bg-zinc-800 rounded py-1 text-sm">reset (seed {c.seed})</button>
    </div>
  );
}
