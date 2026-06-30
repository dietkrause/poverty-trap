import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, ResponsiveContainer, Tooltip, ReferenceLine, Cell } from "recharts";
import type { Snapshot } from "../lib/useSimulation";
import { BAND_COLORS, BAND_ORDER, Card, InfoTip } from "./ui";

/**
 * Talent (Normal) vs final wealth (power law). The point of the model: the very
 * top is not the most talented - normal talent, multiplicative wealth, heavy tail.
 */
export function TalentLuck({ snap }: { snap: Snapshot | null }) {
  const a = snap?.agents;
  const data =
    a?.wealth.map((w, i) => ({ talent: a.talent[i], wealth: w, band: BAND_ORDER[a.band[i]] ?? "media" })) ?? [];
  const rich = snap?.cutoffs.rich_threshold ?? 1;
  return (
    <Card
      title="Talento y riqueza"
      subtitle="talento ~ Normal; riqueza con cola pesada (ref. Pluchino 2018)"
      right={
        <InfoTip
          title="Talento vs riqueza"
          text="Cada punto es un agente vivo: eje x = talento (fijo al nacer, ~Normal), eje y = riqueza. La linea dorada marca el umbral de riqueza. Como la riqueza crece de forma multiplicativa, su distribucion tiene cola pesada aunque el talento sea Normal."
        />
      }
    >
      <ResponsiveContainer width="100%" height={170}>
        <ScatterChart margin={{ top: 6, right: 8, left: -22, bottom: 0 }}>
          <XAxis
            type="number"
            dataKey="talent"
            name="talento"
            domain={[-3, 3]}
            tick={{ fill: "#71717a", fontSize: 10 }}
          />
          <YAxis
            type="number"
            dataKey="wealth"
            name="riqueza"
            domain={[0, Math.max(rich, 1)]}
            tick={{ fill: "#71717a", fontSize: 10 }}
          />
          <ZAxis range={[18, 18]} />
          <ReferenceLine y={rich} stroke="#f5c542" strokeDasharray="4 4" />
          <Tooltip
            cursor={{ stroke: "#3f3f46" }}
            contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
            formatter={(v: number, n) => [Number(v).toFixed(2), n === "wealth" ? "riqueza" : "talento"]}
          />
          <Scatter data={data} fillOpacity={0.7}>
            {data.map((d, i) => (
              <Cell key={i} fill={BAND_COLORS[d.band]} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <p className="mt-2 text-[11px] leading-snug text-zinc-500">
        El talento se distribuye Normal. Como la riqueza crece de forma multiplicativa, su
        distribucion resultante tiene cola pesada, y la correlacion entre talento y riqueza
        final es debil en la cola alta.
      </p>
    </Card>
  );
}
