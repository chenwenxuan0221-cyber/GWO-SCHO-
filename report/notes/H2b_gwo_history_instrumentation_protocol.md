# H2b — Supplementary-material availability decision + instrumentation protocol

## Availability check

The paper itself states that animated versions of Fig. 11 are in the
Supplementary Materials, and Appendix A points supplementary data to the online
DOI record.

A current web/source check found:

- ScienceDirect article record: article metadata is accessible, but the page is
  access-restricted to automated retrieval and no supplementary asset was
  exposed by the accessible record.
- Griffith Research Online: an accepted-manuscript PDF is accessible, but no
  Fig.-11 supplementary animation/code was surfaced in the public record found.
- Official `alimirjalili/GWO` GitHub repository: contains only the generic GWO
  implementation/demo files (`GWO.m`, `main.m`, benchmark helpers, PDF/image);
  no dedicated Fig.-11 history/animation runner is present.
- MATLAB File Exchange: the public GWO submission lists the same generic
  function set; the GWO toolbox is a GUI-oriented optimizer package rather than
  a documented Fig.-11 source package.

Therefore H2 currently cannot claim Tier-A exact/source-backed recovery of:
- exact shift vectors,
- exact Fig.-11 random stream,
- exact history sampling semantics.

The project proceeds with Tier B:
`PAPER-STRUCTURE / CONTROLLED-EQUIVALENT`.

If the original supplementary ZIP/videos are later obtained, Tier A can be
reopened without changing the frozen core GWO.

## Instrumentation sampling convention

The new `gwo_with_history` adapter copies the frozen `algorithms/gwo.py`
control flow and random-call order.

Histories are sampled at the **evaluated population state**:
1. boundary repair,
2. save positions,
3. evaluate fitness,
4. save fitness,
5. update alpha/beta/delta,
6. compute a,
7. update positions,
8. save historical-best convergence value.

Recorded arrays:
- `position_history[t, agent, dim]`
- `fitness_history[t, agent]`
- `first_agent_x1[t]`
- `first_agent_fitness[t]`
- `best_position_history[t, dim]`
- `a_history[t]`
- `convergence_curve[t]`

This sampling choice is explicit and reproducible. It is not claimed to be
the unavailable original Fig.-11 internal logging convention.

## Regression requirement

For the same objective, seed and protocol, adding instrumentation must not
change:
- final best score,
- best position,
- complete convergence curve.

The supplied H2b test checks exact equality against frozen `algorithms/gwo.py`
for F1 and F9 using:
- N=6
- MaxIter=100
- seed=1000

No Fig.-11 shifted benchmark experiment is run in H2b.
