# KARBA MVP — final engineering & commercial report

**Project path:** `C:\Users\dbdf0\Kozphy\kozphy-karba`  
**Date:** 2026-11-16  
**Constraint compliance:** No existing Kozphy/GitHub product repos modified; no remote created; no customer contact; no fabricated production revert rates.

## Phases completed

1. Competitive analysis → `docs/COMPETITIVE_ANALYSIS.md`  
2. Architecture / metrics / threat model → `docs/ARCHITECTURE.md`, `METRICS.md`, `THREAT_MODEL.md`  
3. MVP implementation → `src/karba/`  
4. Evaluation → 32 cases × 4 agents × 1 trial = **128 attempts** (`run-mvp-001`)  
5. Commercial pack → `commercial/` (unpublished)  
6. Acceptance evidence → tests + hashed evidence under `evidence/run-mvp-001/`

## Tests executed

```
pytest -q  →  7 passed
```

## Actual evaluation results (`run-mvp-001`)

| Metric | Observed |
|--------|----------|
| Attempts | 128 |
| Infra errors | 0 |
| Task success rate | **0.25** (32/128 oracle accepts) |
| Wilson 95% CI | **[0.183, 0.332]** |
| Validated patch success rate | 0.333 (32 accepted / 96 patched attempts) |
| Regression rate | 0.0 (oracle passed hidden tests when present) |
| Revert rate | **null** (intentionally unmeasured) |
| Simulated CFR | **0.75** (rejected/scored — **not** production CFR) |
| Human intervention rate | 0.25 (malicious profile) |
| Security violation attempts | **32** (malicious only) |
| Evidence completeness | **1.0** |
| Cost / successful task | US$0.035 (stub pricing) |
| merge_authorized | always false |

Evidence root: `evidence/run-mvp-001/`  
Metrics: `evidence/run-mvp-001/metrics.json`  
SQLite: `evidence/karba.sqlite`

## Security findings

- Permission gate denies `git_push` / `deploy` / `read_credentials` (unit-tested).  
- Malicious agent secret-pattern patches → `rejected` with findings.  
- Semgrep/Gitleaks not required; recorded as `scanner_unavailable` when absent (not counted as violations).  
- Residual: tempdir isolation only; host-admin can forge evidence.

## Unresolved issues

- Live LLM / OpenHands / Aider adapters not wired  
- Docker/`network=none` isolation deferred  
- `bad_dependency_config` category still uses the same calc fixture (taxonomy placeholder)  
- Reproducibility across two campaign repeats not yet automated as a metric job  

## Reproducibility

See `README.md` Windows install + evaluate commands. Use `--run-id` for a fresh evidence tree.

## Next three priorities — DONE

See `docs/PRIORITY_UPGRADE.md` and `docs/PRIORITY_RESULTS.md`.

1. Docker-isolated verify (`--isolation container`, network=none) — **128/128** on `run-mvp-002`  
2. Aider/OpenHands adapters (mock default; live fail-closed) — `run-adapters-001` **64/64**  
3. Second campaign reproducibility vs `run-mvp-001` — **1.0** (128/128 paired matches)  

## Commercial

US$149 pilot pack is drafted under `commercial/`. **Do not publish or outreach without explicit approval.**