import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip } from "recharts";
import type { Snapshot } from "../lib/useSimulation";
import { BAND_COLORS, BAND_LABELS, BAND_ORDER } from "./ui";

/** Population share in each wealth band - the live continuum distribution. */
export function BandChart({ snap }: { snap: Snapshot | null }) {
  const data = BAND_ORDER.map((k) => ({
    band: BAND_LABELS[k],
    key: k,
    share: snap ? (snap.bands[k] ?? 0) : 0,
  }));
  return (
    <ResponsiveContainer width="100%" height={170}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: -22, bottom: 0 }}>
        <XAxis dataKey="band" tick={{ fill: "#9aa0aa", fontSize: 10 }} interval={0} />
        <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fill: "#9aa0aa", fontSize: 10 }} />
        <Tooltip
          cursor={{ fill: "#ffffff08" }}
          contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
          formatter={(v: number) => [`${(v * 100).toFixed(1)}%`, "poblacion"]}
        />
        <Bar dataKey="share" radius={[4, 4, 0, 0]}>
          {data.map((d) => (
            <Cell key={d.key} fill={BAND_COLORS[d.key]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
