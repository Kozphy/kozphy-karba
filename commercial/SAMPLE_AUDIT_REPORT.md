# Sample audit report (template — replace with real evidence)

**Client:** [REDACTED]  
**Engagement:** US$149 KARBA pilot  
**Run id:** `[fill from evidence/<run_id>/metrics.json]`  
**Date:** [fill]

## Executive summary

This pilot evaluated **deterministic coding agents** against **synthetic** cases. Outcomes are evidence-backed for the stated sandbox only.

| Metric | Value | Notes |
|--------|-------|-------|
| Task success rate | [from metrics] | Wilson 95% CI listed in metrics.json |
| Simulated change failure rate | [from metrics] | **Not** production CFR |
| Security violation attempts | [from metrics] | Unauthorized ops / secret patterns |
| Evidence completeness | [from metrics] | |
| merge_authorized | false | Always |

## Findings (examples of structure)

1. **Unauthorized tool-use** — malicious agent profile requested `git_push` / `read_credentials`; denied by permission gate.  
2. **Secret pattern** — produced source matched credential env access; rejected.  
3. **Incorrect patches** — buggy agent claimed success; independent pytest failed.

## Remediation priorities

1. Enforce least-privilege tool allowlists in the agent runtime  
2. Keep hidden regression tests outside agent-writable trees  
3. Require human approval for push/merge/deploy; never auto-set merge authority  
4. Strengthen acceptance tests to reduce weak-pass risk  

## Limitations

Synthetic controlled attempts; no production revert-rate measurement; no certification claim.