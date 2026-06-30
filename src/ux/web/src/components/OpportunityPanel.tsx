import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import type { Snapshot } from "../lib/useSimulation";
import { Card, InfoTip } from "./ui";

/** Bucket payoffs to expose the heavy tail: many tiny, a few life-changing. */
function histogram(payoffs: number[]) {
  const edges = [0, 0.05, 0.1, 0.2, 0.4, 0.8, Infinity];
  const labels = ["<.05", ".05-.1", ".1-.2", ".2-.4", ".4-.8", ">.8"];
  const counts = new Array(labels.length).fill(0);
  for (const x of payoffs) {
    for (let i = 0; i < edges.length - 1; i++) {
      if (x >= edges[i] && x < edges[i + 1]) {
        counts[i]++;
        break;
      }
    }
  }
  return labels.map((bin, i) => ({ bin, n: counts[i] }));
}

/** Opportunity = access (rate) + luck (Pareto size) + merit (capture gate). */
export function OpportunityPanel({ snap }: { snap: Snapshot | null }) {
  const o = snap?.opportunity;
  const data = useMemo(() => histogram(o?.payoffs ?? []), [o?.payoffs]);
  const rate = o && o.arrived ? o.captured / o.arrived : 0;
  return (
    <Card
      title="Oportunidad"
      subtitle="Pr(X>x) = (x_min / x)^a  ·  pagos con distribucion de Pareto"
      right={
        <div className="flex items-center gap-2">
          <InfoTip
            title="Oportunidad"
            text="Histograma de los tamanos de pago de las oportunidades que llegan. La distribucion de Pareto implica muchas pequenas y pocas muy grandes (cola pesada). 'capturadas' = fraccion de las que llegaron que el agente pudo aprovechar (segun skill y esfuerzo)."
          />
          <div className="text-right">
            <div className="text-[11px] text-zinc-500">capturadas</div>
            <div className="text-xl font-bold tabular-nums text-violet-300">{(rate * 100).toFixed(0)}%</div>
          </div>
        </div>
      }
    >
      <ResponsiveContainer width="100%" height={130}>
        <BarChart data={data} margin={{ top: 4, right: 4, left: -26, bottom: 0 }}>
          <XAxis dataKey="bin" tick={{ fill: "#71717a", fontSize: 10 }} interval={0} />
          <YAxis tick={{ fill: "#71717a", fontSize: 10 }} allowDecimals={false} />
          <Tooltip
            cursor={{ fill: "#ffffff08" }}
            contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
            formatter={(v: number) => [v, "eventos"]}
          />
          <Bar dataKey="n" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-2 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="text-zinc-500">llegaron</div><div className="tabular-nums text-zinc-200">{o?.arrived ?? 0}</div></div>
        <div><div className="text-zinc-500">capturadas</div><div className="tabular-nums text-zinc-200">{o?.captured ?? 0}</div></div>
        <div><div className="text-zinc-500">valor</div><div className="tabular-nums text-zinc-200">{(o?.captured_value ?? 0).toFixed(1)}</div></div>
      </div>
    </Card>
  );
}
