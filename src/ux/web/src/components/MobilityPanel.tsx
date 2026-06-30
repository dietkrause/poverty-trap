import type { Snapshot } from "../lib/useSimulation";
import { Card, InfoTip, pct } from "./ui";

/**
 * Mobility for the born-poor at three levels of strictness, to separate a
 * transient line-crossing from durably living out of poverty:
 *   - left_poverty   : ever crossed the line (first passage; may fall back)
 *   - time_above_line: average share of the life spent above the line (durable)
 *   - became_rich    : reached the rich threshold
 */
export function MobilityPanel({ snap }: { snap: Snapshot | null }) {
  const m = snap?.mobility;
  const poor = m?.poor;
  const rich = m?.rich;
  const gap = m ? (rich!.became_rich - poor!.became_rich) : undefined;

  const Row = ({ label, sub, value, color }: { label: string; sub: string; value?: number; color: string }) => (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="text-xs text-zinc-300">{label}</span>
        <span className="text-2xl font-bold tabular-nums" style={{ color }}>{pct(value)}</span>
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-zinc-800">
        <div className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.max(0, Math.min(1, value ?? 0)) * 100}%`, background: color }} />
      </div>
      <div className="mt-1 text-[11px] text-zinc-500">{sub}</div>
    </div>
  );

  return (
    <Card
      title="Movilidad de los nacidos pobres"
      subtitle="de transitorio a durable: tocar la linea no es vivir fuera de la pobreza"
      right={
        <InfoTip
          title="Los tres niveles (y por que difieren)"
          text="Cruzo la linea: la toco al menos una vez (primer paso); muchos cruces son transitorios por un shock y luego recaen. Tiempo fuera: promedio de la vida pasado sobre la linea (durabilidad real). Se hizo rico: alcanzo el umbral superior. Por eso 'cruzo' > 'tiempo fuera' > 'rico'. Son acumulados desde el (re)inicio y convergen al crecer 'intentos'."
        />
      }
    >
      <div className="space-y-3">
        <Row
          label="Cruzo la linea (alguna vez)"
          sub={`primer paso; incluye cruces transitorios · nacidos ricos: ${pct(rich?.left_poverty)}`}
          value={poor?.left_poverty}
          color="#38bdf8"
        />
        <Row
          label="Tiempo fuera de pobreza (vida)"
          sub={`% promedio de la vida sobre la linea · nacidos ricos: ${pct(rich?.time_above_line)}`}
          value={poor?.time_above_line}
          color="#34d399"
        />
        <Row
          label="Se hizo rico (alcanzo w*)"
          sub={`nacidos ricos: ${pct(rich?.became_rich)}`}
          value={poor?.became_rich}
          color="#f5c542"
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3">
          <div className="text-[11px] text-zinc-500">Brecha por nacimiento</div>
          <div className="text-xl font-semibold tabular-nums text-rose-300">
            {gap == null ? "-" : `+${(gap * 100).toFixed(0)} pts`}
          </div>
          <div className="text-[11px] text-zinc-600">P(rico) rico - pobre</div>
        </div>
        <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3">
          <div className="text-[11px] text-zinc-500">IGE (Gran Gatsby)</div>
          <div className="text-xl font-semibold tabular-nums text-sky-300">
            {m?.ige == null ? "calculando..." : m.ige.toFixed(2)}
          </div>
          <div className="text-[11px] text-zinc-600">elasticidad intergeneracional</div>
        </div>
      </div>
      <div className="mt-2 text-[11px] text-zinc-600">
        intentos: {poor?.attempts ?? 0} pobres / {rich?.attempts ?? 0} ricos
      </div>
    </Card>
  );
}
