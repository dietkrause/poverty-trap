import type { Snapshot } from "../lib/useSimulation";
import { Card, InfoTip, Meter } from "./ui";

/**
 * What effort actually is in the model: magnitude x efficiency x quality.
 * Shows the scarcity tax directly - the same effort buys less when poor.
 */
export function EffortPanel({ snap }: { snap: Snapshot | null }) {
  const p = snap?.zones.poor;
  const r = snap?.zones.rich;
  return (
    <Card
      title="Descomposicion del esfuerzo"
      subtitle="valor = alpha · e · eta · q  (magnitud × eficiencia × calidad)"
      right={
        <InfoTip
          title="Esfuerzo en el modelo"
          text="eta (eficiencia) en [eta_min,1] depende de la riqueza respecto a la linea y de los estresores; q (calidad) en [q_min,1] crece con la skill. Ambos multiplican el esfuerzo e antes de convertirse en valor, por lo que un mismo e rinde distinto segun el barrio."
        />
      }
    >
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-3">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-rose-400">Barrio pobre</div>
          <Meter label="eficiencia eta" value={p?.eta ?? 0} color="#e5484d" />
          <Meter label="calidad q (destreza)" value={p?.q ?? 0} color="#e08a3c" />
          <Meter label="ahorro s (capital)" value={p?.savings ?? 0} color="#8b8b8b" />
        </div>
        <div className="space-y-3">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-emerald-400">Barrio rico</div>
          <Meter label="eficiencia eta" value={r?.eta ?? 0} color="#30a46c" />
          <Meter label="calidad q" value={r?.q ?? 0} color="#7bbf5a" />
          <Meter label="ahorro s" value={r?.savings ?? 0} color="#bcbcbc" />
        </div>
      </div>
      <p className="mt-3 text-[11px] leading-snug text-zinc-500">
        eta y q multiplican el esfuerzo e antes de convertirse en valor. eta decrece con la
        cercania a la linea de pobreza y con los estresores (calibracion: Mani 2013), por lo
        que un mismo e produce distinto valor segun la posicion del agente.
      </p>
    </Card>
  );
}
