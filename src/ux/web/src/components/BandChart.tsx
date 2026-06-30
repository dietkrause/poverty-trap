import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";
import type { Snapshot } from "../lib/useSimulation";

const BAND_COLORS: Record<string, string> = {
  pobreza: "#d64545", vulnerable: "#e08a3c", media: "#d8c84a",
  acomodado: "#7bbf5a", rico: "#2f9e44",
};

/** Population share in each wealth band - the live continuum distribution. */
export function BandChart({ snap }: { snap: Snapshot | null }) {
  const order = ["pobreza", "vulnerable", "media", "acomodado", "rico"];
  const data = order.map((k) => ({ band: k, share: snap ? (snap.bands[k] ?? 0) : 0 }));
  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data}>
        <XAxis dataKey="band" tick={{ fill: "#9aa0aa", fontSize: 11 }} />
        <YAxis domain={[0, 1]} tick={{ fill: "#9aa0aa", fontSize: 11 }} />
        <Bar dataKey="share">
          {data.map((d) => (<Cell key={d.band} fill={BAND_COLORS[d.band]} />))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
