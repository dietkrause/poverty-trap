# Poverty Trap v2 - Comment analysis and extension plan

Source: `comments.json` (live pull from the viral reel `DaBgEPZSJXy`, caption "El pobre
es pobre porque quiere? Definitivamente no..."). 281 comments total, 190 with text read
and analyzed, 567 reshares. This doc turns that feedback into a concrete plan to evolve
the model toward reality and into a series of follow-up reels.

---

## 1. What the comments actually said

Sentiment was overwhelmingly positive and, more importantly, **substantive**. I ignored
the pure-noise / bad-faith ones (a handful of political insults and "ML izquierdista",
"resultado de escritorio", etc.) because they carry no model signal. The constructive
feedback clusters into clear, repeated themes, ranked by how often they came up:

| # | Theme (what people asked for) | Representative voices | Maps to |
|---|-------------------------------|------------------------|---------|
| 1 | **Binary is too crude: add a middle class / continuum.** "Escapar la pobreza" is NOT the same as "hacerse rico/millonario". | mangelesriq, erickhenriquezr, ivanosokohler, ricardo.quappe, eso._.po, mati_11.11, nicolas.addamo, charlescardenas | New: multi-band continuum |
| 2 | **Generational transmission.** Inheritance of wealth, start point, financial education; "6-10 generations to escape" (OECD). | sierracisterna, diego.a.munoz.108, danibrauchi, tio_bodoni, zan.grey, juandenobo | Your idea #2 |
| 3 | **Effort's conversion to value is itself constrained** by circumstances (sick kids, inherited debt, dysfunction, scarcity). | dres.dev, agv_1989, davo.amv, henochsnow, n.arratia.r, cangunejo | Your idea #1 |
| 4 | **Effort is direction/strategy, not just hours.** Smart effort, vision, allocation beats raw quantity. | alfprieto7, ed.morales, javierdonosovi, juandenobo, rodrigoxile, sion.andrieux, nacho_rodriguez | Refines your "effort" |
| 5 | **Collaboration / social networks / collective action / social capital.** | fabio.bozzolo, ravc2511, josebus1785, ppizarroj, karlosvc1212, scarlet_leinth | Your idea #4 |
| 6 | **Access to opportunity, unequally distributed; country matters.** | carolinalina2030, luisg.rodriguez, trovadicto85, soulofwaves, comun_people, la.rous_fm | Your idea #6 |
| 7 | **Talent / cognitive ability / skill as a variable.** | robertoaraya1, moglyman ("las capacidades cognitivas son aleatorias?"), ed.morales, cangunejo | Your idea #5 |
| 8 | **Country / macro regime / welfare state (education, health, housing, redistribution).** | mastertebo, luigyalfred, scarlet_leinth, ppizarroj, rodrigoruizmardones, nf.toledo | Your idea #3 |
| 9 | **Luck as an explicit force.** | christiancagg, ipromise1, panchaarrieta, curadoracurada, manuant_95 | New: explicit luck |
| 10 | **Wealth concentration / the line moves / system needs inequality.** | rodrigoruizmardones, soulofwaves (Adam Smith), henochsnow, bernabe_torres | New: relative line / concentration |
| 11 | **Validate / calibrate the model to real data.** | cristhianavila6, danibrauchi, leon_engymeer, eltiovito | New: calibration |
| 12 | **Open-source the repo.** Dozens asked for the code/paper. | angelortizinnovations and ~30 others | Distribution, not model |

Two clarity issues to fix in the narrative (people got confused):
- "If at 0% effort 13% still escape, did they escape by luck?" -> **Yes.** The baseline
  is luck-driven; make that explicit (ties to theme 9).
- People read "escape = become rich". Decoupling "leave poverty" from "become rich"
  (theme 1) removes most of the confusion.

---

## 2. Validating your proposed approach (idea by idea)

Your instinct is good and, encouragingly, it lines up with both the comments and the
academic literature. Verdict on each, with how to make it rigorous:

### 2.1 A variable for "effort -> value" conversion efficiency  (VALID, high value)
Model effort as having an **efficiency multiplier** eta in [0,1] that is degraded by
adverse conditions. This is exactly the "scarcity tax": being poor consumes cognitive
bandwidth, so the same effort yields less (Mani, Mullainathan, Shafir, Zhao, Science
2013, "Poverty Impedes Cognitive Function"). Implement as a factor on the value-creation
term, lower when wealth is below the poverty line or when stressors are active.

### 2.2 Generational wealth and poverty transmission  (VALID, high value)
Standard and well-measured. Calibrate to the **intergenerational elasticity (IGE)** and
the **Great Gatsby Curve** (Corak 2013), and to the OECD "generations to reach mean
income" (OECD 2018, *A Broken Social Elevator?* - the "6 generations" stat a commenter
cited). Child inherits a fraction of wealth, a correlated talent draw, the zone, and the
network.

### 2.3 Hyperparameters for country / family situation  (VALID)
Make a **regime config** Theta that rescales the premium, the drift spread, the
opportunity rate and inequality, a welfare floor, public-education uplift, and
redistribution. "Switch country" = swap Theta and re-run the SAME agents. This also
answers the large welfare-state comment cluster (theme 8).

### 2.4 Social network / collaboration  (VALID)
Put agents on a graph. **Economic connectedness** predicts mobility (Chetty, Jackson et
al., Nature 2022, "Social capital I & II"); weak ties open opportunities (Granovetter
1973). Connections raise your opportunity arrival rate, help absorb shocks, and let
agents **pool to cross the threshold collectively**.

### 2.5 Talent/skill ~ Normal  (VALID assumption, with a twist)
Yes, model the talent endowment as Normal. But the **key, counter-intuitive result you
should feature**: even with normally distributed talent, outcomes become a power law and
the most successful are rarely the most talented, because dynamics are multiplicative and
opportunity/luck is heavy-tailed. This is exactly the Pluchino, Biondo, Rapisarda (2018)
"Talent vs Luck" ABM. Great reel.

### 2.6 Opportunity as a power-law abstraction  (VALID, the most sophisticated)
Strong intuition and it is supported. Define an **opportunity** precisely (section 3.3):
an arrival process whose payoffs are Pareto (power-law), with arrival rate correlated to
environment and network. The "rich get richer" access is **preferential attachment**
(Barabasi-Albert 1999) and the **Matthew effect** (Merton 1968). This is the cleanest way
to encode "a few have access to many opportunities, most to very few."

**Bottom line:** all six are reasonable and defensible. Add three the comments demand that
you did not list: the **continuum/middle-class** (theme 1, the single most common
critique), the **explicit luck term** (theme 9), and **calibration to real data**
(theme 11).

---

## 3. A unified v2 model (so it stays one coherent story, not a laundry list)

Keep the v1 spine (a wealth random walk with drift between a ruin floor and an escape
threshold). Extend the **drift** and add three processes: opportunity, network, and
generations, all tunable by a regime config.

### 3.1 Agent state
Each agent i carries:
- `w_i` wealth (assets),
- `T_i` talent endowment, drawn `T_i ~ Normal(0, 1)` (your idea #5),
- `h_i` human capital / skill (accumulates from T_i, education, effort),
- `z_i` zone / location (sets base drift, shock size, opportunity density - Chetty),
- `e_i` effort magnitude in [0,1] (now heterogeneous across agents, not one global slider),
- `c_i` connectedness (social capital from the network),
- lineage info (parent's final wealth, generation g).

### 3.2 The drift, rebuilt
Replace the single `mu = mu_base - premium + alpha*e` with:

$$\mu_i \;=\; \underbrace{\mu_{\text{base}}(z_i,\,\Theta)}_{\text{neighborhood (Chetty)}}
\;-\; \underbrace{\pi_{\text{pov}}(w_i,\,\Theta)}_{\text{poverty premium (Ghatak)}}
\;+\; \underbrace{\alpha\, e_i\, \eta_i\, q_i}_{\text{value creation}}
\;+\; \underbrace{\beta_N\, c_i}_{\text{social capital}}
\;+\; \underbrace{r\, w_i\, s_i}_{\text{returns on capital}}$$

where:
- `eta_i` in [0,1] = **effort-to-value efficiency** (your idea #1). Degraded by scarcity
  and stressors: `eta_i = g(stressors_i, w_i)`, lower below the poverty line (Mani 2013).
- `q_i` = **effort quality / direction** (comments theme 4). A function of talent and
  skill `q_i = h(T_i, h_i)`; "smart effort" multiplies, "blind effort" does not.
- `c_i` = connectedness; `beta_N` its weight (network boost).
- `r * w_i * s_i` = **returns on accumulated capital** with savings/allocation share
  `s_i` (comments theme 11: invest vs save vs consume). This term is why the rich
  compound; it is near-zero for the poor who cannot save. Compounding = the engine of
  divergence.

Effort therefore enters as **magnitude x efficiency x direction** (`e * eta * q`), which
directly answers "two people with the same effort get different results" and "effort is
constrained by circumstances."

### 3.3 Opportunity as a precise object (your idea #6)
An **opportunity** is a discrete event, not a smooth drift. For agent i:
- **Arrival**: a Poisson process with rate `lambda_i = lambda_0 * f(z_i, c_i, Theta)` -
  more in good zones and well-connected agents (preferential attachment).
- **Payoff**: drawn from a **Pareto (power-law)** distribution, `X ~ Pareto(x_min, a)` -
  a few opportunities are huge, most are tiny (your power-law intuition).
- **Conversion**: you only capture `X` if you have the capacity to act -
  `capture = X * 1[h_i >= h_min] * (e_i eta_i)` - skill + effort + slack to seize it.

So opportunity = **arrival (environment/network) x payoff (power law) x conversion
(talent/effort/slack)**. This makes "access to opportunity" a first-class, defensible
variable and reproduces the Matthew effect. Even with Normal talent, the Pareto payoffs
make wealth heavy-tailed (the Talent-vs-Luck result).

### 3.4 Network / collaboration (your idea #4)
Agents sit on a graph with homophily (poor tend to connect to poor - Schelling-style),
so segregation emerges. Edges do three things: raise `lambda_i` (opportunity access),
raise `eta_i` (a friend helps absorb a shock, fewer ruinous events), and enable
**pooling**: k connected agents can combine wealth to jointly cross the threshold once,
modeling cooperatives / juntas / family support (comments theme 5). Connectedness `c_i`
is the share of your ties that are above the line (Chetty's "economic connectedness").

### 3.5 Generational transmission (your idea #2)
At death, the child starts with:
- wealth `w_child = b * w_parent + epsilon` (inheritance fraction b),
- talent `T_child = rho * T_parent + sqrt(1-rho^2) * noise` (heritability rho),
- the **same zone and network** unless a (rare) mobility event fires,
- a head start in `h` if the parent was above the line (financial/education transmission).

Calibrate `b, rho` so the simulated IGE matches the Great Gatsby Curve and the OECD
"generations to mean income." This lets you show the trap **persisting across
generations**, and answer "how many generations to escape?" with a number.

### 3.6 Regime hyperparameters (your idea #3)
A config `Theta` you swap to "change country/policy":
- premium scale (how punishing poverty is),
- opportunity rate `lambda_0` and inequality exponent `a` (how concentrated access is),
- **welfare floor** (caps the downside of shocks - fewer ruins),
- **public education** (raises `h` and `eta` for the poor),
- **redistribution** (taxes high `w`, lifts the floor and the poor's `mu_base`),
- threshold height and a **relative poverty line** that rises with median wealth.

"Run the SAME 100 people under Chile vs Denmark vs USA" is a killer reel and answers the
entire policy/structural comment cluster honestly (it does not take a political side; it
shows the mechanism).

### 3.7 The continuum (the #1 requested fix)
Drop pure binary. Define wealth bands (pobreza, vulnerable, clase media, acomodado, rico)
and report **two different probabilities**: P(cross the poverty line) and P(reach the
rich attractor). "Salir de la pobreza" and "hacerse rico" become distinct events - which
is exactly the distinction dozens of commenters demanded.

---

## 4. Roadmap: turn this into a series (ordered by impact / effort)

Each phase is a self-contained follow-up reel. Order chosen so the earliest ones are the
highest-demand and lowest-effort.

**Phase 0 - Open-source the repo (do this now).** Dozens asked. Publish v1 + a clean
README, link in bio. Free reach, credibility, and it seeds every later video.

**Phase 1 - The continuum + "escape poverty != become rich".** Answers the most common
critique and the "did they escape by luck?" confusion. Low effort, high payoff. Reel:
"Ustedes tenian razon: no es binario." Show P(leave poverty) vs P(get rich) separately.

**Phase 2 - Generational transmission.** Watch the trap survive across generations;
calibrate to "6 generations" (OECD). Very shareable, emotionally strong.

**Phase 3 - Effort = magnitude x efficiency x direction.** The scarcity tax (Mani 2013)
and smart-vs-blind effort. Answers "effort is constrained" and "smart effort beats hours."

**Phase 4 - Talent (normal) vs Luck/Opportunity (power law).** The Pluchino result: the
most successful are rarely the most talented. Biggest "wow" reel of the series.

**Phase 5 - Social capital / networks.** "Moving to a connected neighborhood opens doors"
(Chetty social capital). Pooling/cooperatives cross the threshold together.

**Phase 6 - Country / policy regimes.** Same agents, different Theta: welfare floor,
public education, redistribution. The honest, non-partisan "what actually moves the
curve" video.

**Cross-cutting - Calibration & validation.** Tune to IGE / Great Gatsby / OECD; publish a
sensitivity analysis. This is your shield against "resultado de escritorio" and a
credibility flex.

---

## 5. References to anchor v2 (add to your bibliography)

- Mani, Mullainathan, Shafir, Zhao (2013). Poverty Impedes Cognitive Function. *Science*
  341(6149), 976-980. -> effort efficiency / scarcity tax (eta).
- Corak (2013). Income Inequality, Equality of Opportunity, and Intergenerational
  Mobility. *J. Economic Perspectives* 27(3). -> Great Gatsby Curve (generational).
- OECD (2018). *A Broken Social Elevator? How to Promote Social Mobility.* -> generations
  to mean income (the "6 generations" figure).
- Chetty, Jackson, et al. (2022). Social capital I & II. *Nature* 608. -> networks /
  economic connectedness.
- Granovetter (1973). The Strength of Weak Ties. *AJS* 78(6). -> opportunity via ties.
- Barabasi & Albert (1999). Emergence of Scaling in Random Networks. *Science* 286. ->
  preferential attachment / power-law access.
- Merton (1968). The Matthew Effect in Science. *Science* 159. -> cumulative advantage.
- Pluchino, Biondo, Rapisarda (2018). Talent vs Luck: the role of randomness in success
  and failure. *Advances in Complex Systems* 21. -> talent normal, outcomes power-law.
- Bowles, Durlauf, Hoff, eds. (2006). *Poverty Traps.* Princeton. -> membership/structural
  traps.
- (Carried from v1) Chetty et al. 2014; Barrett & Carter 2006; Ghatak 2015; Azariadis &
  Stachurski 2005.

---

## 6. One-line answers you can paste in comments

- "Como calculas el umbral?" -> es el equilibrio inestable del sistema (donde tu cambio
  esperado pasa de negativo a positivo); ver el reel de seguimiento.
- "Y la clase media?" -> tenian razon, en v2 separo 'salir de la pobreza' de 'hacerse
  rico': son dos probabilidades distintas.
- "Y el esfuerzo si tenes hijos enfermos / mil problemas?" -> v2 agrega una eficiencia del
  esfuerzo que la pobreza degrada (el 'impuesto cognitivo' de la escasez, Mani 2013).
- "Y las oportunidades / la suerte?" -> v2 las modela como un proceso de llegada con pagos
  de cola pesada (power law); con talento normal, el resultado igual se vuelve power law.
- "Y el pais / las politicas?" -> v2 tiene un set de hiperparametros de regimen: corro las
  MISMAS personas bajo distintos paises.
- "Opensource?" -> si, va el repo (Fase 0).

---

## 7. Mathematical formalization (the math and the intuition, together)

v1 was deliberately minimal: one number per person (wealth), one lever (effort), two walls
(ruin and the Micawber threshold). v2 keeps that exact spine and adds the machinery the
comments demanded, organized around four questions about each agent:

- who you are: talent $T_i$ and skill $h_i$;
- where you are: zone $z_i$ and your network $c_i$;
- what hits you: random shocks, stressors $St_i$, and opportunities;
- what you pass on: wealth, talent and place handed to your children.

Crucially, all of it funnels into the same single quantity as v1: the drift $\mu_i$, the
expected push on your wealth this period. The new terms just make that push richer and more
honest, and a regime dial $\Theta$ (your country / policy) rescales the structural pieces.
Read section 7.4 first if you want the punchline; the rest defines its pieces.

### 7.1 State vector
In v1 a person was a single number. Now a person is a small profile:

$$x_i = \big(\, w_i,\; T_i,\; h_i,\; z_i,\; e_i,\; s_i,\; St_i,\; c_i,\; g_i \,\big)$$

wealth $w_i$, talent $T_i$ (fixed at birth), skill $h_i$ (grows over life), zone $z_i$,
effort $e_i$, the share of surplus you invest $s_i$, your stressor load $St_i$, your
connectedness $c_i$, and your generation $g_i$. Everything below is just the rules that
move $w_i$ given this profile.

### 7.2 Effort efficiency $\eta$ (idea #1: the scarcity tax)
One comment kept returning: "what if you have sick kids, or inherited debt?" Then the same
effort converts to far less value. We capture that with an efficiency
$\eta_i \in [\eta_{\min}, 1]$ that multiplies the value you create. It collapses when you
are deep below the line or carrying heavy stressors, and approaches $1$ when you have slack:

$$\eta_i = \eta_{\min} + (1-\eta_{\min})\, S\!\big(\, k_w (w_i - w_p) - k_s\, St_i \,\big)$$

where $S$ is the logistic. The term $k_w (w_i - w_p)$ is how far above the poverty line
$w_p$ you sit (your slack), and $k_s St_i$ is the drag of your problems. This is the
experimentally measured "scarcity tax" (Mani 2013): poverty itself eats mental bandwidth,
so an hour of effort buys less. It is precisely why two people with identical effort end up
in different places, and it answers the "effort is constrained by circumstances" critique.

### 7.3 Effort direction and savings, $q$ and $s$ (comments theme 4)
Many comments insisted effort is not hours, it is aim: "smart effort beats blind effort",
"vision", "what you do with the money". We split that into two knobs. Quality $q_i$
multiplies how much value each unit of effort creates and saturates with skill; savings
$s_i$ is how much of your surplus you reinvest instead of consuming:

$$q_i = q_{\min} + (1-q_{\min})\,\frac{h_i}{h_i + h_{1/2}}, \qquad
s_i = s_{\max}\, S\!\big(k_h (h_i - \bar h)\big)\cdot \mathbf{1}\!\left[w_i > w_{\text{sub}}\right]$$

Read $q_i$: at zero skill it sits at the floor $q_{\min}$ (effort barely multiplies); once
skill passes $h_{1/2}$ it climbs toward $1$. Read $s_i$: the indicator says you can only
save above subsistence $w_{\text{sub}}$, and skill or financial literacy raises the share.
So effort now has a magnitude $e_i$, an efficiency $\eta_i$, and a direction $(q_i, s_i)$.

### 7.4 The drift, fully specified (the heart)
This is where everything meets. Each period your wealth gets an expected push $\mu_i$; v1
had three terms, v2 has five:

$$\mu_i = \underbrace{\mu_{\text{base}}(z_i,\Theta)}_{\text{where you are born}}
\; - \; \underbrace{\pi_{\text{pov}}(w_i,\Theta)}_{\text{poverty premium}}
\; + \; \underbrace{\alpha\, e_i\,\eta_i\, q_i}_{\text{value you create}}
\; + \; \underbrace{\beta_N\, c_i}_{\text{your network}}
\; + \; \underbrace{r\, w_i\, s_i}_{\text{your capital compounds}}$$

with the premium switching on below the line,
$\pi_{\text{pov}}(w_i,\Theta) = \pi_0(\Theta)\,\mathbf{1}\!\left[w_i < w_p\right]$. The first
two terms are the v1 structure (Chetty's neighborhood, Ghatak's premium). The third is the
v1 effort lever, now scaled by efficiency and quality. The fourth is new social capital.
The fifth, $r\, w_i\, s_i$, is the quiet engine of inequality: returns on the capital you
already have. The poor have $s_i \approx 0$ (no surplus to invest), so this term is zero for
them and large for the already-wealthy: the same effort buys a permanently steeper climb
once you have a base. That single asymmetry is why the gap widens on its own, with nobody
behaving differently.

### 7.5 Opportunity as a marked Poisson process (idea #6)
"Access to opportunity" was one of the most requested variables, and your hunch that it is
power-law (a few get many, most get few) is exactly right. We model an opportunity as a
discrete event with three independent questions: does one show up, how big is it, and can
you take it.

Arrival. Opportunities knock at a Poisson rate set by where you are and who you know:

$$\lambda_i = \lambda_0\, \exp\!\big(g_z\,\Omega(z_i) + g_c\, c_i\big)$$

richer zones $\Omega(z_i)$ and more connections $c_i$ mean more knocks (preferential
attachment, the Matthew effect).

Size. The payoff is heavy-tailed (Pareto): a handful are life-changing, most are trivial:

$$\Pr(X > x) = \left(\frac{x_{\min}}{x}\right)^{a}, \qquad x \ge x_{\min}, \;\; a \in (1,2]$$

Capture. You only cash it in if you have the skill and the slack to act:

$$\Delta w_i^{\text{opp}} = \kappa\, X \cdot \mathbf{1}\!\left[h_i \ge h_{\min}(X)\right]\cdot \mathbf{1}\!\left[e_i\,\eta_i \ge \tau\right]$$

bigger opportunities demand more skill $h_{\min}(X)$. This one object cleanly separates the
three things people kept blending together: access (the rate $\lambda_i$), luck (which $X$
you draw), and merit (whether you can seize it).

### 7.6 Network and pooling (idea #4)
"No one escapes alone" recurred constantly: cooperatives, unions, family, "move to a better
neighborhood and doors open". We place agents on a graph that forms with homophily (similar
people connect), so segregation emerges by itself. Your social capital is the share of your
contacts who are above the line, Chetty's "economic connectedness":

$$c_i = \frac{1}{\lvert \mathcal{N}(i) \rvert}\sum_{j\in \mathcal{N}(i)} \mathbf{1}\!\left[w_j > w_p\right]$$

A higher $c_i$ raises both your opportunity rate $\lambda_i$ and your efficiency $\eta_i$ (a
friend helps you absorb a shock before it ruins you). Connections also let people pool: a
group $C$ can combine resources to cross the threshold once when
$\sum_{j\in C} w_j \ge w^{*}$, modeling collective escape.

### 7.7 Talent (Normal) becomes outcome (power law) (idea #5, the twist)
You assumed talent is normally distributed, which is correct and standard. The beautiful,
counter-intuitive part (and a perfect reel) is that normal talent still produces wildly
unequal, power-law outcomes. The reason is that wealth grows multiplicatively (the
$r\, w_i\, s_i$ term plus multiplicative opportunity jumps), so each period's wealth is
roughly the previous one times a random factor, plus a shock:

$$w_{t+1} = A_t\, w_t + B_t$$

This is a Kesten recursion, and its stationary distribution has a Pareto tail,
$\Pr(W > w) \sim w^{-\zeta}$, even when the inputs $A_t, B_t$ and talent are light-tailed.
So a Gaussian goes in and a power law comes out, and the very top is dominated by luck
rather than talent (Pluchino 2018; Gabaix on power laws). That is the rigorous backbone of
"the most successful are rarely the most talented".

### 7.8 Generational transmission (idea #2)
The trap is not one life, it is a relay race; several comments cited "6 generations to
escape". At death a child inherits a slice of wealth, a correlated dose of talent, the same
place, and a head start in skill if the parent was above the line:

$$w^{0}_{\text{child}} = b\, w^{\text{final}}_{\text{parent}} + \varepsilon, \qquad
T_{\text{child}} = \rho\, T_{\text{parent}} + \sqrt{1-\rho^{2}}\;\xi, \quad \xi \sim N(0,1)$$

plus $h^{0}_{\text{child}} = h_{\text{floor}} + \delta\,\mathbf{1}\!\left[\text{parent above line}\right]$,
inheriting zone and network unless a rare mobility event (probability $p_{\text{move}}$)
fires. We pin $b$ and $\rho$ so the simulated intergenerational elasticity,

$$\mathrm{IGE} = \frac{\mathrm{Cov}\!\left(\log w_{\text{child}}, \log w_{\text{parent}}\right)}{\mathrm{Var}\!\left(\log w_{\text{parent}}\right)},$$

lands on the Great Gatsby Curve and matches the OECD "generations to mean income" (about
$6$ for Chile). That is the bridge from a toy model to a number people recognize.

### 7.9 Regime hyperparameters $\Theta$ (idea #3)
"It depends on the country", "what about welfare, free education, redistribution?" These are
all the same model with different structural dials. $\Theta$ is the dial set; swapping it is
"change country / policy", and you run it on the same people.

| Lever | Symbol | Effect |
|-------|--------|--------|
| Poverty premium scale | $\pi_0$ | how punishing being poor is |
| Opportunity rate / inequality | $\lambda_0,\, a$ | density and concentration of access |
| Welfare floor | $w_{\text{floor}}$ | a reflecting (not absorbing) barrier: caps ruin |
| Public education | $\delta$ | raises poor agents' $h$ and $\eta$ |
| Redistribution | $t$ | taxes high $w$, funds the floor and poor $\mu_{\text{base}}$ |
| Relative poverty line | $w_p = \max(w_p^{0},\, \theta\,\mathrm{median}(w))$ | the line rises with society |

Presets (Chile / Denmark / USA) are just named $\Theta$ vectors run on the same random
seed, so any difference you see on screen is the policy, not the luck.

### 7.10 The continuum (the #1 requested fix)
The loudest critique: escaping poverty is not the same as becoming rich, and there is a
middle class in between. So we replace the single wall with a ladder of bands and report two
different probabilities. Ordered cutoffs $0 < w_p < w_m < w_a < w^{*}$ define the bands
{pobreza, vulnerable, media, acomodado, rico}, and we track $\Pr(\text{cross } w_p)$ (leave
poverty) separately from $\Pr(\text{reach } w^{*})$ (become rich). Two different events, two
different numbers, which also dissolves the "did the 13% escape by luck?" confusion, because
"escape" now means the lower, reachable wall.

### 7.11 One tick of v2 (the algorithm)
For each living agent $i$, with step $dt$:

1. update $St_i$, then $\eta_i$ (7.2) and $q_i, s_i$ (7.3);
2. form $\mu_i$ (7.4); diffuse $w_i \mathrel{+}= \mu_i\, dt + \sigma_i \sqrt{dt}\; Z$, with $Z \sim N(0,1)$;
3. opportunity: with probability $\lambda_i\, dt$ draw $X \sim \text{Pareto}$ and add $\Delta w_i^{\text{opp}}$ (7.5);
4. apply $\Theta$: welfare floor, tax / redistribution, relative line (7.9);
5. band bookkeeping: record first crossings of $w_p$ and $w^{*}$ (7.10);
6. age; on death reproduce (7.8); periodically rewire the network (7.6).

### 7.12 Parameter table (v2 additions)
| Param | Meaning | Calibrated default |
|-------|---------|-------|
| $\eta_{\min}, k_w, k_s$ | efficiency floor, wealth and stressor sensitivity | 0.3, 4, 1.5 |
| $q_{\min}, h_{1/2}$ | quality floor, skill half-saturation | 0.4, 0.5 |
| $s_{\max}, w_{\text{sub}}, k_h$ | max savings share, subsistence, skill sensitivity | 0.3, 0.1, 3 |
| $r$, slope | return on invested capital, wealth-slope | 0.003, 0.0 per period |
| $\lambda_0, g_z, g_c$ | base opportunity rate, zone and network gains | 0.1, 1.0, 1.5 |
| $a, x_{\min}, \kappa$ | Pareto shape, min payoff, capture scale | 1.5, 0.02, 0.03 |
| $\beta_N, \gamma_{\text{peer}}$ | network drift weight, peer-spillover weight | 0.003, 0.01 |
| $\alpha$ | value-creation weight | 0.012 |
| $\mu_{\text{base}}$ (poor, rich) | base drift / cost-of-living drag by zone | -0.015, -0.008 |
| starts (poor, rich) | birth wealth by zone | 0.05, 0.12 |
| $b, \rho, p_{\text{move}}$ | inheritance, talent heritability, mobility | 0.10, 0.25, 0.05 |
| bands $w_p, w_m, w_a, w^{*}$ | continuum cutoffs | 0.10, 0.25, 0.55, 1.0 |

> **Calibration.** The defaults above put the model in a *realistic* regime: the
> wealth process is near-mean-reverting (a small cost-of-living drag, $\mu_{\text{base}}<0$)
> with a heavy-tailed upside, so reaching $w^{*}$ is a **rare tail event** (~5% of
> poor-born lives, not a majority), the intergenerational elasticity sits in the
> Great Gatsby range ($\mathrm{IGE}\approx 0.3\text{-}0.6$), and the distribution is
> bottom/middle-heavy. Targets and an auditable check live in
> `experiments/calibration/`; the record is in `docs/literature/calibration.md`.
> These are illustrative targets, **not** a fit to any specific country.

### 7.13 How it all fits in one sentence
Who you are (7.1, 7.7) and where you are (7.4-7.6) set your drift and your opportunity
stream; what hits you (the stressors of 7.2 and the diffusion shocks) erodes it
asymmetrically; what compounds (capital in 7.4, opportunities in 7.5) pulls the lucky and
well-placed away; and what you pass on (7.8) turns it into a multi-generational trap, all
under a single policy dial (7.9) and read out honestly on a continuum (7.10). Effort is
still your lever, but now you can see exactly why the same effort travels different
distances.

---

## 8. Interface plan: make the sim show v2

The v1 window (two zones, dots parking top/bottom, a rate HUD, a wealth-gap graph) proved
the core point but can only display one idea. v2 needs a layered, config-driven renderer so
each follow-up reel switches on exactly the overlays it needs, on the same 9:16 canvas.

### 8.1 Architecture refactor (do this first; it unblocks every phase)
- Layered renderer. Split drawing into toggleable layers: bands, agents, network,
  opportunities, lineage, hud, panel. A config dict decides which are on; each reel = a
  layer preset.
- Deterministic seed + replay. Store the RNG seed so you can re-run the SAME agents under a
  different regime $\Theta$ (essential for the country comparison and before/after wipes).
- Record mode. A flag that pins FPS, hides debug text, optionally dumps frames.
- Headless metrics. Keep the headless path emitting the new stats: $\Pr(\text{leave poverty})$,
  $\Pr(\text{rich})$, IGE, Gini, so every visual claim is backed by a number.
- Performance: cap the population near 200-300; for the network layer, draw only a
  subsampled set of edges (e.g. bridging ties) so it stays legible and fast.

### 8.2 Per-concept visual encoding (what each layer looks like)
| Concept | Visual encoding | Control / panel |
|---------|-----------------|-----------------|
| Continuum (Phase 1) | one yellow line becomes 4 shaded horizontal bands; two reference lines: poverty line (white) and rich line (gold); dots colored by band | two big counters: "Salio de pobreza X%" and "Se hizo rico Y%" |
| Effort heterogeneity | per-agent effort as dot size; small histogram panel of the effort distribution | slider sets the mean of the effort distribution, not a global value |
| Effort efficiency $\eta$ | dot opacity/brightness equals $\eta$ (dim = poverty tax); red halo when stressors spike | side gauge: average $\eta$ of poor vs rich |
| Opportunity (Phase 4 prep) | opportunities fall as tokens sized by payoff (few huge, many tiny = visible power law); capture = burst + upward jump; misses fade | log-scale histogram of opportunity sizes; captured vs missed counter |
| Network (Phase 5) | draw edges; bridging (cross-band) ties bright, within-band dim; pooling event = a group flashing and merging upward | "conectividad economica" heat per zone |
| Generations (Phase 2) | lineage threads: child spawns near parent with a thin line; faint per-lineage wealth trail across generations | counter: "Generaciones para escapar" (median) |
| Talent vs Luck (Phase 4) | side scatter panel: talent (x) vs final wealth (y), weak correlation; highlight top-wealth = mid-talent + lucky | toggle to color by "luck captured" |
| Regime / country (Phase 6) | literal floor line (welfare) catching falling dots; preset buttons (Chile/Denmark/USA) that replay the same seed; before/after wipe (9:16 too narrow for side-by-side) | preset bar + the two continuum counters live |

### 8.3 Layout for the reel format (9:16)
- Top ~6%: HUD (regime name, the two counters).
- Middle ~62%: the banded simulation field (agents, network, opportunities, lineage).
- Bottom ~32%: a swappable panel slot holding the phase-specific chart (effort histogram,
  opportunity power law, talent-vs-luck scatter, or wealth-gap-over-time).
- Controls overlaid bottom-left, hidden in record mode.

### 8.4 Build order for the UI (mirrors the reel roadmap)
1. Refactor to layers + seed/replay + headless metrics (8.1). One-time cost, enables all.
2. Bands + two counters (Phase 1). Smallest change, biggest clarity win; answers the #1
   comment.
3. Effort distribution + $\eta$ opacity (Phase 3). Makes "same effort, different result"
   literally visible.
4. Lineage threads + generations counter (Phase 2).
5. Opportunity tokens + power-law histogram, then the talent-vs-luck scatter (Phase 4). The
   visual centerpiece of the series.
6. Network edges + pooling (Phase 5).
7. Regime presets + welfare floor + seed-replay wipe (Phase 6).

> Suggested first commit: 8.4 step 1 (refactor) + step 2 (continuum bands). It ships the
> most-requested fix and lays the rails for everything else.
