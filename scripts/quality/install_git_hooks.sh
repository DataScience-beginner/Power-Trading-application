#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
git -C "$ROOT" config core.hooksPath .githooks
echo "Configured .githooks as the repository hook path."
echo "Every local push will run the standard Testing QA Agent gate."
