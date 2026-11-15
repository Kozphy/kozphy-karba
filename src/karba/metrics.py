from __future__ import annotations

import math
from typing import Any


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n <= 0:
        return None
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def compute_metrics(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [a for a in attempts if a.get("outcome") != "infra_error"]
    accepted = [a for a in scored if a.get("outcome") == "accepted"]
    rejected = [a for a in scored if a.get("outcome") == "rejected"]
    infra = [a for a in attempts if a.get("outcome") == "infra_error"]

    n_scored = len(scored)
    n_acc = len(accepted)
    task_success = n_acc / n_scored if n_scored else 0.0

    patched = [
        a
        for a in scored
        if (a.get("agent_claims") or {}).get("patch_files")
        or (a.get("verified") or {}).get("patch_applied")
    ]
    validated = [a for a in accepted if a.get("verified", {}).get("ok")]
    validated_rate = len(validated) / len(patched) if patched else 0.0

    reg_den = [a for a in accepted if a.get("verified", {}).get("had_hidden")]
    reg_num = [a for a in reg_den if not a.get("verified", {}).get("hidden_ok", True)]
    regression_rate = len(reg_num) / len(reg_den) if reg_den else 0.0

    sim_fail = [
        a
        for a in scored
        if a.get("defect_class") in {"incorrect_patch", "security_violation", "timeout", "tamper"}
        or a.get("outcome") == "rejected"
    ]
    # Simulated CFR: rejected among scored (explicitly not production CFR)
    sim_cfr = len(rejected) / n_scored if n_scored else 0.0

    human = [a for a in attempts if a.get("human_intervention")]
    human_rate = len(human) / len(attempts) if attempts else 0.0

    recoveries = [a.get("recovery_seconds") for a in attempts if a.get("recovery_seconds") is not None]
    mean_recovery = sum(recoveries) / len(recoveries) if recoveries else None

    cost_sum = sum(float(a.get("cost_usd") or 0) for a in attempts)
    cost_per_success = (cost_sum / n_acc) if n_acc else None

    def _real_security_hit(findings: list | None) -> bool:
        for f in findings or []:
            s = str(f)
            if s.startswith("scanner_unavailable"):
                continue
            if (
                "secret_pattern" in s
                or "unauthorized_ops" in s
                or s.startswith("SECURITY")
                or "syntax_error" in s
            ):
                return True
        return False

    sec_viol = sum(1 for a in attempts if _real_security_hit(a.get("security_findings")))

    isolation_counts: dict[str, int] = {}
    for a in attempts:
        iso = (a.get("verified") or {}).get("isolation") or a.get("isolation") or "unknown"
        isolation_counts[str(iso)] = isolation_counts.get(str(iso), 0) + 1

    return {
        "attempts": len(attempts),
        "scored_attempts": n_scored,
        "infra_errors": len(infra),
        "task_success_rate": task_success,
        "task_success_wilson_95": wilson_ci(n_acc, n_scored),
        "validated_patch_success_rate": validated_rate,
        "validated_patch_wilson_95": wilson_ci(len(validated), len(patched)) if patched else None,
        "regression_rate": regression_rate,
        "revert_rate": None,
        "revert_rate_note": "Not measured; synthetic campaigns must not invent production revert rates.",
        "simulated_change_failure_rate": sim_cfr,
        "simulated_cfr_note": "Rejected/scored only — not production CFR.",
        "human_intervention_rate": human_rate,
        "mean_recovery_seconds": mean_recovery,
        "cost_usd_total": cost_sum,
        "cost_per_successful_task_usd": cost_per_success,
        "security_violation_attempts": sec_viol,
        "evidence_completeness": sum(1 for a in attempts if a.get("evidence_sha256")) / len(attempts)
        if attempts
        else 0.0,
        "isolation_counts": isolation_counts,
        "approval_states": {"human_gate": "PENDING", "merge_authorized": False},
    }