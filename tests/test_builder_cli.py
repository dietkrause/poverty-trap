"""Builder, regimes, and CLI: composition toggles and end-to-end entry points."""

from __future__ import annotations

from poverty_trap.builder import build_simulation
from poverty_trap.cli import main
from poverty_trap.regimes.presets import PRESETS, get_preset


def test_toggles_change_component_count() -> None:
    full = build_simulation(seed=0, effort=0.3)
    v1 = build_simulation(seed=0, effort=0.3, with_opportunity=False, with_network=False)
    assert len(full.event_processes) == 1 and len(v1.event_processes) == 0
    assert len(full.drift_terms) > len(v1.drift_terms)            # peer + network drift added
    assert len(full.population_processes) > len(v1.population_processes)


def test_presets_resolve_and_unknown_raises() -> None:
    for name in PRESETS:
        get_preset(name).validate()
    try:
        get_preset("nope")
        assert False, "expected KeyError"
    except KeyError:
        pass


def test_cli_run_smoke(capsys) -> None:
    rc = main(["run", "--effort", "0.5", "--ticks", "300", "--no-opportunity", "--no-network"])
    assert rc == 0
    assert "mobility" in capsys.readouterr().out
