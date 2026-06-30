import type { Snapshot } from "../lib/useSimulation";
import { Card, InfoTip, Meter } from "./ui";

/** Social capital: connectedness (Chetty) + collective pooling escapes. */
export function NetworkPanel({ snap }: { snap: Snapshot | null }) {
  const p = snap?.zones.poor;
  const r = snap?.zones.rich;
  return (
    <Card
      title="Red y pooling"
      subtitle="c_i = fraccion de tus contactos sobre la linea (conectividad economica)"
      right={
        <div className="flex items-center gap-2">
          <InfoTip
            title="Red y pooling"
            text="Conectividad (c_i): fraccion de los contactos de un agente que estan sobre la linea de pobreza; alimenta la deriva y la tasa de oportunidad. pooling: numero acumulado de escapes colectivos (un grupo combina recursos para que un miembro cruce el umbral)."
          />
          <div className="text-right">
            <div className="text-[11px] text-zinc-500">pooling</div>
            <div className="text-xl font-bold tabular-nums text-sky-300">{snap?.pooling.events ?? 0}</div>
          </div>
        </div>
      }
    >
      <div className="space-y-3">
        <Meter label="conectividad - barrio pobre" value={p?.conn ?? 0} color="#e5484d" />
        <Meter label="conectividad - barrio rico" value={r?.conn ?? 0} color="#30a46c" />
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-2">
          <div className="text-zinc-500">sobre la linea (pobre)</div>
          <div className="text-base tabular-nums text-zinc-200">{((p?.above_line ?? 0) * 100).toFixed(0)}%</div>
        </div>
        <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-2">
          <div className="text-zinc-500">sobre la linea (rico)</div>
          <div className="text-base tabular-nums text-zinc-200">{((r?.above_line ?? 0) * 100).toFixed(0)}%</div>
        </div>
      </div>
      <p className="mt-3 text-[11px] leading-snug text-zinc-500">
        El grafo se forma con homofilia (conexion preferente dentro del mismo barrio). El
        pooling permite que un grupo combine recursos para que un miembro cruce el umbral.
      </p>
    </Card>
  );
}
