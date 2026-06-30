import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, ReferenceLine } from "recharts";
import type { HistPoint, Snapshot } from "../lib/useSimulation";
import { Card, InfoTip } from "./ui";

/** Inequality over time: the wealth gap (poor vs rich mean) and the Gini. */
export function InequalityPanel({ snap, history }: { snap: Snapshot | null; history: HistPoint[] }) {
  const line = snap?.cutoffs.poverty_line ?? 0.2;
  const rich = snap?.cutoffs.rich_threshold ?? 1;
  return (
    <Card
      title="Desigualdad en el tiempo"
      subtitle="riqueza media por barrio y coeficiente de Gini de la poblacion viva"
      right={
        <div className="flex items-center gap-2">
          <InfoTip
            title="Desigualdad"
            text="Coeficiente de Gini de la poblacion viva (0 = igualdad total, 1 = maxima concentracion) y riqueza media de cada barrio a lo largo del tiempo. Las lineas punteadas marcan la linea de pobreza y el umbral de riqueza."
          />
          <div className="text-right">
            <div className="text-[11px] text-zinc-500">Gini</div>
            <div className="text-2xl font-bold tabular-nums text-violet-300">{snap?.gini?.toFixed(3) ?? "-"}</div>
          </div>
        </div>
      }
    >
      <ResponsiveContainer width="100%" height={170}>
        <LineChart data={history} margin={{ top: 4, right: 8, left: -22, bottom: 0 }}>
          <XAxis dataKey="tick" tick={{ fill: "#71717a", fontSize: 10 }} />
          <YAxis domain={[0, Math.max(rich, 1)]} tick={{ fill: "#71717a", fontSize: 10 }} />
          <Tooltip
            contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
            labelFormatter={(t) => `tick ${t}`}
            formatter={(v: number, n) => [v.toFixed(3), n === "rich" ? "barrio rico" : "barrio pobre"]}
          />
          <ReferenceLine y={line} stroke="#e5484d" strokeDasharray="4 4" />
          <ReferenceLine y={rich} stroke="#f5c542" strokeDasharray="4 4" />
          <Line type="monotone" dataKey="rich" stroke="#30a46c" dot={false} strokeWidth={2} isAnimationActive={false} />
          <Line type="monotone" dataKey="poor" stroke="#e5484d" dot={false} strokeWidth={2} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
