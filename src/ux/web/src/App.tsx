import { useState } from "react";
import { useSimulation, type Controls } from "./lib/useSimulation";
import { AgentField } from "./components/AgentField";
import { BandChart } from "./components/BandChart";
import { ControlPanel } from "./components/ControlPanel";
import { MobilityPanel } from "./components/MobilityPanel";
import { EffortPanel } from "./components/EffortPanel";
import { InequalityPanel } from "./components/InequalityPanel";
import { OpportunityPanel } from "./components/OpportunityPanel";
import { NetworkPanel } from "./components/NetworkPanel";
import { TalentLuck } from "./components/TalentLuck";
import { Card } from "./components/ui";

const REGIMES = ["baseline", "harsh", "mixed", "protective"];

export default function App() {
  const [c, set] = useState<Controls>({
    effort: 0.5, regime: "baseline", generational: true,
    opportunity: true, network: true, seed: 0,
  });
  const { snap, history, connected } = useSimulation(c);

  return (
    <div className="min-h-screen bg-[#0a0b0f] text-zinc-200">
      <div className="mx-auto max-w-[1320px] px-5 py-6">
        {/* Header */}
        <header className="mb-6 flex flex-wrap items-end justify-between gap-3 border-b border-zinc-800/80 pb-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              La Trampa de Pobreza <span className="text-zinc-500">· simulacion en vivo</span>
            </h1>
            <p className="mt-1 text-sm text-zinc-500">
              modelo basado en agentes · estructura, esfuerzo, oportunidad, redes y generaciones
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className={`h-2.5 w-2.5 rounded-full ${connected ? "bg-emerald-500" : "bg-rose-500"}`} />
            <span className="tabular-nums text-zinc-400">
              {connected ? `tick ${snap?.tick ?? 0}` : "conectando..."}
            </span>
          </div>
        </header>

        {/* Hero row: agent field + mobility KPIs + controls */}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
          <div className="lg:col-span-6">
            <Card title="Poblacion (cada punto, una vida)" subtitle="x = barrio · altura = riqueza · color = banda">
              <AgentField snap={snap} />
            </Card>
          </div>
          <div className="space-y-4 lg:col-span-4">
            <MobilityPanel snap={snap} />
            <BandChartCard snap={snap} />
          </div>
          <div className="lg:col-span-2">
            <ControlPanel c={c} set={set} regimes={REGIMES} />
          </div>
        </div>

        {/* Dynamics grid */}
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          <EffortPanel snap={snap} />
          <InequalityPanel snap={snap} history={history} />
          <OpportunityPanel snap={snap} />
          <NetworkPanel snap={snap} />
          <TalentLuck snap={snap} />
          <Card title="Referencia de variables" subtitle="que representa cada panel">
            <ul className="space-y-2 text-[12px] leading-snug text-zinc-400">
              <li><b className="text-emerald-400">Movilidad:</b> tres niveles para nacidos pobres — cruzar la linea (alguna vez), tiempo de vida fuera de la pobreza (durable) y alcanzar el umbral de riqueza.</li>
              <li><b className="text-rose-400">Eficiencia (&eta;):</b> factor en [&eta;_min, 1] que multiplica el valor creado; depende de la riqueza relativa a la linea y de los estresores.</li>
              <li><b className="text-amber-400">Capital (r·w·s):</b> termino de deriva proporcional a la riqueza ya acumulada.</li>
              <li><b className="text-violet-400">Oportunidad:</b> llegadas Poisson con pagos de distribucion Pareto (cola pesada).</li>
              <li><b className="text-sky-400">Red:</b> conectividad economica c_i y escape colectivo (pooling).</li>
              <li><b className="text-zinc-200">Regimen (&Theta;):</b> conjunto de parametros estructurales; al cambiar el preset se re-corre el mismo cohorte.</li>
            </ul>
          </Card>
        </div>

        <footer className="mt-6 border-t border-zinc-800/80 pt-3 text-[11px] text-zinc-600">
          Modelo open-source · resultados ilustrativos del modelo, no estimaciones calibradas de ningun pais.
        </footer>
      </div>
    </div>
  );
}

function BandChartCard({ snap }: { snap: import("./lib/useSimulation").Snapshot | null }) {
  return (
    <Card title="El continuo (bandas de riqueza)" subtitle="reparto de la poblacion viva por banda">
      <BandChart snap={snap} />
    </Card>
  );
}
