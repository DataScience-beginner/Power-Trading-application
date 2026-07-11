#!/usr/bin/env python3
"""
Golden automated test runner for the Power Trading application.

Usage:
    python scripts/quality/golden_test.py --mode smoke
    python scripts/quality/golden_test.py --mode standard
    python scripts/quality/golden_test.py --mode rigorous

This runner is intentionally conservative:
- no production writes;
- no unbounded API startup;
- no dependency on local SQLite data as production truth.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class CheckResult:
    name: str
    passed: bool
    skipped: bool = False
    details: str = ""


def run_command(
    name: str,
    command: Sequence[str],
    *,
    cwd: Path = ROOT,
    timeout: int = 120,
    env: dict[str, str] | None = None,
) -> CheckResult:
    print(f"\n▶ {name}")
    print("  " + " ".join(command))

    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd),
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"  ❌ timed out after {timeout}s")
        return CheckResult(name=name, passed=False, details=f"Timed out after {timeout}s")

    if completed.stdout.strip():
        print(completed.stdout.rstrip())

    if completed.returncode == 0:
        print("  ✅ passed")
        return CheckResult(name=name, passed=True)

    print(f"  ❌ failed with exit code {completed.returncode}")
    return CheckResult(
        name=name,
        passed=False,
        details=f"Exit code {completed.returncode}",
    )


def check_git_artifact_hygiene() -> CheckResult:
    print("\n▶ Git artifact hygiene")
    forbidden_suffixes = (".db", ".pid", ".zip", ".log")
    forbidden_segments = ("/node_modules/", "/dist/", "/__pycache__/", "/.pytest_cache/")
    forbidden_env_names = {".env", ".env.railway", ".env.local", ".env.production"}

    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
        check=False,
    )

    if completed.returncode != 0:
        print(completed.stdout.rstrip())
        return CheckResult("Git artifact hygiene", False, details="git ls-files failed")

    offenders: list[str] = []
    for file_name in completed.stdout.splitlines():
        path = "/" + file_name
        base = Path(file_name).name
        if base in forbidden_env_names:
            offenders.append(file_name)
        elif file_name.endswith(forbidden_suffixes):
            offenders.append(file_name)
        elif any(segment in path for segment in forbidden_segments):
            offenders.append(file_name)

    if offenders:
        print("  ❌ forbidden tracked files:")
        for offender in offenders:
            print(f"  - {offender}")
        return CheckResult("Git artifact hygiene", False, details=f"{len(offenders)} offenders")

    print("  ✅ passed")
    return CheckResult("Git artifact hygiene", True)


def run_smoke() -> list[CheckResult]:
    return [
        check_git_artifact_hygiene(),
        run_command(
            "Python compile",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "api",
                "database",
                "parsers",
                "backend",
                "scripts",
                "tests",
            ],
            timeout=120,
        ),
        run_command(
            "Golden static contracts",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests/golden"],
            timeout=60,
        ),
    ]


def run_frontend_build() -> CheckResult:
    package_json = ROOT / "frontend-react" / "package.json"
    node_modules = ROOT / "frontend-react" / "node_modules"

    if not package_json.exists():
        print("\n▶ Frontend build")
        print("  ⚠ skipped: frontend-react/package.json not found")
        return CheckResult("Frontend build", True, skipped=True, details="package.json missing")

    if not node_modules.exists():
        print("\n▶ Frontend build")
        print("  ⚠ skipped: frontend-react/node_modules missing; run npm install first")
        return CheckResult("Frontend build", True, skipped=True, details="node_modules missing")

    return run_command(
        "Frontend build",
        ["npm", "run", "build"],
        cwd=ROOT / "frontend-react",
        timeout=180,
    )


def run_standard() -> list[CheckResult]:
    return run_smoke() + [run_frontend_build()]


def run_rigorous() -> list[CheckResult]:
    results = run_standard()

    # Historical tests are not yet normalized, but when pytest is installed this
    # lets the QA agent expose failures explicitly during rigorous checks.
    try:
        import pytest  # noqa: F401
    except Exception:
        print("\n▶ Full pytest suite")
        print("  ❌ pytest is not installed; add/install test dependencies before rigorous gate")
        results.append(
            CheckResult(
                "Full pytest suite",
                False,
                details="pytest missing",
            )
        )
    else:
        results.append(
            run_command(
                "Full pytest suite",
                [sys.executable, "-m", "pytest", "tests", "-q"],
                timeout=300,
            )
        )

    return results


def summarize(mode: str, results: list[CheckResult]) -> int:
    print("\n" + "=" * 80)
    print(f"Golden test summary: {mode}")
    print("=" * 80)

    failed = [result for result in results if not result.passed]
    skipped = [result for result in results if result.skipped]

    for result in results:
        if result.passed and result.skipped:
            status = "SKIP"
        elif result.passed:
            status = "PASS"
        else:
            status = "FAIL"
        detail = f" - {result.details}" if result.details else ""
        print(f"{status:4} {result.name}{detail}")

    if skipped:
        print("\nSkipped checks are allowed only when the missing dependency is outside the change scope.")

    if failed:
        print("\n❌ Golden gate failed. Do not commit/push until this is resolved or explicitly accepted.")
        return 1

    print("\n✅ Golden gate passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Power Trading golden test gate.")
    parser.add_argument(
        "--mode",
        choices=["smoke", "standard", "rigorous"],
        default="standard",
        help="Test depth to run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.mode == "smoke":
        results = run_smoke()
    elif args.mode == "standard":
        results = run_standard()
    else:
        results = run_rigorous()

    return summarize(args.mode, results)


if __name__ == "__main__":
    raise SystemExit(main())

