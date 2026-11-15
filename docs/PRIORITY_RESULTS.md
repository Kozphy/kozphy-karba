# Priority upgrade — actual results

Date: 2026-11-16

## 1. Docker-isolated verify

- Image built: `kozphy-karba-verifier:py312`
- `run-mvp-002`: **128/128** attempts with `isolation=container`, `network=none`
- Adapter campaign `run-adapters-001`: **64/64** container verifies
- pytest `test_container_isolation_oracle` passed when Docker available

## 2. Aider / OpenHands adapters

- `aider-mock` / `openhands-mock`: deterministic patches through permission + evidence gates
- Live modes fail-closed without flags; with flags still refuse autonomous API spend
- `run-adapters-001`: task success **1.0** (64 accepted), infra_errors **0**

## 3. Reproducibility delta

| | |
|--|--|
| Baseline | `run-mvp-001` (host) |
| Candidate | `run-mvp-002` (container) |
| Paired attempts | 128 |
| Matching outcomes | **128** |
| Evaluation reproducibility | **1.0** |
| Wilson 95% CI | **[0.971, 1.0]** |
| Mismatches | **0** |

Evidence:
- `evidence/run-mvp-002/metrics.json`
- `evidence/run-mvp-002/reproducibility.json`
- `evidence/run-adapters-001/metrics.json`

Unit/integration: **14 passed** (`pytest -q`).