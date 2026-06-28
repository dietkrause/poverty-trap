# Model verification: equations to code

This document is an audit. It maps every equation in the model spec
([`../README.md`](../README.md) section 7) to the exact code that implements it,
states the integration scheme, and records the few places where the
implementation deliberately differs from or defers a part of the spec. The goal
is that a reader can confirm the simulation is a faithful, formal representation
of the stated assumptions - not a black box.

Reviewed against commit state of `src/poverty_trap/`. Status: **[exact]** code is
the literal equation; **[approx]** a documented numerical approximation;
**[deferred]** specified in the model but not yet implemented.

## 1. The integration scheme

The per-agent wealth is an Ito drift-diffusion with discrete jumps:

$$dw_i = \mu_i\,dt \;+\; \sigma_i\,dW_i \;+\; dJ_i$$

The engine integrates it with **Euler-Maruyama** plus a jump step, in this order
(`core/engine.py::Simulation.step`):

$$w_i \leftarrow w_i + \underbrace{\mu_i\,\Delta t}_{\text{drift terms}}
+ \underbrace{\sigma_i\sqrt{\Delta t}\,Z}_{\text{noise terms}}
+ \underbrace{\Delta w_i^{\text{opp}}}_{\text{event jumps}},\qquad Z\sim N(0,1)$$

The `sqrt(dt)` scaling of noise versus the `dt` scaling of drift is the reason
`DriftTerm` and `NoiseTerm` are separate interfaces. **[exact]**

## 2. Drift terms (spec 7.4)

Spec:
$$\mu_i = \mu_{\text{base}}(z_i) - \pi_{\text{pov}}(w_i) + \alpha\,e_i\,\eta_i\,q_i + \beta_N\,c_i + r\,w_i\,s_i$$

The engine sums these `DriftTerm` components (each returns a `(n,)` array):

| Spec term | Code | Status |
|-----------|------|--------|
| $\mu_{\text{base}}(z_i)$ | `dynamics/neighborhood.py` -> `where(zone==0, mu_base_poor, mu_base_rich)` | [exact] |
| $-\pi_{\text{pov}}(w_i) = -\pi_0\,\mathbf{1}[w_i<w_p]$ | `dynamics/poverty_premium.py` | [exact] |
| $\alpha\,e_i\,\eta_i\,q_i$ | `dynamics/value_creation.py::ValueCreation` | [exact] |
| $\beta_N\,c_i$ | `population/network.py::NetworkDrift` | [exact] |
| $r\,w_i\,s_i$ | `dynamics/capital_returns.py` (uses $\max(w,0)$) | [exact] |

## 3. Effort efficiency, quality, savings (spec 7.2-7.3)

$$\eta_i = \eta_{\min} + (1-\eta_{\min})\,S\!\big(k_w(w_i-w_p) - k_s\,St_i\big)$$
$$q_i = q_{\min} + (1-q_{\min})\,\frac{h_i}{h_i+h_{1/2}}$$
$$s_i = s_{\max}\,S\!\big(k_h(h_i-\bar h)\big)\,\mathbf{1}[w_i>w_{\text{sub}}]$$

All three are in `dynamics/value_creation.py` (`effort_efficiency`,
`effort_quality`, `savings_share`); `S` is a numerically stable logistic
(`0.5(1+tanh(x/2))`). **[exact]**

## 4. Diffusion noise (spec 7.4)

$$\sigma_i = \sigma_{\text{poor/rich}}(z_i),\qquad \text{increment} = \sigma_i\sqrt{\Delta t}\,Z$$

`dynamics/diffusion.py`. All draws come from `ctx.rng`. **[exact]**

## 5. Opportunity process (spec 7.5)

`events/opportunity.py`. Three independent stages:

- **Arrival**: intensity $\lambda_i = \lambda_0\exp(g_z\,\Omega(z_i)+g_c\,c_i)$,
  realised as the exact probability of at least one Poisson event in a step,
  $\Pr(N\ge1) = 1-e^{-\lambda_i\Delta t}$ (`-np.expm1(-rate*dt)`). **[approx]**
  (one arrival per step max; exact in the small-`dt` limit, valid for any rate).
- **Payoff**: Pareto Type I, $\Pr(X>x)=(x_{\min}/x)^a$. Implemented via NumPy's
  Lomax draw shifted and scaled, `x_min*(1+rng.pareto(a))`, which is exactly
  Pareto Type I with minimum `x_min` and shape `a`. **[exact]**
- **Capture**: $\Delta w^{\text{opp}} = \kappa X\,\mathbf{1}[h_i\ge h_{\min}(X)]\,\mathbf{1}[e_i\eta_i\ge\tau]$
  with $h_{\min}(X)=\,$`skill_gate`$\cdot X$ (rises with payoff). **[exact]**

## 6. Network and connectedness (spec 7.6)

$$c_i = \frac{1}{|\mathcal N(i)|}\sum_{j\in\mathcal N(i)}\mathbf{1}[w_j>w_p]$$

`population/network.py::SocialNetwork` builds a homophilous graph (tie propensity
`homophily` within zone, `1-homophily` across) and computes connectedness as a
single row-normalised matrix-vector product $c = W\,\mathbf{1}[w>w_p]$. **[exact]**

**[deferred]** *Pooling* (a connected group jointly crossing $w^*$ when
$\sum_{j\in C}w_j\ge w^*$) is described in the spec but not implemented. It would
be a new `PopulationProcess`; it is intentionally left as a clearly-scoped
extension rather than an untested addition.

## 7. Talent -> power-law tail (spec 7.7)

No code asserts a Pareto tail; it **emerges**. The update is a Kesten recursion
$w_{t+1}=A_t w_t+B_t$ with the multiplicative factor $A_t = 1 + r\,s_i\,\Delta t$
(from the capital-returns drift) plus heavy-tailed additive jumps $B_t$ (Pareto
opportunities). Talent enters only through $h_i$ and $q_i$ (Gaussian inputs), so
this is the mechanism by which a normal talent distribution yields a power-law
wealth tail. **[exact]** (verifiable empirically by fitting the tail of the
final wealth array).

## 8. Generational transmission (spec 7.8)

`population/lifecycle.py::GenerationalTransmission`:

$$w^0_{\text{child}} = b\,w^{\text{final}}_{\text{parent}} + (1-b)\,w^{\text{base}}(z) + \varepsilon$$
$$T_{\text{child}} = \rho\,T_{\text{parent}} + \sqrt{1-\rho^2}\,\xi,\qquad
h^0 = h_{\text{floor}} + \delta\,\mathbf{1}[\text{parent above line}]$$

with a mobility flip at rate `move_probability`. The IGE is estimated as the OLS
slope of $\log w_{\text{child}}$ on $\log w_{\text{parent}}$ over resolved lives
(`FirstPassageMonitor.ige`). **[exact]** (note: the spec writes $b\,w_{\text{parent}}+\varepsilon$;
the code blends in a zone base term so a lineage does not collapse to zero - a
documented, conservative refinement).

## 9. Regime levers (spec 7.9)

`population/regime.py::RegimePolicy`:
- **Welfare floor**: reflecting barrier $w_i\leftarrow\max(w_i,w_{\text{floor}})$. **[exact]**
- **Redistribution**: tax $t$ on wealth above $w^*$, redistributed equally to
  below-line agents. **[exact]**

**[deferred]** The *relative poverty line* $w_p=\max(w_p^0,\theta\,\mathrm{median}(w))$
is specified but not implemented; `poverty_line` is currently a static parameter
used by the premium, the bands, and $\eta$. Making it dynamic is a scoped change
(thread an effective line through those three call sites) left for a later pass.

## 10. Continuum bands and first-passage (spec 7.10)

`core/bands.py::classify` maps wealth to the five ordered bands via
`searchsorted` on the cutoffs. `FirstPassageMonitor` records the two distinct
events - $\Pr(\text{cross }w_p)$ ("left poverty") and $\Pr(\text{reach }w^*)$
("became rich") - separately by birth class. **[exact]**

## 11. Inequality metric

`observe/metrics.py::gini` uses the sorted, mean-normalised form
$G = \dfrac{\sum_{k}(2k-n-1)\,w_{(k)}}{n\sum_k w_{(k)}}$ on non-negative wealth.
$G=0$ for equality, $\to 1$ for a single holder. **[exact]**

## 12. Determinism

Every stochastic draw flows through the single `numpy.random.Generator` in
`SimContext`. A fixed seed reproduces a run bit-for-bit; enforced by
`tests/test_determinism.py`. **[exact]**

## 13. Summary of deviations from the spec

| Item | Status | Why |
|------|--------|-----|
| Opportunity arrival = one event/step | [approx] | exact $\Pr(N\ge1)$; multi-arrival negligible at small `dt` |
| Generational base-blend term | refinement | prevents lineages collapsing to 0; conservative |
| Pooling (7.6) | [deferred] | scoped extension, not yet implemented |
| Relative poverty line (7.9) | [deferred] | scoped extension, not yet implemented |
| Constant `r` vs data | spec-faithful | spec uses constant `r`; `calibration.md` section 6 proposes `r(w)` |

Everything else is a literal, verifiable implementation of the equations.
