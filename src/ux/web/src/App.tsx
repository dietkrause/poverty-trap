import { useState } from "react";
import { useSimulation, type Controls } from "./lib/useSimulation";
import { AgentField } from "./components/AgentField";
import { BandChart } from "./components/BandChart";
import { ControlPanel } from "./components/ControlPanel";

const REGIMES = ["baseline", "harsh", "mixed", "protective"];
const card = "rounded-lg bg-zinc-900/70 border border-zinc-800 p-4";

export default function App() {
  const [c, set] = useState<Controls>({
    effort: 0.5, regime: "baseline", generational: true,
    opportunity: true, network: true, seed: 0,
  });
  const { snap, connected } = useSimulation(c);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="flex items-baseline justify-between mb-4">
        <h1 className="text-2xl font-bold">Poverty Trap - live simulation</h1>
        <span className={`text-sm ${connected ? "text-emerald-400" : "text-red-400"}`}>
          {connected ? `tick ${snap?.tick ?? 0}` : "connecting..."}
        </span>
      </header>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <div className={card}><AgentField snap={snap} /></div>
          <div className={card}>
            <div className="text-sm text-zinc-400 mb-2">Wealth bands (continuum)</div>
            <BandChart snap={snap} />
          </div>
        </div>
        <div className="space-y-4">
          <ControlPanel c={c} set={set} regimes={REGIMES} />
          <div className={card}>
            <div className="text-sm text-zinc-400">Gini</div>
            <div className="text-3xl font-bold">{snap?.gini?.toFixed(3) ?? "-"}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
