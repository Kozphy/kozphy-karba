"""Docker-isolated verification (network=none). Inspired by harness collector; lives only in KARBA."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

IMAGE = "kozphy-karba-verifier:py312"
DOCKER_DIR = Path(__file__).resolve().parents[2] / "docker"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    proc = _run(["docker", "info"])
    return proc.returncode == 0


def image_fingerprint() -> str:
    h = hashlib.sha256()
    for name in ("Dockerfile", "run_verify_in_container.py"):
        h.update((DOCKER_DIR / name).read_bytes())
    h.update(b"karba-docker-verify-v1")
    return h.hexdigest()


def ensure_image(*, rebuild: bool = False) -> str:
    inspect = _run(["docker", "image", "inspect", IMAGE])
    if inspect.returncode == 0 and not rebuild:
        return IMAGE
    proc = _run(
        ["docker", "build", "-t", IMAGE, "-f", str(DOCKER_DIR / "Dockerfile"), str(DOCKER_DIR)]
    )
    if proc.returncode != 0:
        raise RuntimeError(f"docker build failed:\n{proc.stdout}\n{proc.stderr}")
    return IMAGE


def run_verify_container(workspace: Path) -> dict:
    """Run ruff+pytest(+hidden) in container. Returns parsed result + metadata."""
    ensure_image()
    workspace = workspace.resolve()
    with tempfile.TemporaryDirectory(prefix="karba-dout-") as tmp:
        out = Path(tmp)
        cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "128",
            "--memory",
            "512m",
            "--cpus",
            "1",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "-v",
            f"{workspace}:/work:rw",
            "-v",
            f"{out.resolve()}:/out:rw",
            "-w",
            "/work",
            IMAGE,
        ]
        proc = _run(cmd)
        result_path = out / "result.json"
        if not result_path.is_file():
            raise RuntimeError(
                f"container produced no result.json exit={proc.returncode}\n"
                f"stdout={proc.stdout}\nstderr={proc.stderr}"
            )
        data = json.loads(result_path.read_text(encoding="utf-8"))
        data["_docker_exit"] = proc.returncode
        data["_image"] = IMAGE
        data["_image_fingerprint"] = image_fingerprint()
        data["_network"] = "none"
        return data
