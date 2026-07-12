#!/usr/bin/env python3
"""Deterministic security-phase gate for local pushes and CI."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def run(name: str, command: list[str], timeout: int) -> bool:
    print(f"\n▶ {name}")
    completed = subprocess.run(command, cwd=ROOT, timeout=timeout, check=False)
    print("  ✅ passed" if completed.returncode == 0 else f"  ❌ failed ({completed.returncode})")
    return completed.returncode == 0


def main() -> int:
    checks = [
        run("Identity and MFA security tests", [sys.executable, "-m", "pytest", "tests/test_identity.py", "-q"], 120),
        run("Traffic and upload security tests", [sys.executable, "-m", "pytest", "tests/test_security_controls.py", "-q"], 120),
        run("Compliance control evidence", [sys.executable, "scripts/security/generate_control_evidence.py"], 60),
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
