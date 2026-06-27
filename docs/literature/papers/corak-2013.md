# Corak (2013)

**Income Inequality, Equality of Opportunity, and Intergenerational Mobility.**
*Journal of Economic Perspectives*, 27(3), 79-102.

- DOI: https://doi.org/10.1257/jep.27.3.79
- Free (IZA discussion paper 7520): https://docs.iza.org/dp7520.pdf

## What it shows (in our words)

Documents the "Great Gatsby Curve": countries with higher income inequality tend
to have lower intergenerational mobility (a higher intergenerational elasticity,
IGE - the slope linking parents' and children's incomes). More unequal societies
pass advantage and disadvantage down more strongly.

## What we borrow

The IGE as a single, measurable target for how much status is inherited, and the
empirical link between inequality and immobility.

## How it maps to the model

It is the **calibration target** for the generational layer (section 7.8): we
tune the inheritance fraction `b` and talent heritability `rho` so the simulated
IGE matches an empirical value, rather than choosing them arbitrarily. The
`FirstPassageMonitor` reports the simulated IGE for this comparison.
