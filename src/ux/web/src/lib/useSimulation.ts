import { useEffect, useRef, useState } from "react";

export type Controls = {
  effort: number;
  regime: string;
  generational: boolean;
  opportunity: boolean;
  network: boolean;
  seed: number;
  params?: Record<string, number>;
};

export type ZoneStat = {
  count: number;
  wealth: number;
  eta: number;
  q: number;
  savings: number;
  conn: number;
  above_line: number;
  above_rich: number;
};

export type Mobility = {
  birth_policy: string;
  poor: { attempts: number; became_rich: number; time_above_line: number; left_poverty: number };
  rich: { attempts: number; became_rich: number; time_above_line: number; left_poverty: number };
  ige: number | null;
};

export type Snapshot = {
  tick: number;
  cutoffs: {
    poverty_line: number;
    band_vulnerable: number;
    band_acomodado: number;
    rich_threshold: number;
  };
  gini: number;
  bands: Record<string, number>;
  agents: {
    wealth: number[];
    zone: number[];
    band: number[];
    talent: number[];
    skill: number[];
    effort: number[];
    eta: number[];
    q: number[];
    savings: number[];
    conn: number[];
    generation: number[];
  };
  zones: { poor: ZoneStat; rich: ZoneStat };
  opportunity: { arrived: number; captured: number; captured_value: number; payoffs: number[] };
  pooling: { events: number };
  mobility?: Mobility;
  controls?: Partial<Controls>;
};

export type HistPoint = { tick: number; gini: number; poor: number; rich: number };

const URL = "ws://localhost:8000/ws";
const HIST_MAX = 160;

/** Streams snapshots from the engine, keeps a short time-series, pushes controls back. */
export function useSimulation(controls: Controls) {
  const [snap, setSnap] = useState<Snapshot | null>(null);
  const [history, setHistory] = useState<HistPoint[]>([]);
  const [connected, setConnected] = useState(false);
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(URL);
    socket.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      const s: Snapshot = JSON.parse(e.data);
      setSnap(s);
      setHistory((h) => {
        const next = [...h, { tick: s.tick, gini: s.gini, poor: s.zones.poor.wealth, rich: s.zones.rich.wealth }];
        return next.length > HIST_MAX ? next.slice(next.length - HIST_MAX) : next;
      });
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify(controls));
      setHistory([]); // a control change rebuilds the sim; start a fresh series
    }
  }, [controls]);

  return { snap, history, connected };
}
