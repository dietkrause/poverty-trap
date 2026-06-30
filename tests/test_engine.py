"""Engine-level behaviour: the model must reproduce the core qualitative facts."""

from __future__ import annotations

from simulation.builder import build_simulation


def _mobility(effort: float, *, generational: bool = False, ticks: int = 8000) -> dict:
    sim = build_simulation(
        seed=0,
        effort=effort,
        generational=generational,
        with_opportunity=False,
        with_network=False,
    )
    return sim.run(ticks).reports["FirstPassageMonitor"]


def test_rich_escape_more_than_poor() -> None:
    """Born rich should reach the top far more often than born poor."""
    m = _mobility(0.0)
    assert m["rich"]["became_rich"] > m["poor"]["became_rich"]


def test_effort_raises_poor_escape() -> None:
    """More effort must (weakly) raise the poor's chance of becoming rich."""
    low = _mobility(0.0)["poor"]["became_rich"]
    high = _mobility(1.0)["poor"]["became_rich"]
    assert high > low


def test_leaving_poverty_is_easier_than_getting_rich() -> None:
    """The continuum's whole point: leaving poverty != becoming rich."""
    m = _mobility(1.0)
    assert m["poor"]["left_poverty"] >= m["poor"]["became_rich"]


def test_full_model_runs_and_reports() -> None:
    """The full v2 pipeline (opportunity + network + generations) runs end to end."""
    sim = build_simulation(seed=3, effort=0.5, generational=True)
    result = sim.run(3000)
    assert "FirstPassageMonitor" in result.reports
    assert "PopulationMetrics" in result.reports
    assert 0.0 <= result.reports["PopulationMetrics"]["gini"] <= 1.0


def test_peer_influence_pulls_toward_neighbors() -> None:
    """Peer spillover should push an agent toward the mean wealth of its ties."""
    from simulation.core.config import ModelParams
    from simulation.core.context import SimContext
    from simulation.core.state import AgentState
    from simulation.population.network import PeerInfluence
    import numpy as np

    p = ModelParams()
    state, ctx = AgentState.initialize(p, np.random.default_rng(0)), None
    ctx = SimContext(params=p, rng=np.random.default_rng(0))
    state.wealth[:] = 0.3
    state.peer_mean_wealth = np.where(np.arange(state.n) < state.n // 2, 0.9, 0.0)
    d = PeerInfluence().drift(state, ctx)
    # Agents with richer neighbours get a positive pull; poorer neighbours, negative.
    assert d[0] > 0 and d[-1] < 0
