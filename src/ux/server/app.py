"""FastAPI WebSocket backend: stream simulation frames to the web UI.

This is the only place that bridges the headless engine to the browser. A client
connects to /ws and sends a small control JSON ({effort, regime, generational,
opportunity, network, seed}); the server builds a simulation, attaches the
engine's SnapshotEmitter observer (the only coupling, and it is read-only), and
streams one frame every few ticks. New control messages rebuild the sim.

Run:
    pip install -r src/ux/server/requirements.txt
    python -m uvicorn app:app --reload --app-dir src/ux/server   # from repo root
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

SRC = Path(__file__).resolve().parents[2]  # .../src (holds the `simulation` package)
sys.path.insert(0, str(SRC))

from simulation.builder import build_simulation  # noqa: E402
from simulation.core.config import ModelParams  # noqa: E402
from simulation.core.engine import Simulation  # noqa: E402
from simulation.observe.stream import SnapshotEmitter  # noqa: E402
from simulation.population.lifecycle import FirstPassageMonitor  # noqa: E402
from simulation.regimes.presets import PRESETS  # noqa: E402

app = FastAPI(title="poverty-trap UX")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def make_params(ctrl: dict) -> ModelParams:
    name = ctrl.get("regime", "baseline")
    base = PRESETS[name] if name in PRESETS else ModelParams()
    # Allow the UI to override any configurable hyperparameter.
    overrides = ctrl.get("params") or {}
    valid = {f for f in ModelParams.__dataclass_fields__}
    safe = {k: v for k, v in overrides.items() if k in valid}
    return base.evolve(**safe) if safe else base


def build(ctrl: dict) -> Simulation:
    sim = build_simulation(
        make_params(ctrl),
        seed=int(ctrl.get("seed", 0)),
        effort=float(ctrl.get("effort", 0.5)),
        generational=bool(ctrl.get("generational", True)),
        with_opportunity=bool(ctrl.get("opportunity", True)),
        with_network=bool(ctrl.get("network", True)),
    )
    return sim


def find_monitor(sim: Simulation) -> FirstPassageMonitor | None:
    """Locate the first-passage monitor so the live mobility rates can be read."""
    for pop in sim.population_processes:
        if isinstance(pop, FirstPassageMonitor):
            return pop
    return None


@app.websocket("/ws")
async def ws(socket: WebSocket) -> None:
    await socket.accept()
    ctrl = {"effort": 0.5, "regime": "baseline"}
    frames: list[dict] = []
    sim = build(ctrl)
    sim.observers.append(SnapshotEmitter(sink=frames.append, every=15, drift_terms=sim.drift_terms))
    monitor = find_monitor(sim)
    try:
        while True:
            # Non-blocking check for a new control message.
            try:
                msg = await asyncio.wait_for(socket.receive_text(), timeout=0.001)
                ctrl.update(json.loads(msg))
                sim = build(ctrl)
                sim.observers.append(SnapshotEmitter(sink=frames.append, every=15, drift_terms=sim.drift_terms))
                monitor = find_monitor(sim)
                frames.clear()
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass

            sim.step()
            if frames:
                frame = frames.pop()
                frames.clear()
                # Merge the live two-probability mobility report (+ IGE) into the frame.
                if monitor is not None:
                    frame["mobility"] = monitor.report()
                frame["controls"] = {k: ctrl.get(k) for k in
                                     ("effort", "regime", "generational", "opportunity", "network", "seed")}
                await socket.send_text(json.dumps(frame))
            await asyncio.sleep(0.03)
    except WebSocketDisconnect:
        return


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "regimes": list(PRESETS)}
