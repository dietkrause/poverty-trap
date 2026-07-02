import type { Snapshot } from "../lib/useSimulation";
import { Card, InfoTip } from "./ui";

// Order and labels follow the drift equation mu = mu_base - premium + alpha*e*eta*q
// + beta_N*c + gamma*peer + r*w*s. Keys are the components' `.name` values; only
// the terms the engine is actually running are streamed (e.g. no network when off).
const TERMS: { key: string; label: string }[] = [
  { key: "neighborhood", label: "barrio (mu_base)" },
  { key: "poverty_premium", label: "prima de pobreza (-pi)" },
  { key: "value_creation", label: "valor (alpha·e·eta·q)" },
  { key: "capital_returns", label: "capital (r·w·s)" },
  { key: "network_drift", label: "red (beta·c)" },
  { key: "peer_influence", label: "pares (gamma·tanh)" },
];

/**
 * The drift decomposition (spec 7.4): the expected per-tick push on wealth, split
 * into its terms, for the poor vs rich zone. This is the mechanism that links the
 * rules to the outcomes - shown for exactly the terms currently active.
 */
export function DriftPanel({ snap }: { snap: Snapshot | null }) {
  const poor = snap?.drift.poor ?? {};
  const rich = snap?.drift.rich ?? {};
  const present = TERMS.filter((t) => t.key in poor || t.key in rich);

  // Shared scale so poor and rich bars are comparable.
  const vals: number[] = present.flatMap((t) => [poor[t.key] ?? 0, rich[t.key] ?? 0]);
  const maxAbs = Math.max(1e-6, ...vals.map((v) => Math.abs(v)));

  const Bar = ({ v, color }: { v: number; color: string }) => {
    const w = (Math.abs(v) / maxAbs) * 50; // half-width %
    return (
      <div className="relative h-3 w-full rounded bg-zinc-800/60">
        <div className="absolute left-1/2 top-0 h-full w-px bg-zinc-600" />
        <div
          className="absolute top-0 h-full rounded"
          style={
            v >= 0
              ? { left: "50%", width: `${w}%`, background: color }
              : { right: "50%", width: `${w}%`, background: color }
          }
        />
      </div>
    );
  };

  const Row = ({ label, tkey }: { label: string; tkey: string }) => {
    const pv = poor[tkey] ?? 0;
    const rv = rich[tkey] ?? 0;
    return (
      <div className="grid grid-cols-[1fr_auto] items-center gap-2">
        <div className="min-w-0">
          <div className="mb-0.5 text-[11px] text-zinc-400">{label}</div>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex items-center gap-1">
              <span className="w-6 text-[9px] text-rose-400">pob</span>
              <div className="flex-1"><Bar v={pv} color="#e5484d" /></div>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-6 text-[9px] text-emerald-400">ric</span>
              <div className="flex-1"><Bar v={rv} color="#30a46c" /></div>
            </div>
          </div>
        </div>
        <div className="w-24 text-right font-mono text-[10px] tabular-nums text-zinc-500">
          {pv >= 0 ? "+" : ""}{(pv * 1000).toFixed(1)} / {rv >= 0 ? "+" : ""}{(rv * 1000).toFixed(1)}
        </div>
      </div>
    );
  };

  const totalP = poor["total"];
  const totalR = rich["total"];

  return (
    <Card
      title="Descomposicion de la deriva (mu)"
      subtitle="empuje esperado sobre la riqueza por termino, x1000 · pobre vs rico"
      right={
        <InfoTip
          title="El corazon del modelo (7.4)"
          text="Cada mes la riqueza recibe un empuje esperado mu = suma de terminos: barrio (mu_base), prima de pobreza (solo bajo la linea), valor creado por el esfuerzo (alpha·e·eta·q), retorno del capital (r·w·s), red (beta·c) y pares (gamma·tanh). Barra a la derecha = empuja hacia arriba; a la izquierda = hacia abajo. Se muestran solo los terminos activos."
        />
      }
    >
      <div className="space-y-2.5">
        {present.length === 0 ? (
          <div className="text-[11px] text-zinc-500">esperando datos...</div>
        ) : (
          present.map((t) => <Row key={t.key} label={t.label} tkey={t.key} />)
        )}
      </div>
      {(totalP != null || totalR != null) && (
        <div className="mt-3 flex items-center justify-between border-t border-zinc-800 pt-2 text-[11px]">
          <span className="text-zinc-400">deriva neta (x1000)</span>
          <span className="font-mono tabular-nums">
            <span className="text-rose-300">pob {((totalP ?? 0) * 1000).toFixed(1)}</span>
            <span className="text-zinc-600"> · </span>
            <span className="text-emerald-300">ric {((totalR ?? 0) * 1000).toFixed(1)}</span>
          </span>
        </div>
      )}
      <p className="mt-2 text-[11px] leading-snug text-zinc-500">
        Aparte de la deriva, cada tick suma un shock aleatorio de media cero (ruido &sigma;):
        &sigma;<sub>pobre</sub> {(snap?.noise.sigma_poor ?? 0).toFixed(2)} vs
        &sigma;<sub>rico</sub> {(snap?.noise.sigma_rich ?? 0).toFixed(2)} — los golpes pegan
        mas fuerte al pobre (se ven como la dispersion en el campo de agentes).
      </p>
    </Card>
  );
}
