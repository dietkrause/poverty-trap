# Calibration and evidence ledger

This document does three things the project needs to stay honest:

1. **Backs each model assumption** with published, data-strong research, and the
   specific number, proportion, or formula that justifies it.
2. **Flags the gaps** - assumptions for which we have no direct empirical study,
   so we are explicit about what is invented versus measured.
3. **Proposes calibration values and model improvements** drawn from the data,
   so the parameters in `src/simulation/core/config.py` can be moved from
   "illustrative" toward "estimated".

Status legend: **[backed]** a study gives the number/shape directly;
**[partial]** the direction is evidenced but the functional form or magnitude is
ours; **[GAP]** no direct study - an explicit assumption.

The full text of every paper cited here can be downloaded and converted locally
with `papers/fetch_papers.py` + `papers/convert_papers.py` (see `papers/`).

---

## 1. The threshold itself (does a poverty trap exist?)

The whole model rests on a bistable threshold `w*`. The evidence is real but
**contested**, and we record both sides.

| Claim | Evidence (number) | Status |
|-------|-------------------|--------|
| A critical asset threshold exists; below it people slide back, above it they accumulate | **Balboni et al. 2022 (QJE)**: RCT asset transfer reveals an unstable threshold at **~504 USD PPP (k = 2.33 log BDT)**; the asset transition curve crosses the 45-degree line there. | [backed] |
| Classic livestock poverty trap | **Lybbert et al. 2004 (EJ)**: low equilibrium ~**1 cow**, high **40-75**, unstable threshold **10-15 cattle**. **Santos & Barrett 2018 (NBER)**: threshold ~**15 cattle**, shock-dependent. | [backed] |
| A "big push" above the threshold causes lasting escape | **Banerjee et al. 2015 (Science)**, 6-country graduation RCT, N=10,495: consumption **+0.12 SD (~+5%)**, assets **+0.26 SD**, income **+0.38 SD**, persisting to endline 2. | [backed] |
| ...but traps are NOT universal | **Kraay & McKenzie 2014 (JEP)**: standard traps are "rare and largely limited to remote or disadvantaged areas"; concave (no-trap) accumulation is the common case. | [GAP / caveat] |

**Implication.** Keep `w*` but add a **no-trap regime** (concave accumulation,
single equilibrium) as a robustness setting, per Kraay & McKenzie. Do not claim
the trap is universal.

---

## 2. Neighbourhood base drift (`mu_base_poor`, `mu_base_rich`, skill growth, `move_probability`)

| Model piece | Evidence (number) | Status |
|-------------|-------------------|--------|
| Where you grow up changes outcomes, per year of exposure | **Chetty & Hendren 2018 I (QJE)**: outcomes converge to the destination at **~4% per year of childhood exposure**. | [backed] |
| Magnitude of a better county | **Chetty & Hendren 2018 II**: for low-income children, **1 year in a 1-SD-better county -> +0.5% adult income**. | [backed] |
| Place effects are causal and large | **Opportunity Atlas (Chetty et al. 2018)**: ~**60%** of tract variation is causal; a 25th->75th percentile tract move at birth -> **+$387k** lifetime earnings. | [backed] |
| Relocation is gated by frictions (calibrates `move_probability`) | **Bergman et al. 2024 (AER)**: with search support, high-opportunity moves rose **15.4% -> 53.2% (+37.8 pp)**. | [backed] |

**Suggested values.** The poor/rich base-drift gap should encode roughly the
~4%/year exposure convergence; `move_probability` is small without support and
much larger with it (model a "support" lever in the regime).

---

## 3. Poverty premium (`premium` / `pi_0`)

| Model piece | Evidence (number) | Status |
|-------------|-------------------|--------|
| Being poor costs more for the same goods | **Davies, Finney & Hartfree 2016 (Bristol PFRC)**: average premium **GBP 490/household/year**. | [backed] |
| Incidence and tail | **Davies & Evans 2023 (PFRC)**: **98%** of low-income households incur >=1 premium; mean **3.5** premiums; average **GBP 217/year** (method-equivalent **GBP 499**). | [backed] |

**Suggested value.** As a fraction of a low UK income (~GBP 15k), the premium is
roughly **2-3% of income per year** - express `pi_0` as that order of magnitude
rather than an abstract constant. **Ghatak 2015** supplies the theory; these give
the size.

---

## 4. Effort efficiency `eta` (the scarcity tax) - the most cautious term

| Model piece | Evidence (number) | Status |
|-------------|-------------------|--------|
| Scarcity reduces cognitive bandwidth | **Mani et al. 2013 (Science)**: scarcity effect ~**13 IQ points (~0.88-0.94 SD)**; field effect ~3/4 as large. | [partial] |
| ...but the cognition channel is not always robust | **Carvalho, Meier & Wang 2016 (AER)**: before payday, present-bias rises (**+$10.60** to sooner reward) but **no measurable cognitive (Stroop) effect (~0.00)**. | [GAP / caveat] |
| Poverty -> stress -> short-sighted behaviour feedback | **Haushofer & Fehr 2014 (Science)**: review of the stress/scarcity feedback loop. | [partial] |

**Implication.** The *direction* of `eta` (poverty degrades effective effort) is
evidenced, but the **logistic form `eta(w, St)` and the floor `eta_min=0.3` are
ours [GAP]**, and Carvalho cautions that the mechanism may be liquidity /
discounting rather than raw cognition. Frame `eta` as "bandwidth + liquidity",
keep the floor conservative, and do not over-claim a precise cognitive tax.

---

## 5. Effort quality `q` and savings `s`

| Model piece | Evidence (number) | Status |
|-------------|-------------------|--------|
| Skill turns effort into earnings (calibrates `q`) | **Psacharopoulos & Patrinos 2018 (World Bank)**: 1,120 estimates / 139 countries; private return ~**9% per year of schooling**; Mincer form `ln Y = a + rho_s * s + ...`. | [backed] |
| Ability vs schooling bias | **Card 1999**: IV returns often **20-40% above OLS**; twin studies suggest ability bias ~**10%**. | [backed] |
| Mincer functional form | **Heckman, Lochner & Todd 2006 (NBER)**: the earnings-function form and its caveats. | [backed] |
| Rich save a larger share (calibrates `s`) | **Dynan, Skinner & Zeldes 2004 (JPE)**: lifetime saving rate rises from **-2.7% (bottom decile) to 16.1% (top decile)**. | [backed] |

**Suggested values.** Set `q` so an extra unit of skill maps to ~9%/year
earnings leverage; set `s` to ~0 below the line (the poor dissave) rising toward
~0.16 at the top - which is close to the current `s_max=0.30` upper shape but the
*level* should be lower for the poor.

---

## 6. Capital returns `r * w * s` - data says make `r` rise with wealth

This is the compounding engine, and the data is unusually strong - and it tells
us our **constant `r` is wrong**.

| Model piece | Evidence (number) | Status |
|-------------|-------------------|--------|
| Returns to wealth INCREASE with wealth | **Fagereng et al. 2020 (Econometrica)**: median return **0.7% at P10 -> 2.6% at P90 (+180 bps)**; persistent individual fixed effects (SD **2.8 pp**, P90-P10 **6.4 pp**); intergenerational return slope **0.085-0.10**. | [backed] |
| Steeper at the very top | **Bach, Calvet & Sodini 2020 (AER)**: expected excess return **2.2% (bottom decile) -> 7.9% (top 0.01%)**; top vs median **+3.6 pp/year**. | [backed] |

**Model improvement (do this).** Replace the constant `r` with a
**wealth-dependent** `r(w)` rising from ~0.7% to ~2.6% across the wealth
distribution (Fagereng), optionally steeper at the top (Bach). This grounds the
divergence mechanism in measured data instead of assumption.

---

## 7. Power-law wealth from multiplicative dynamics (`pareto_a`, the talent->luck story)

| Model piece | Evidence (number) | Status |
|-------------|-------------------|--------|
| Random multiplicative returns produce a Pareto tail | **Benhabib & Bisin 2018 (JEL)** (and Benhabib, Bisin & Zhu 2011): Kesten condition **E[A^mu] = 1** sets the tail exponent. | [backed] |
| Empirical wealth tail exponent | **Vermeulen 2018 (RIW)**: Pareto index ~**1.4-1.7** (US **1.52**, UK 1.74, DE 1.39, FR 1.62). **Benhabib & Bisin 2018**: Forbes 400 ~**1.49**. | [backed] |
| Tail dynamics are slow | **Gabaix, Lasry, Lions & Moll 2016 (Econometrica)**: SCF `eta=0.65 -> zeta~1.54`; transition half-life **>=26 years**, tail-moment half-life **~79.5 years**. | [backed] |
| Talent normal, outcome power-law, top is luck | **Pluchino et al. 2018**: the agent-based precedent. | [backed] |

**Validation.** Our `pareto_a = 1.5` is **right on the empirical mark (~1.5)** -
keep it. The slow-transition result independently supports the multi-generational
framing.

---

## 8. Social capital and opportunity concentration (`beta_network`, `g_conn`, `homophily`)

| Model piece | Evidence (number) | Status |
|-------------|-------------------|--------|
| Connectedness predicts mobility (calibrates `beta_network`) | **Chetty, Jackson et al. 2022 (Nature) I**: raising low-SES children's economic connectedness to the high-SES average -> **+20% adult income**; county slope ~**16.4 income-rank points per 1.0 EC**. | [backed] |
| The disconnection is exposure + bias (calibrates `homophily`) | **Social Capital II**: SES disconnection ~**54% exposure** vs **46% friending bias**. | [backed] |
| Opportunity/access is highly concentrated | **Bell et al. 2019 (QJE)**: top-1% children **10x** as likely to become inventors; equalising exposure would **quadruple** inventors. | [backed] |
| Peer spillover / social multiplier | **Glaeser, Sacerdote & Scheinkman**: local peer effects amplify behaviour; neighbours' outcomes feed back into one's own. Calibrates the `gamma_peer` term (drift toward neighbours' mean wealth). | [partial] |
| Preferential attachment generates the power law | **Barabasi & Albert 1999 (Science)**. | [backed] |

**Suggested values.** `beta_network` should reproduce roughly a +20% income lift
from full connectedness; the homophily split (~54/46) calibrates how much of low
connectedness is structural exposure versus tie-formation bias.

---

## 9. Generational transmission (`inherit_fraction b`, `talent_heritability rho`)

Calibrate `b` and `rho` so the simulated intergenerational elasticity (IGE)
lands on real country values.

| Country | IGE (Corak 2013) | Father-son (Jantti 2006) |
|---------|------------------|--------------------------|
| Denmark | 0.15 | 0.071 |
| Norway | 0.17 | 0.155 |
| Finland | 0.18 | 0.173 |
| Sweden | 0.27 | 0.258 |
| Germany | 0.32 | - |
| France | 0.41 | - |
| UK / Italy | 0.50 | 0.306 (UK) |
| US | 0.47 | 0.517 |

- **Great Gatsby slope** (Corak): ~**+0.03 IGE per Gini point** (~+0.30 per 10).
- **Chetty et al. 2014**: US rank-rank slope **0.341** (+10 parent percentiles ->
  +3.41 child percentiles).
- **Mazumder 2015**: US family-income IGE likely **>0.6** (an upper bound; the
  tax-data 0.34 may be downward-biased).

**Suggested values.** Target a simulated IGE of ~0.15 for a Nordic regime and
~0.5 for a US/UK regime; tune `b` and `rho` to hit it. Our defaults
(`b=0.4, rho=0.4`) sit mid-range and should be regime-specific.

---

## 10. Literature gaps (assumptions we are making without a direct study)

These are the honest weak points - documented so reviewers can challenge them:

1. **The threshold's universality** (section 1). Kraay & McKenzie show traps are
   not everywhere. We assume one by default. -> add a no-trap regime.
2. **The functional form of `eta(w, St)`** (section 4). The logistic shape, the
   `eta_min` floor, and the sensitivities `k_w, k_s` are invented; and the
   cognition channel itself is contested (Carvalho).
3. **The opportunity capture gate** (`h_min(X)`, `slack_gate`): no direct study
   pins the skill-threshold-by-payoff-size relationship.
4. **Constant returns `r`**: contradicted by Fagereng/Bach (returns rise with
   wealth). This is a known defect to fix (section 6).
5. **Talent ~ Normal** exactly: a convention. (Low risk: the Kesten result makes
   the wealth tail Pareto regardless of the talent distribution's shape.)
6. **The stressor process `St ~ Exp`**: arbitrary; uncalibrated.
7. **The network->opportunity-rate elasticity `g_conn`**: Social Capital gives
   connectedness->income, not the arrival-rate elasticity directly.
8. **The effort-magnitude distribution** (Beta): no empirical basis for its shape.

---

## 11. Concrete, data-driven changes to make

In priority order, each backed by a paper above:

1. **`r` -> `r(w)` rising 0.7% to 2.6%+** across wealth (Fagereng 2020; Bach 2020).
2. **`sigma_poor / sigma_rich` ~ 1.6** (income-volatility CV ~55% below vs ~34%
   above the line; US Financial Diaries / JPMorgan Chase Institute), versus the
   current 2.0.
3. **Keep `pareto_a ~ 1.5`** (Vermeulen 2018; Benhabib & Bisin 2018) - already
   correct.

---

## Calibration record: v2 realistic defaults

An earlier (illustrative) parameterisation put the model in an **unrealistic
regime**: a majority of *all* lives reached the "rich" band (~70%), born-rich
reached it ~100% of the time, ~45% of the living population sat in the *acomodado*
band, and the simulated intergenerational elasticity was far above 1. The cause
was structural, not a single bad number: a **bounded drift-diffusion with net
upward drift** (positive base drift in the rich zone, strong value-creation and
capital-compounding terms, and a large opportunity-capture scale `kappa`) carries
almost every agent up to the `w*` ceiling. In such a process the top is not a
tail - it is where ordinary drift takes you.

The defaults were re-calibrated so the wealth process is **near-mean-reverting
with a heavy-tailed upside**, making `w*` a rare destination:

| Parameter | Old | Calibrated | Rationale |
|-----------|-----|------------|-----------|
| `mu_base_poor`, `mu_base_rich` | -0.010, +0.020 | -0.015, -0.008 | a cost-of-living drag for both zones; the rich zone's is *smaller* (a relative, not absolute, edge - Chetty) |
| `alpha` (value-creation) | 0.060 | 0.012 | effort still helps, but does not deterministically lift everyone |
| `kappa` (opportunity scale) | 1.0 | 0.03 | opportunities are heavy-tailed but only the extreme tail reaches the top |
| `r`, `r_wealth_slope` | 0.007, 0.020 | 0.003, 0.0 | capital still compounds but is not a guaranteed escalator |
| `beta_network`, `gamma_peer` | 0.010, 0.020 | 0.003, 0.010 | social lift is modest, not dominant |
| starts (poor, rich) | 0.15, 0.55 | 0.05, 0.12 | nobody is born pre-loaded near `w*` (gambler's-ruin: a start at 0.55 hits 1.0 ~55% of the time) |
| bands `w_p, w_m, w_a` | 0.20, 0.45, 0.70 | 0.10, 0.25, 0.55 | rescaled so the bulk spreads across the lower bands |
| `inherit_fraction` `b`, `talent_heritability` `rho` | 0.40, 0.40 | 0.10, 0.25 | brings the IGE into the Great Gatsby range [0.3, 0.6] |

**Resulting regime (4 seeds, effort 0.5; see `experiments/calibration/`):**
P(rich \| born poor) ~5%, P(rich \| population) ~6%, IGE ~0.5, durable escape
(`time_above_line`) ~27% (>> P(rich)), and a bottom/middle-heavy distribution
(~80% below the *acomodado* band). All six calibration checks pass.

**Known limitation - the welfare floor.** A reflecting `welfare_floor` removes the
absorbing ruin barrier, which in this calibration is too powerful: with no
downward exit, almost every floored life eventually reaches `w*` over a long
lifespan (~80% become rich for any floor > 0). The `protective` preset therefore
expresses protection through a *smaller cost-of-living drag*, lower premium,
education head-start, and redistribution rather than a hard floor. A **soft floor**
(extra positive drift near the bottom instead of a reflecting barrier) is the
right future fix; the hard floor remains available for programmatic study but is
not used in any preset and is not exposed in the UI.

These remain **illustrative** targets, not a fit to any specific country. Re-run
`experiments/calibration/run.py` after any parameter change to confirm the model
is still in a realistic regime.
4. **`premium` as ~2-3% of income/year** (Davies 2016; Davies & Evans 2023).
5. **Regime-specific `b, rho` targeting IGE 0.15 (Nordic) to 0.5 (US/UK)** (Corak
   2013; Jantti 2006; Chetty 2014).
6. **`q` tied to ~9%/year returns to schooling** (Psacharopoulos 2018).
7. **`s` near 0 below the line, rising with wealth** (Dynan 2004).
8. **Add a no-trap (concave) regime** for honesty (Kraay & McKenzie 2014).

---

## 12. Sources (with the key number and a free PDF)

All links are free / open versions; run the fetch + convert scripts in `papers/`
to get the full text locally.

- Balboni, Bandiera, Burgess, Ghatak & Heil (2022), *Why Do People Stay Poor?*,
  QJE 137(2). Threshold ~504 USD PPP. NBER w29340.
- Kraay & McKenzie (2014), *Do Poverty Traps Exist?*, JEP 28(3). Skeptic case.
- Banerjee et al. (2015), *A Multifaceted Program... Six Countries*, Science 348.
  Graduation RCT, N=10,495.
- Lybbert, Barrett, Desta & Coppock (2004), *Stochastic Wealth Dynamics*, EJ 114.
- Santos & Barrett (2018), *Heterogeneous Wealth Dynamics*, NBER chapter.
- Chetty & Hendren (2018), *Neighborhoods I & II*, QJE 133. ~4%/year exposure.
- Chetty et al. (2018), *The Opportunity Atlas*, NBER w25147. 60% causal.
- Bergman et al. (2024), *Creating Moves to Opportunity*, AER 114. +37.8 pp.
- Davies, Finney & Hartfree (2016) and Davies & Evans (2023), *Poverty Premium*,
  Bristol PFRC. ~GBP 490 / 217 per year.
- Mani, Mullainathan, Shafir & Zhao (2013), *Poverty Impedes Cognitive Function*,
  Science 341. ~13 IQ points.
- Carvalho, Meier & Wang (2016), *Decision-Making at Payday*, AER 106.
- Haushofer & Fehr (2014), *On the Psychology of Poverty*, Science 344.
- Psacharopoulos & Patrinos (2018), *Returns to Investment in Education*, World
  Bank WPS 8402. ~9%/year.
- Card (1999), *The Causal Effect of Education on Earnings*.
- Heckman, Lochner & Todd (2006), *Earnings Functions*, NBER w11544.
- Dynan, Skinner & Zeldes (2004), *Do the Rich Save More?*, JPE 112. -2.7% to
  16.1% saving rate. NBER w7906.
- Fagereng, Guiso, Malacrino & Pistaferri (2020), *Returns to Wealth*,
  Econometrica 88. +180 bps P10->P90. NBER w22822.
- Bach, Calvet & Sodini (2020), *Rich Pickings?*, AER 110. 2.2% -> 7.9%.
- Benhabib, Bisin & Zhu (2011), *Distribution of Wealth*, Econometrica 79;
  Benhabib & Bisin (2018), *Skewed Wealth Distributions*, JEL 56. Kesten tail.
- Gabaix, Lasry, Lions & Moll (2016), *The Dynamics of Inequality*, Econometrica
  84. zeta ~ 1.54; slow transitions.
- Vermeulen (2018), *How Fat is the Top Tail?*, RIW 64. Pareto index ~1.4-1.7.
- Chetty, Jackson et al. (2022), *Social Capital I & II*, Nature 608. +20% income;
  54/46 exposure/bias. NBER w30313, w30314.
- Bell, Chetty, Jaravel, Petkova & Van Reenen (2019), *Who Becomes an Inventor?*,
  QJE 134. 10x.
- Corak (2013), *Income Inequality... Mobility*, JEP 27. IGE table; Great Gatsby.
- Jantti et al. (2006), *American Exceptionalism*, IZA dp1938. Father-son IGE.
- Mazumder (2015), *Estimating the IGE*, Chicago Fed WP. US IGE > 0.6.
- Chetty, Hendren, Kline & Saez (2014), *Land of Opportunity?*, QJE 129.
  Rank-rank 0.341. NBER w19843.
- Barabasi & Albert (1999), *Emergence of Scaling*, Science 286. arXiv.
- Pluchino, Biondo & Rapisarda (2018), *Talent vs Luck*, ACS 21. arXiv.
- Ghatak (2015), *Theories of Poverty Traps*, WBER 29. Poverty premium theory.
