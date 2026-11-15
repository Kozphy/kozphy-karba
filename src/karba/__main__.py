from __future__ import annotations

import argparse
import json
from pathlib import Path

from karba.dashboard import serve
from karba.engine import evaluate_campaign
from karba.reproducibility import (
    compare_attempt_sets,
    load_attempts_from_run,
    write_reproducibility_report,
)
from karba.store import connect, list_attempts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="karba")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_eval = sub.add_parser("evaluate", help="Run controlled evaluation campaign")
    p_eval.add_argument("--cases", type=Path, default=Path("benchmarks/cases"))
    p_eval.add_argument("--out", type=Path, default=Path("evidence"))
    p_eval.add_argument("--db", type=Path, default=Path("evidence/karba.sqlite"))
    p_eval.add_argument("--trials", type=int, default=1)
    p_eval.add_argument(
        "--agents",
        default="oracle,buggy,malicious,timeout",
        help="Comma-separated agent ids (includes aider-mock, openhands-mock)",
    )
    p_eval.add_argument("--run-id", default=None)
    p_eval.add_argument(
        "--isolation",
        choices=["auto", "host", "container"],
        default="auto",
        help="Verify isolation: container uses Docker network=none",
    )
    p_eval.add_argument(
        "--approval-token",
        type=Path,
        default=None,
        help="Human approval token file (required for *-live adapters; still no merge authority)",
    )
    p_eval.add_argument(
        "--compare-to",
        default=None,
        help="Baseline run_id for reproducibility delta after this campaign",
    )

    p_repro = sub.add_parser("reproduce", help="Compare two runs for paired outcome stability")
    p_repro.add_argument("--baseline", required=True)
    p_repro.add_argument("--candidate", required=True)
    p_repro.add_argument("--out", type=Path, default=Path("evidence"))
    p_repro.add_argument("--db", type=Path, default=Path("evidence/karba.sqlite"))

    p_dash = sub.add_parser("dashboard", help="Serve local dashboard")
    p_dash.add_argument("--metrics", type=Path, required=True)
    p_dash.add_argument("--port", type=int, default=8787)

    args = parser.parse_args(argv)

    if args.cmd == "evaluate":
        agents = [a.strip() for a in args.agents.split(",") if a.strip()]
        metrics = evaluate_campaign(
            cases_root=args.cases,
            agents=agents,
            trials=args.trials,
            out_dir=args.out,
            db_path=args.db,
            run_id=args.run_id,
            isolation=args.isolation,
            approval_token_path=args.approval_token,
        )
        if args.compare_to:
            conn = connect(args.db)
            baseline = list_attempts(conn, args.compare_to)
            candidate = list_attempts(conn, metrics["run_id"])
            if not baseline:
                baseline = load_attempts_from_run(args.out, args.compare_to)
            if not candidate:
                candidate = load_attempts_from_run(args.out, metrics["run_id"])
            comparison = compare_attempt_sets(baseline, candidate)
            metrics["reproducibility_vs"] = args.compare_to
            metrics["evaluation_reproducibility"] = comparison["evaluation_reproducibility"]
            metrics["reproducibility_wilson_95"] = comparison["reproducibility_wilson_95"]
            metrics["reproducibility_mismatches"] = comparison["mismatched_outcomes"]
            report = args.out / metrics["run_id"] / "reproducibility.json"
            write_reproducibility_report(
                baseline_run=args.compare_to,
                candidate_run=metrics["run_id"],
                comparison=comparison,
                out_path=report,
            )
            (args.out / metrics["run_id"] / "metrics.json").write_text(
                json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
            )
            conn.close()
        print(json.dumps(metrics, indent=2))
        return 0

    if args.cmd == "reproduce":
        conn = connect(args.db)
        baseline = list_attempts(conn, args.baseline) or load_attempts_from_run(args.out, args.baseline)
        candidate = list_attempts(conn, args.candidate) or load_attempts_from_run(
            args.out, args.candidate
        )
        comparison = compare_attempt_sets(baseline, candidate)
        out_path = args.out / f"repro-{args.baseline}-vs-{args.candidate}.json"
        write_reproducibility_report(
            baseline_run=args.baseline,
            candidate_run=args.candidate,
            comparison=comparison,
            out_path=out_path,
        )
        print(json.dumps(comparison, indent=2))
        conn.close()
        return 0

    if args.cmd == "dashboard":
        serve(args.metrics, port=args.port)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
