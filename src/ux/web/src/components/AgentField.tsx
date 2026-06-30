import { useEffect, useMemo, useRef } from "react";
import type { Snapshot } from "../lib/useSimulation";
import { BAND_COLORS, BAND_ORDER } from "./ui";

const BAND_FILL = ["#1a1012", "#1a150f", "#181711", "#121711", "#0f1713"]; // pobreza..rico, subtle

/** Deterministic [0,1) jitter per agent index so dots keep a stable x position. */
function jitter(i: number): number {
  const x = Math.sin(i * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

/**
 * Agents as dots. x = barrio (pobre izquierda / rico derecha), y = riqueza.
 * Encoding: color = banda, tamano = esfuerzo, opacidad = eficiencia (eta, el
 * impuesto de escasez). Lineas de referencia: pobreza y umbral de riqueza.
 */
export function AgentField({ snap }: { snap: Snapshot | null }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const W = 560;
  const H = 540;
  const offsets = useMemo(() => Array.from({ length: 400 }, (_, i) => jitter(i)), []);

  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d")!;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#0c0e13";
    ctx.fillRect(0, 0, W, H);
    if (!snap) return;

    const top = snap.cutoffs.rich_threshold;
    const pad = 28;
    const yOf = (w: number) => H - pad - Math.max(0, Math.min(1.05, w / top)) * (H - 2 * pad);

    // Band background shading (the continuum), from ruin up to the rich line.
    const edges = [0, snap.cutoffs.poverty_line, snap.cutoffs.band_vulnerable, snap.cutoffs.band_acomodado, top, top * 1.08];
    for (let b = 0; b < 5; b++) {
      const yTop = yOf(edges[b + 1]);
      const yBot = yOf(edges[b]);
      ctx.fillStyle = BAND_FILL[b];
      ctx.fillRect(0, yTop, W, yBot - yTop);
    }

    // Reference lines.
    const line = (y: number, color: string, label: string, dash = true) => {
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.4;
      if (dash) ctx.setLineDash([6, 5]);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = color;
      ctx.font = "11px ui-sans-serif, system-ui";
      ctx.fillText(label, 8, y - 5);
      ctx.restore();
    };
    line(yOf(top), "#f5c542", "umbral de riqueza (Micawber) w*", false);
    line(yOf(snap.cutoffs.poverty_line), "#e5484d", "linea de pobreza w_p");

    // Zone divider + labels.
    ctx.strokeStyle = "#23262f";
    ctx.beginPath();
    ctx.moveTo(W / 2, 0);
    ctx.lineTo(W / 2, H);
    ctx.stroke();
    ctx.fillStyle = "#6b7280";
    ctx.font = "11px ui-sans-serif, system-ui";
    ctx.fillText("barrio pobre", 10, H - 8);
    ctx.fillText("barrio rico", W - 78, H - 8);

    // Agents.
    const a = snap.agents;
    for (let i = 0; i < a.wealth.length; i++) {
      const half = (W - 16) / 2;
      const x = a.zone[i] === 0 ? 10 + offsets[i] * (half - 12) : W / 2 + 8 + offsets[i] * (half - 12);
      const eta = a.eta[i] ?? 0.5;
      const eff = a.effort[i] ?? 0.3;
      ctx.globalAlpha = 0.3 + 0.7 * eta; // opacity = scarcity tax (eta)
      ctx.fillStyle = BAND_COLORS[BAND_ORDER[a.band[i]] ?? "media"];
      ctx.beginPath();
      ctx.arc(x, yOf(a.wealth[i]), 2.4 + 3.2 * eff, 0, 7); // size = effort
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }, [snap, offsets]);

  return (
    <div>
      <canvas ref={ref} width={W} height={H} className="w-full rounded-lg" />
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-zinc-500">
        <span>color = banda</span>
        <span>tamano = esfuerzo (e)</span>
        <span>opacidad = eficiencia (&eta;)</span>
        <span>altura = riqueza (w)</span>
      </div>
    </div>
  );
}
