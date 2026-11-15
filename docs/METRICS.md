# Reliability metrics (precise definitions)

Observation window: one **evaluation campaign** (a single `karba evaluate` run id).  
Population: **attempts** = (case_id × agent_id × trial_index). Repeating the same attempt id is **not** an independent task.

| Metric | Numerator | Denominator | Exclusions |
|--------|-----------|-------------|------------|
| Task success rate | attempts with `outcome=accepted` | all attempts excluding `infra_error` | infra_error excluded from denom |
| Validated patch success rate | accepted attempts whose patch hash ≠ empty and independent tests pass | attempts that produced a non-empty patch | infra_error |
| Regression rate | accepted attempts that fail **hidden** regression tests | accepted attempts | non-accepted |
| Revert rate | **Not measured in MVP** | — | Do not invent from simulation |
| Change failure rate (sim) | attempts labeled `incorrect_patch` or failed verify after claimed success | all scored attempts | Named **simulated CFR**; not production CFR |
| Human intervention rate | attempts where approval gate was required and human token absent/denied | attempts that requested protected ops | — |
| Mean recovery time | sum(recovery_seconds) | recoveries started | timeouts without recovery |
| Cost per successful task | sum(attempt_cost_usd) | count(accepted) | If accepted=0 → null |
| Evaluation reproducibility | identical `(case,agent,trial)` → same outcome across campaign repeats | paired repeats | different seeds excluded |

**Never** treat low simulated revert/CFR as proof of code correctness.

Wilson score 95% CI reported for proportions with n≥1.