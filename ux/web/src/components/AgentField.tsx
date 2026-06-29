import { useEffect, useRef } from "react";
import type { Snapshot } from "../lib/useSimulation";

// Wealth -> color: deep red (debt) -> yellow (baseline) -> green (rich).
function wealthColor(w: number, top: number): string {
  const t = Math.max(0, Math.min(1, w / top));
  if (t < 0.5) {
    const k = t / 0.5;
    return `rgb(${214 - 40 * k},${69 + 130 * k},${69 + 20 * k})`;
  }
  const k = (t - 0.5) / 0.5;
  return `rgb(${174 - 127 * k},199,${89 + 45 * k})`;
}

/** Agents as dots: x by zone (left poor / right rich), y by wealth; band lines. */
export function AgentField({ snap }: { snap: Snapshot | null }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d")!;
    const W = c.width, H = c.height, top = snap?.rich_threshold ?? 1;
    ctx.fillStyle = "#0e1016";
    ctx.fillRect(0, 0, W, H);
    if (!snap) return;
    const yOf = (w: number) => H - 24 - Math.max(0, Math.min(1, w / top)) * (H - 48);
    // reference lines
    ctx.strokeStyle = "#d4dc78"; ctx.beginPath();
    ctx.moveTo(0, yOf(top)); ctx.lineTo(W, yOf(top)); ctx.stroke();
    ctx.strokeStyle = "#5a5a5a"; ctx.beginPath();
    ctx.moveTo(0, yOf(snap.poverty_line)); ctx.lineTo(W, yOf(snap.poverty_line)); ctx.stroke();
    const { wealth, zone } = snap.agents;
    for (let i = 0; i < wealth.length; i++) {
      const x = (zone[i] === 0 ? 0.05 + 0.4 * Math.random() : 0.55 + 0.4 * Math.random()) * W;
      ctx.fillStyle = wealthColor(wealth[i], top);
      ctx.beginPath(); ctx.arc(x, yOf(wealth[i]), 3, 0, 7); ctx.fill();
    }
  }, [snap]);

  return <canvas ref={ref} width={520} height={520} className="w-full rounded-lg" />;
}
