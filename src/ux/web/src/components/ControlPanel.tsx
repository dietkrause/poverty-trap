import type { Controls } from "../lib/useSimulation";
import { Card, InfoTip } from "./ui";

type Props = { c: Controls; set: (c: Controls) => void; regimes: string[] };

const LABELS: Record<string, string> = {
  generational: "herencia",
  opportunity: "oportunidad",
  network: "red",
};

/** Steer the live simulation: effort, regime, mechanism toggles, seed, advanced dials. */
export function ControlPanel({ c, set, regimes }: Props) {
  const toggle = (k: "generational" | "opportunity" | "network") => set({ ...c, [k]: !c[k] });
  const setParam = (k: string, v: number) => set({ ...c, params: { ...(c.params ?? {}), [k]: v } });
  const param = (k: string, d: number) => c.params?.[k] ?? d;

  return (
    <Card title="Controles" subtitle="al cambiar un control, la simulacion se reconstruye">
      <div className="space-y-4">
        <div>
          <label className="flex items-baseline justify-between text-xs text-zinc-400">
            <span className="flex items-center gap-1.5">
              Esfuerzo (e)
              <InfoTip
                title="Esfuerzo (e)"
                text="Nivel de esfuerzo de todos los agentes, en [0,1]. Entra en la deriva como alpha·e·eta·q. Subirlo aumenta el valor creado por periodo; el efecto pasa por eta (eficiencia) y q (calidad), por lo que varia segun la posicion del agente."
              />
            </span>
            <span className="tabular-nums text-emerald-400">{(c.effort * 100).toFixed(0)}%</span>
          </label>
          <input
            type="range" min={0} max={1} step={0.05} value={c.effort}
            onChange={(e) => set({ ...c, effort: +e.target.value })}
            className="mt-1 w-full accent-emerald-500"
          />
        </div>

        <div>
          <label className="flex items-center gap-1.5 text-xs text-zinc-400">
            Regimen (pais / politica)
            <InfoTip
              title="Regimen (Theta)"
              text="Preset de parametros estructurales: prima de pobreza, tasa y concentracion de oportunidad, piso de bienestar, educacion y redistribucion. Re-corre el mismo cohorte bajo otra estructura, de modo que las diferencias se deben a la politica y no al azar."
            />
          </label>
          <select
            value={c.regime}
            onChange={(e) => set({ ...c, regime: e.target.value, params: {} })}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-2 py-1.5 text-sm capitalize"
          >
            {regimes.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div>
          <div className="mb-1 flex items-center gap-1.5 text-xs text-zinc-400">
            Mecanismos
            <InfoTip
              title="Mecanismos"
              text="herencia: al resolverse una vida el hijo hereda riqueza, talento, zona y ventaja educativa (afecta la IGE); desactivarlo reinicia cada vida desde cero. oportunidad: llegadas Poisson con pagos Pareto, capturadas con skill y esfuerzo efectivo. red: grafo con homofilia, conectividad economica, influencia de pares y pooling."
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {(["generational", "opportunity", "network"] as const).map((k) => (
              <button
                key={k}
                onClick={() => toggle(k)}
                className={
                  "rounded-full px-3 py-1 text-xs font-medium transition " +
                  (c[k] ? "bg-emerald-600/90 text-white" : "bg-zinc-800 text-zinc-500")
                }
              >
                {LABELS[k]}
              </button>
            ))}
          </div>
        </div>

        <details className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
          <summary className="cursor-pointer text-xs text-zinc-400">Avanzado (dial de regimen Theta)</summary>
          <div className="mt-3 space-y-3">
            <div>
              <label className="flex justify-between text-[11px] text-zinc-500">
                <span className="flex items-center gap-1.5">
                  prima de pobreza pi_0
                  <InfoTip
                    title="Prima de pobreza (pi_0)"
                    text="Deriva negativa adicional mientras la riqueza esta bajo la linea de pobreza. Valores mayores hacen la trampa mas persistente (mas dificil de cruzar la linea)."
                  />
                </span>
                <span className="tabular-nums">{param("premium", 0.004).toFixed(3)}</span>
              </label>
              <input type="range" min={0} max={0.012} step={0.001} value={param("premium", 0.004)}
                onChange={(e) => setParam("premium", +e.target.value)} className="w-full accent-rose-500" />
            </div>
            <div>
              <label className="flex justify-between text-[11px] text-zinc-500">
                <span className="flex items-center gap-1.5">
                  redistribucion t
                  <InfoTip
                    title="Redistribucion (t)"
                    text="Tasa que grava la riqueza por encima del umbral y la transfiere a los agentes bajo la linea. Valores mayores reducen la desigualdad (Gini) y elevan la movilidad de los de abajo."
                  />
                </span>
                <span className="tabular-nums">{param("redistribution", 0).toFixed(2)}</span>
              </label>
              <input type="range" min={0} max={0.15} step={0.01} value={param("redistribution", 0)}
                onChange={(e) => setParam("redistribution", +e.target.value)} className="w-full accent-sky-500" />
            </div>
          </div>
        </details>

        <button
          onClick={() => set({ ...c, seed: c.seed + 1 })}
          className="w-full rounded-lg border border-zinc-700 bg-zinc-800 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700"
        >
          reiniciar cohorte (seed {c.seed})
        </button>
      </div>
    </Card>
  );
}
