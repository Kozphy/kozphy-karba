# KARBA architecture (MVP)

```mermaid
flowchart LR
  Cases[Synthetic case corpus] --> Engine[Benchmark Engine]
  Agents[Deterministic agents<br/>oracle buggy malicious timeout] --> Engine
  Engine --> Sandbox[Isolated temp workspace]
  Sandbox --> Verify[Independent verifier<br/>pytest ruff security]
  Verify --> Evidence[Evidence Engine<br/>JSON MD hashes]
  Evidence --> Store[(SQLite)]
  Store --> Dash[Local dashboard]
  Perm[Permission gate] -.-> Agents
  Perm -.-> Engine
```

## Components

| ID | Module | Role |
|----|--------|------|
| A | `karba.engine` | Load cases, run agents, bound retries |
| B | `karba.metrics` | Reliability metrics + Wilson CI |
| C | `karba.security` | Permissions, secret scan, fail-closed |
| D | `karba.evidence` | JSON/MD reports + SHA-256 |
| E | `karba.dashboard` | HTML metrics UI |
| F | `commercial/` | US$149 pilot pack (no outreach) |

## Trust boundary

- **Untrusted:** agent patches, stdout, claims of success
- **Trusted:** sealed case acceptance, verifier process, metrics formulas, SQLite written by harness
- **Never claimed:** production revert rate, certification, customer adoption

## Isolation (MVP)

Temp directory copy per attempt. Docker optional later. Residual risk: host-admin compromise, no kernel isolation.