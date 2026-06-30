"""Configuration objects for the simulation.

``ModelParams`` is the single, immutable source of truth for every numeric
parameter in the model. Components read the parameters they need from it; they
never hold their own copies of shared constants. Default values mirror the
parameter table in ``docs/README.md`` (the v2 model spec).

Keeping all parameters in one frozen dataclass makes runs reproducible and makes
"change the country/policy" a matter of producing a modified copy (see
``simulation.regimes``), never mutating global state.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class ModelParams:
    """All numeric parameters of the poverty-trap model.

    The fields are grouped by the model section in ``docs/README.md`` that
    introduces them. Every field has a documented meaning and a default taken
    from the v2 parameter table. The object is frozen; use :meth:`evolve` to
    derive a modified copy (e.g. for a policy regime).
    """

    # --- Population / integration -------------------------------------------
    n_agents: int = 240
    """Number of agents simulated in parallel (vectorised)."""
    dt: float = 0.01
    """Integration step. First-passage probabilities are invariant to ``dt``;
    smaller is more accurate, larger is faster."""

    # --- Wealth geometry: barriers and continuum bands (section 7.10) -------
    ruin: float = 0.0
    """Absorbing ruin barrier (debt / collapse)."""
    rich_threshold: float = 1.0
    """Upper Micawber threshold ``w*``: reaching it = 'became rich'."""
    poverty_line: float = 0.10
    """``w_p``: below it the poverty premium switches on; crossing it upward =
    'left poverty' (a distinct event from becoming rich)."""
    band_vulnerable: float = 0.25
    """``w_m``: pobreza/vulnerable -> media cutoff (continuum reporting only)."""
    band_acomodado: float = 0.55
    """``w_a``: media -> acomodado cutoff (continuum reporting only)."""
    start_poor: float = 0.05
    """Birth wealth of an agent born poor (near the ruin floor)."""
    start_rich: float = 0.12
    """Birth wealth of an agent born rich (with a cushion)."""
    poor_fraction: float = 0.5
    """Fraction of the population that starts in the poor zone."""

    # --- Neighbourhood drift (Chetty) and poverty premium (Ghatak) ----------
    mu_base_poor: float = -0.015
    """Base drift in the poor zone (negative: a cost-of-living drag toward ruin)."""
    mu_base_rich: float = -0.008
    """Base drift in the rich zone. Still a drag, but smaller than the poor zone's:
    the neighbourhood advantage is *relative* (Chetty), not a guaranteed climb."""
    premium: float = 0.004
    """``pi_0``: extra negative drift while below the poverty line."""

    # --- Diffusion shocks ----------------------------------------------------
    sigma_poor: float = 0.20
    """Shock volatility for poor agents (hits harder)."""
    sigma_rich: float = 0.10
    """Shock volatility for rich agents (cushion absorbs shocks)."""

    # --- Effort: magnitude x efficiency x direction (sections 7.2-7.4) ------
    alpha: float = 0.012
    """Drift bought per unit of effective effort (value creation weight)."""
    eta_min: float = 0.30
    """Floor of effort-to-value efficiency (the scarcity tax floor)."""
    k_w: float = 4.0
    """Sensitivity of efficiency to wealth above the poverty line."""
    k_s: float = 1.5
    """Sensitivity of efficiency to the stressor load."""
    q_min: float = 0.40
    """Floor of effort quality (low-skill effort barely multiplies)."""
    h_half: float = 0.50
    """Skill at which effort quality is halfway to its maximum."""

    # --- Savings / capital returns (compounding engine, section 7.4) --------
    s_max: float = 0.30
    """Maximum share of surplus invested."""
    w_sub: float = 0.10
    """Subsistence wealth below which no saving is possible."""
    k_h: float = 3.0
    """Sensitivity of the savings share to skill."""
    h_bar: float = 0.50
    """Skill reference point for the savings-share logistic."""
    r: float = 0.003
    """Base return on invested capital (low-wealth) per period."""
    r_wealth_slope: float = 0.0
    """Extra return at the rich threshold: r(w) rises from r to r + slope across
    the wealth range (Fagereng 2020). Off by default in the calibrated baseline;
    raise it to study returns-driven divergence."""

    # --- Social network (section 7.6) ---------------------------------------
    beta_network: float = 0.003
    """Drift weight of economic connectedness ``c_i``."""
    gamma_peer: float = 0.010
    """Strength of local peer spillover: value creation drifts toward the mean
    wealth of your network neighbours (knowledge/role-model/demand spillover).
    With homophily this reinforces both rich and poor clusters."""
    network_degree: int = 6
    """Average number of ties per agent in the generated graph."""
    homophily: float = 0.85
    """Probability that a tie connects same-zone agents (segregation)."""
    pool_size: int = 4
    """Group size for collective pooling (cooperatives / family support)."""
    pool_rate: float = 0.02
    """Per-tick chance a poor agent attempts to pool resources with peers to
    push one member across the threshold (set 0 to disable)."""

    # --- Opportunity process (marked Poisson / Pareto, section 7.5) ---------
    lambda0: float = 0.10
    """Base opportunity arrival rate per unit time."""
    g_zone: float = 1.0
    """Gain of arrival rate with zone opportunity density."""
    g_conn: float = 1.5
    """Gain of arrival rate with connectedness."""
    pareto_a: float = 1.5
    """Pareto shape of opportunity payoffs (1 < a <= 2: heavy tail)."""
    x_min: float = 0.02
    """Minimum opportunity payoff (Pareto scale)."""
    kappa: float = 0.03
    """Scale converting a captured payoff into a wealth jump."""
    skill_gate: float = 0.5
    """Skill needed to capture a unit-size opportunity (scales with payoff)."""
    slack_gate: float = 0.20
    """Minimum effective effort (e*eta) required to act on an opportunity."""

    # --- Generational transmission (section 7.8) ----------------------------
    inherit_fraction: float = 0.10
    """``b``: fraction of a parent's final wealth inherited by the child."""
    talent_heritability: float = 0.25
    """``rho``: correlation between parent and child talent."""
    move_probability: float = 0.05
    """Probability a child is born into a different zone than the parent."""
    education_headstart: float = 0.10
    """``delta``: skill head-start for a child whose parent was above the line."""

    # --- Skill dynamics ------------------------------------------------------
    skill_growth_poor: float = 0.0002
    """Per-step skill accrual in the poor zone (sparse resource nodes)."""
    skill_growth_rich: float = 0.0006
    """Per-step skill accrual in the rich zone (dense resource nodes)."""

    # --- Regime / welfare (section 7.9) -------------------------------------
    welfare_floor: float | None = None
    """If set, a reflecting floor that caps how far an agent can fall (welfare).
    ``None`` means ruin is fully absorbing (no safety net)."""
    redistribution: float = 0.0
    """Per-period tax rate on wealth above the rich threshold, redistributed as
    a uniform lift to below-line agents. ``0`` disables redistribution."""
    relative_line_theta: float = 0.0
    """If > 0, the effective poverty line rises with society:
    ``w_p_eff = max(poverty_line, theta * median(wealth))``. ``0`` = absolute line."""

    def evolve(self, **changes: Any) -> "ModelParams":
        """Return a modified copy of these parameters.

        This is the only supported way to "change" parameters, preserving
        immutability and reproducibility. Used by regime presets and tests.

        Example
        -------
        >>> denmark = ModelParams().evolve(premium=0.001, welfare_floor=0.05)
        """
        return replace(self, **changes)

    def validate(self) -> None:
        """Raise ``ValueError`` if any parameter is outside its valid range.

        Called once by the engine at construction so misconfigurations fail
        fast and loudly rather than producing silently wrong results.
        """
        if self.n_agents <= 0:
            raise ValueError("n_agents must be positive")
        if self.dt <= 0:
            raise ValueError("dt must be positive")
        if not (self.ruin < self.poverty_line < self.rich_threshold):
            raise ValueError("require ruin < poverty_line < rich_threshold")
        if not (self.poverty_line <= self.band_vulnerable <= self.band_acomodado
                <= self.rich_threshold):
            raise ValueError("continuum bands must be ordered within [poverty_line, rich_threshold]")
        if not (1.0 < self.pareto_a):
            raise ValueError("pareto_a must be > 1 for a finite mean")
        if not (0.0 <= self.poor_fraction <= 1.0):
            raise ValueError("poor_fraction must be in [0, 1]")
        if not (0.0 <= self.talent_heritability <= 1.0):
            raise ValueError("talent_heritability must be in [0, 1]")
