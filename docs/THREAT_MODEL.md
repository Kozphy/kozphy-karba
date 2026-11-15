# Threat model — KARBA MVP

Status: engineering controls for a local synthetic assurance prototype. Not a certification.

## Assets

- Integrity of acceptance criteria and hidden tests
- Authenticity of evidence (hashes, outcomes)
- Host secrets / credentials (must not be used by agents)
- Client trust in audit reports (honesty of limitations)

## Adversaries / failure modes

1. Agent weakens or deletes tests
2. Agent reads env secrets / attempts push-deploy
3. Prompt injection via code comments / logs
4. Harness bugs counting infra_error as success
5. Operator overclaims (production CFR from synthetic data)

## Controls

- Hidden tests kept outside agent-writable paths until verify stage (MVP: verify uses pristine tests from case package after agent edit of `src/` only)
- Permission deny-list for protected ops; fail-closed
- Secret pattern scan on produced source
- Outcome model: `accepted` | `rejected` | `infra_error`
- Evidence separates `agent_claims` from `verified`
- Metrics docs forbid inventing production revert rates

## Residual risks

- Tempdir isolation ≠ container/k8s isolation; kernel exploits out of scope
- Host admin can forge evidence
- Stub agents ≠ live LLM behavior; live adapters need same gates
- Semgrep/Gitleaks optional; MVP includes lightweight scanners if tools missing → record as `scanner_unavailable` not pass

## Docker note

If Docker is added later: network=none, read-only root, dropped caps — still not a guarantee against privileged daemon compromise.