import { useEffect, useRef, useState } from "react";

export type Controls = {
  effort: number;
  regime: string;
  generational: boolean;
  opportunity: boolean;
  network: boolean;
  seed: number;
};

export type Snapshot = {
  tick: number;
  agents: { wealth: number[]; zone: number[]; band: number[]; talent: number[] };
  gini: number;
  bands: Record<string, number>;
  poverty_line: number;
  rich_threshold: number;
};

const URL = "ws://localhost:8000/ws";

/** Streams snapshots from the engine and pushes control changes back. */
export function useSimulation(controls: Controls) {
  const [snap, setSnap] = useState<Snapshot | null>(null);
  const [connected, setConnected] = useState(false);
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(URL);
    socket.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => setSnap(JSON.parse(e.data));
    return () => ws.close();
  }, []);

  useEffect(() => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify(controls));
    }
  }, [controls]);

  return { snap, connected };
}
