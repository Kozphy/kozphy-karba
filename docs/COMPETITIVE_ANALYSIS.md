# Phase 1 — Competitive gap analysis (KARBA)

**Method:** Public GitHub metadata + README/docs fetched 2026-11-16. Local Kozphy repos inspected read-only.  
**Legend:** **V** = verified from public docs/metadata · **I** = reasonable inference · **U** = unverified claim

Existing Kozphy product repos were **not** modified.

## Competitor snapshot

| Project | Stars (V) | License (V) | Core focus (V) | Isolation (V/I) | Audit evidence (V/I) | Human gates (V/I) |
|---------|-----------|-------------|----------------|-----------------|----------------------|-------------------|
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) | 6193 | MIT | Real GitHub issues → patch; Docker eval | Docker (V) | logs/`results.json` (V) | External leaderboard submit (V); not merge-authority gates (I) |
| [OpenHands/benchmarks](https://github.com/OpenHands/benchmarks) | 134 | MIT | Multi-bench harness for OpenHands V1 SDK | Docker + remote runtime (V) | instance logs, rich logging (V) | LLM config required; safety bench present (V) |
| [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk) | 1399 | MIT | Agent SDK (tools/workspace/server) | Container workspace (I/V via docs) | SDK-level, not audit product (I) | Critic module exists in newer SDK (V) |
| [SWE-PR](https://github.com/Software-Engineering-Arena/SWE-PR) | 13 | none listed | Live GitHub PR merge leaderboard | None — tracks public PRs (V) | HF datasets of PR metadata (V) | Community submit (V) |
| [repoagentbench](https://github.com/HumphreySun98/repoagentbench) | 26 | MIT | Mine *your* PRs → local agent bench | Per-task venv (V) | manifest/events/verification JSON (V) | Local-first; mock-fix oracle (V) |
| [agent-eval-platform](https://github.com/wuchris-ch/agent-eval-platform) | 0 | Apache-2.0 | Evidence-first eval, k3s, OTel, scanners | k3s pods + Docker (V) | JSON+SQLite+hashes; accepted/rejected/infra_error (V) | Blind eval, release gates, privacy filtering (V) |
| [latitude coding-agent-benchmark](https://github.com/latitude-dev/coding-agent-benchmark) | 1 | MIT | Cost/latency/tool reliability; Latitude traces | Sandboxed JS task copy (V) | results.jsonl + Latitude traces (V) | Tamper detection on test edits (V) |

### Local Kozphy context (V, read-only)

| Asset | Relevance |
|-------|-----------|
| EvalForge | Local-first eval + hashed evidence patterns |
| ci-failure-orchestrator | CI failure RCA / selective verification |
| Enterprise-RAG-Evaluation | Deterministic RAG eval + governance framing |
| kozphy-atv (local) | Sealed acceptance, independent verify, permission deny, synthetic coding bench |
| agent-trust-gateway (local) | Offline evidence assessor; `merge_authorized=false` |

## Capability matrix → KARBA recommendation

| Capability | Best observed | KARBA stance |
|------------|---------------|--------------|
| Real-world issue difficulty | SWE-bench | **Integrate later** (consume predictions); do not reimplement corpus |
| Agent framework | OpenHands SDK | **Reuse optionally** as adapter; not required for MVP |
| Multi-bench orchestration | OpenHands/benchmarks | **Reuse patterns**; keep KARBA harness thin |
| Live merge popularity | SWE-PR | **Do not use as correctness proof** (V docs admit no sandboxes); optional external signal only |
| Private-repo contamination-free tasks | repoagentbench | **Integrate later** for client PRs; MVP uses synthetic cases |
| Evidence-first + fail-closed outcomes | agent-eval-platform | **New implementation** inspired by outcome model (`accepted`/`rejected`/`infra_error`) — avoid k3s complexity in MVP |
| Cost/latency/tool reliability | Latitude bench | **New implementation** (deterministic cost model for stub agents; real cost fields reserved) |
| Trust/governance / human approval | Kozphy ATG + ATV | **New implementation** in KARBA (portfolio differentiator) |
| Commercial US$149 audit pack | Not seen as a productized pilot in these repos (I) | **New** |

## Gaps KARBA fills (differentiator)

1. **Assurance product packaging** — reliability metrics with explicit numerators/denominators + confidence intervals on **synthetic controlled attempts**, plus a paid pilot offer (docs only; no outreach).
2. **Governance-first coding-agent eval** — unauthorized tool-use cases, secrets/deny-list, human approval gates, evidence that never grants merge authority.
3. **Deterministic baselines first** — oracle / buggy / malicious / timeout agents before live LLM spend.
4. **Portfolio-credible honesty** — no fabricated production revert rates; simulated change-failure ≠ production CFR.

## Adoption barriers observed (V/I)

- SWE-bench: heavy Docker/storage (V warning ≥120GB).
- OpenHands benchmarks: SDK submodule + LLM keys + optional remote runtime (V).
- agent-eval-platform: k3s/OTel depth → high setup cost (V); strongest evidence story.
- repoagentbench: early alpha; needs `gh` + real agents for full value (V).
- SWE-PR: selection bias / maintainer taste confounds (I); not a sandbox.

## Decision

**Build a new local MVP (`kozphy-karba`)** that implements A–F from the mission brief, conceptually aligned with ATV/ATG and agent-eval-platform outcome semantics, without forking or modifying those repositories.