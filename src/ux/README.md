# ux - live visualization

A web UI to watch the simulation evolve. It is fully isolated from the engine:
the only coupling is the read-only `SnapshotEmitter` observer
(`src/simulation/observe/stream.py`), which streams compact frames; nothing in
`src/` depends on this folder.

```
src/ux/
  server/   FastAPI WebSocket backend (streams sim frames)
  web/      Vite + React + TypeScript + Tailwind frontend
```

## Run

Backend (from repo root):

```bash
pip install -r src/ux/server/requirements.txt
python -m uvicorn app:app --app-dir src/ux/server   # serves ws://localhost:8000/ws
```

Frontend:

```bash
cd src/ux/web
npm install
npm run dev                            # http://localhost:5173
```

## What you see

The dashboard is designed to mirror the mathematical model in full - every panel
maps to a mechanism in [`../../docs/README.md`](../../docs/README.md) section 7:

- **Agent field**: dots by zone (poor left / rich right) and wealth (height); color
  = band, size = effort `e`, opacity = efficiency `eta`; the poverty line and the
  Micawber threshold `w*` are drawn in.
- **Mobility**: the three per-life outcomes for the born-poor - crossed the line
  (first passage), time spent above the line (durability), and reached `w*` - plus
  the birth gap, IGE, and mean lineage generation.
- **Drift decomposition (mu)**: the expected per-tick push on wealth split into its
  terms (neighbourhood, poverty premium, value creation, capital, network, peer),
  poor vs rich, for exactly the terms currently active; the mean-zero shock `sigma`
  is noted alongside. This is the model's section 7.4 made visible.
- **Effort**: efficiency `eta`, quality `q`, savings `s` and stressors `St`, poor
  vs rich (the scarcity tax).
- **Continuum**: the live wealth-band distribution.
- **Inequality**: Gini and the poor/rich mean-wealth gap over time.
- **Opportunity**: the heavy-tailed (Pareto) payoff histogram and capture rate.
- **Network**: connectedness `c` by zone and collective-pooling events.
- **Talent vs wealth**: the talent-vs-final-wealth scatter (Normal in, heavy tail out).
- **Controls**: effort slider, regime preset, mechanism toggles (generational /
  opportunity / network), advanced regime dials (premium, redistribution), and a
  seed reset. Each control has an info tooltip explaining its role.

The browser sends a control JSON; the server rebuilds the simulation and streams
frames (via the read-only `SnapshotEmitter`). Change effort or regime and the
system re-runs live. The streamed frame carries only quantities the engine
actually computes, so the view cannot drift from the simulator.
