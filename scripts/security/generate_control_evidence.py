#!/usr/bin/env python3
"""Generate non-secret, machine-readable security control evidence."""

from datetime import UTC, datetime
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def command(*args: str) -> dict[str, object]:
    completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False)
    return {"command": " ".join(args), "passed": completed.returncode == 0, "output": completed.stdout.strip()[-2000:]}


def main() -> int:
    evidence = {
        "generated_at": datetime.now(UTC).isoformat(),
        "commit": command("git", "rev-parse", "HEAD"),
        "worktree": command("git", "status", "--short"),
        "tracked_artifacts": command("git", "ls-files", ".env", ".env.*", "*.db", "*.log", "*.zip"),
        "security_files": {
            path: (ROOT / path).exists()
            for path in [
                "api/security/http_security.py",
                "api/security/upload_security.py",
                "api/security/mfa.py",
                ".github/workflows/security_gate.yml",
                ".github/workflows/codeql.yml",
                "compliance/control_matrix.md",
            ]
        },
        "disclaimer": "Repository evidence only; this is not SOC 2 or ISO certification.",
    }
    print(json.dumps(evidence, indent=2))
    return 0 if all(evidence["security_files"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
