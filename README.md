# KARBA — Kozphy Agent Reliability Benchmark & Assurance Platform

Local MVP for evidence-driven evaluation of AI coding-agent reliability, security, and governance.

**Constraints honored:** existing Kozphy/GitHub product repos are read-only; no remote repo created; no customer outreach; no fabricated production metrics.

## Docs

| Doc | Purpose |
|-----|---------|
| `docs/COMPETITIVE_ANALYSIS.md` | Phase 1 gap analysis |
| `docs/ARCHITECTURE.md` | System design |
| `docs/METRICS.md` | Metric numerators/denominators |
| `docs/THREAT_MODEL.md` | Security boundaries |
| `commercial/` | US$149 pilot pack (unpublished) |
| `docs/FINAL_REPORT.md` | Completion report (after eval) |

## Windows install

```powershell
cd C:\Users\dbdf0\Kozphy\kozphy-karba
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
```

## Reproduce evaluation (≥30 cases, ≥100 attempts)

```powershell
python scripts\generate_cases.py
# 32 cases × 4 agents × 1 trial = 128 attempts
python -m karba evaluate --cases benchmarks\cases --out evidence --db evidence\karba.sqlite --trials 1 --agents oracle,buggy,malicious,timeout --run-id run-mvp-001
pytest -q
python -m karba dashboard --metrics evidence\run-mvp-001\metrics.json --port 8787
```

### Docker isolation + second campaign (reproducibility)

```powershell
# auto uses Docker network=none when daemon is up; else host fallback
python -m karba evaluate --cases benchmarks\cases --out evidence --db evidence\karba.sqlite --trials 1 --agents oracle,buggy,malicious,timeout --run-id run-mvp-002 --isolation auto --compare-to run-mvp-001

# Optional adapter mocks (same gates)
python -m karba evaluate --cases benchmarks\cases --out evidence --db evidence\karba.sqlite --agents aider-mock,openhands-mock --run-id run-adapters-001 --isolation auto
```

See `docs/PRIORITY_UPGRADE.md`.

`accepted` never sets `merge_authorized`; human_gate remains `PENDING`.

## Known limitations

- Live Aider/OpenHands adapters are fail-closed (no autonomous API spend)
- Docker isolation residual: host Docker daemon trust
- Semgrep/Gitleaks optional (`scanner_unavailable` if missing)
- Simulated CFR ≠ production change-failure rate
- Revert rate intentionally unmeasured