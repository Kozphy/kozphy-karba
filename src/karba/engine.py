from __future__ import annotations

import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from karba.agents import run_agent
from karba.evidence import build_evidence, write_evidence
from karba.metrics import compute_metrics
from karba.security import PermissionGate, optional_external_scanners
from karba.store import connect, save_metrics, upsert_attempt
from karba.verify import Isolation, apply_src_patches_only, run_verify


def _load_meta(case_dir: Path) -> dict[str, Any]:
    return json.loads((case_dir / "case.json").read_text(encoding="utf-8"))


def run_attempt(
    *,
    run_id: str,
    case_dir: Path,
    agent_id: str,
    trial_index: int,
    out_dir: Path,
    isolation: Isolation = "auto",
    approval_token_path: Path | None = None,
) -> dict[str, Any]:
    meta = _load_meta(case_dir)
    gate = PermissionGate()
    tmp = Path(tempfile.mkdtemp(prefix="karba-"))
    workspace = tmp / "ws"
    try:
        shutil.copytree(
            case_dir,
            workspace,
            ignore=shutil.ignore_patterns("candidates", ".venv", "__pycache__"),
        )
        claim = run_agent(
            agent_id,
            case_dir,
            gate,
            approval_token_path=approval_token_path,
        )
        ignored = apply_src_patches_only(workspace, claim.patch_files)
        tamper_intent = any(not k.replace("\\", "/").startswith("src/") for k in claim.patch_files)

        human = bool(gate.attempts)
        for op in claim.requested_ops:
            gate.request(op)
            human = True

        verify = run_verify(workspace, case_dir, isolation=isolation)
        scanner_notes = optional_external_scanners(workspace)

        if agent_id in ("timeout", "aider-live", "openhands-live") and not claim.patch_files:
            outcome = "rejected"
            recovery = None
        elif not verify.ok:
            outcome = "rejected"
            recovery = None
        else:
            outcome = "accepted"
            recovery = claim.elapsed_seconds if agent_id in ("oracle", "aider", "aider-mock", "openhands", "openhands-mock") else None

        verified = {
            "ok": verify.ok,
            "pytest_ok": verify.pytest_ok,
            "ruff_ok": verify.ruff_ok,
            "security_ok": verify.security_ok,
            "hidden_ok": verify.hidden_ok,
            "had_hidden": (case_dir / "hidden_tests").is_dir(),
            "test_summary": verify.test_summary,
            "ignored_non_src_patches": ignored,
            "tamper_intent": tamper_intent,
            "patch_applied": bool(claim.patch_files),
            "isolation": verify.isolation,
            "network": verify.network,
        }

        security_findings = list(verify.findings) + scanner_notes
        if gate.attempts:
            security_findings.append(f"unauthorized_ops:{','.join(gate.attempts)}")

        evidence = build_evidence(
            run_id=run_id,
            case_id=meta["case_id"],
            agent_id=agent_id,
            trial_index=trial_index,
            outcome=outcome,
            agent_claims=claim.model_dump(),
            verified=verified,
            commands=verify.commands,
            security_findings=security_findings,
            notes="synthetic controlled attempt; not production evidence",
        )
        ev_path = out_dir / run_id / meta["case_id"] / f"{agent_id}_t{trial_index}" / "evidence.json"
        write_evidence(ev_path, evidence)

        return {
            "run_id": run_id,
            "case_id": meta["case_id"],
            "agent_id": agent_id,
            "trial_index": trial_index,
            "outcome": outcome,
            "agent_claims": claim.model_dump(),
            "verified": verified,
            "security_findings": security_findings,
            "commands": verify.commands,
            "recovery_seconds": recovery,
            "human_intervention": human,
            "cost_usd": claim.cost_usd,
            "defect_class": meta.get("defect_class"),
            "evidence_sha256": evidence["evidence_sha256"],
            "evidence_path": str(ev_path),
            "merge_authorized": False,
            "human_gate": "PENDING",
            "isolation": verify.isolation,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "run_id": run_id,
            "case_id": case_dir.name,
            "agent_id": agent_id,
            "trial_index": trial_index,
            "outcome": "infra_error",
            "agent_claims": {"error": str(exc)},
            "verified": {"ok": False},
            "security_findings": [f"infra:{type(exc).__name__}"],
            "commands": [],
            "recovery_seconds": None,
            "human_intervention": False,
            "cost_usd": 0.0,
            "evidence_sha256": None,
            "merge_authorized": False,
            "human_gate": "PENDING",
            "isolation": isolation,
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def evaluate_campaign(
    *,
    cases_root: Path,
    agents: list[str],
    trials: int,
    out_dir: Path,
    db_path: Path,
    run_id: str | None = None,
    isolation: Isolation = "auto",
    approval_token_path: Path | None = None,
) -> dict[str, Any]:
    run_id = run_id or datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    cases = sorted(p for p in cases_root.iterdir() if p.is_dir() and (p / "case.json").is_file())
    conn = connect(db_path)
    attempts: list[dict[str, Any]] = []
    for case_dir in cases:
        for agent_id in agents:
            for trial in range(trials):
                rec = run_attempt(
                    run_id=run_id,
                    case_dir=case_dir,
                    agent_id=agent_id,
                    trial_index=trial,
                    out_dir=out_dir,
                    isolation=isolation,
                    approval_token_path=approval_token_path,
                )
                upsert_attempt(conn, rec)
                attempts.append(rec)
                print(
                    f"{rec['case_id']} {agent_id} t{trial}: {rec['outcome']} "
                    f"isolation={rec.get('isolation')}"
                )

    metrics = compute_metrics(attempts)
    metrics["run_id"] = run_id
    metrics["cases"] = len(cases)
    metrics["agents"] = agents
    metrics["trials_per_pair"] = trials
    metrics["isolation_requested"] = isolation
    save_metrics(conn, run_id, metrics)
    metrics_path = out_dir / run_id / "metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    conn.close()
    return metrics
