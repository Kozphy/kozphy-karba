# Priority upgrade notes (Docker / adapters / reproducibility)

## 1. Docker-isolated verify

- Image: `kozphy-karba-verifier:py312` built from `docker/Dockerfile`
- Runtime flags: `--network none`, `--cap-drop ALL`, `no-new-privileges`, CPU/memory/pids limits
- CLI: `--isolation auto|host|container`
- `auto` uses Docker when the daemon is available; otherwise host fallback (recorded in evidence)
- Residual risk: Docker daemon compromise / Windows mount semantics — not kernel attestation

## 2. Aider / OpenHands adapters

| Agent id | Behavior |
|----------|----------|
| `aider` / `aider-mock` | Deterministic mock patch (same gates + evidence) |
| `openhands` / `openhands-mock` | Deterministic mock patch |
| `aider-live` / `openhands-live` | Fail-closed unless `KARBA_ALLOW_LIVE_AGENTS=1` + approval token; still **refuses API spend** in MVP |

Live adapters never set `merge_authorized`. They record unauthorized op probes.

## 3. Reproducibility

```powershell
python -m karba evaluate ... --run-id run-mvp-002 --compare-to run-mvp-001
# or
python -m karba reproduce --baseline run-mvp-001 --candidate run-mvp-002
```

Metric: paired identical `(case_id, agent_id, trial_index)` outcome match rate + Wilson CI.  
Repeats are **not** counted as independent tasks.