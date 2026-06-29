# ux - live visualization

A web UI to watch the simulation evolve. It is fully isolated from the engine:
the only coupling is the read-only `SnapshotEmitter` observer
(`src/poverty_trap/observe/stream.py`), which streams compact frames; nothing in
`src/` depends on this folder.

```
ux/
  server/   FastAPI WebSocket backend (streams sim frames)
  web/      Vite + React + TypeScript + Tailwind frontend
```

## Run

Backend (from repo root):

```bash
pip install -r ux/server/requirements.txt
uvicorn app:app --app-dir ux/server   # serves ws://localhost:8000/ws
```

Frontend:

```bash
cd ux/web
npm install
npm run dev                            # http://localhost:5173
```

## What you see

- Agent field: dots by zone (poor left / rich right) and wealth (red->yellow->green),
  with the poverty line and Micawber threshold drawn in.
- Wealth bands (the continuum) as a live bar chart, and the live Gini.
- Controls: effort slider, regime preset, mechanism toggles (generational /
  opportunity / network), and a seed reset.

The browser sends a control JSON; the server rebuilds the simulation and streams
frames. Change effort or regime and the system re-runs live.
