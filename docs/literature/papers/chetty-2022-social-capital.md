# Chetty, Jackson, et al. (2022)

**Social capital I: measurement and associations with economic mobility** and
**Social capital II: determinants of economic connectedness.** *Nature*, 608.

- DOI I: https://doi.org/10.1038/s41586-022-04996-4
- DOI II: https://doi.org/10.1038/s41586-022-04997-3
- Open access on nature.com.

## What it shows (in our words)

Using large-scale social-network data, the authors construct "economic
connectedness" - the share of a person's friends who are high socioeconomic
status - and find it is one of the strongest predictors of upward mobility for
low-income children, beyond neighbourhood income or inequality alone. Who you are
connected to matters, not just where you live.

## What we borrow

Economic connectedness as a concrete, predictive measure of social capital.

## How it maps to the model

It defines our **connectedness** `c_i` in section 7.6: the share of an agent's
network that sits above the poverty line. Connectedness feeds a small drift term
(`beta_network * c`) and raises the opportunity-arrival rate, so well-connected
agents both progress faster and see more opportunities.
