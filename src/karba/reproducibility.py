from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from karba.metrics import wilson_ci


def _key(a: dict[str, Any]) -> tuple[str, str, int]:
    return (str(a["case_id"]), str(a["agent_id"]), int(a["trial_index"]))


def compare_attempt_sets(
    baseline: list[dict[str, Any]],
    candidate: list[dict[str, Any]],
) -> dict[str, Any]:
    """Paired reproducibility: same (case, agent, trial) → same outcome.

    Repeated executions are not independent tasks; this metric measures stability.
    """
    base_map = {_key(a): a for a in baseline}
    cand_map = {_key(a): a for a in candidate}
    shared = sorted(set(base_map) & set(cand_map))
    matched = 0
    mismatched: list[dict[str, Any]] = []
    for k in shared:
        b, c = base_map[k], cand_map[k]
        if b.get("outcome") == c.get("outcome"):
            matched += 1
        else:
            mismatched.append(
                {
                    "case_id": k[0],
                    "agent_id": k[1],
                    "trial_index": k[2],
                    "baseline_outcome": b.get("outcome"),
                    "candidate_outcome": c.get("outcome"),
                }
            )
    n = len(shared)
    rate = matched / n if n else 0.0
    return {
        "paired_attempts": n,
        "matching_outcomes": matched,
        "mismatched_outcomes": len(mismatched),
        "evaluation_reproducibility": rate,
        "reproducibility_wilson_95": wilson_ci(matched, n) if n else None,
        "baseline_only": len(set(base_map) - set(cand_map)),
        "candidate_only": len(set(cand_map) - set(base_map)),
        "mismatches": mismatched[:50],
        "note": "Paired identical (case,agent,trial) keys; repeats are not independent tasks.",
    }


def load_attempts_from_run(evidence_root: Path, run_id: str) -> list[dict[str, Any]]:
    """Load attempts from per-attempt evidence.json files under a run directory."""
    root = evidence_root / run_id
    attempts: list[dict[str, Any]] = []
    for path in sorted(root.glob("*/*/evidence.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        attempts.append(
            {
                "run_id": data.get("run_id"),
                "case_id": data.get("case_id"),
                "agent_id": data.get("agent_id"),
                "trial_index": data.get("trial_index"),
                "outcome": data.get("outcome"),
                "evidence_sha256": data.get("evidence_sha256"),
                "verified": data.get("verified"),
                "security_findings": data.get("security_findings"),
                "agent_claims": data.get("agent_claims"),
                "cost_usd": (data.get("agent_claims") or {}).get("cost_usd", 0),
            }
        )
    return attempts


def write_reproducibility_report(
    *,
    baseline_run: str,
    candidate_run: str,
    comparison: dict[str, Any],
    out_path: Path,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "baseline_run": baseline_run,
        "candidate_run": candidate_run,
        **comparison,
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    md = out_path.with_suffix(".md")
    md.write_text(
        "\n".join(
            [
                f"# Reproducibility delta — {baseline_run} vs {candidate_run}",
                "",
                f"- Paired attempts: **{comparison['paired_attempts']}**",
                f"- Matching outcomes: **{comparison['matching_outcomes']}**",
                f"- Evaluation reproducibility: **{comparison['evaluation_reproducibility']:.4f}**",
                f"- Wilson 95% CI: `{comparison['reproducibility_wilson_95']}`",
                f"- Mismatches: **{comparison['mismatched_outcomes']}**",
                "",
                comparison["note"],
                "",
            ]
        ),
        encoding="utf-8",
    )
