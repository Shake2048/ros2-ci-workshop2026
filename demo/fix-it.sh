#!/usr/bin/env bash
# Undo whatever break-it.sh did, so the demo is repeatable.
set -euo pipefail
cd "$(dirname "$0")/.."
git checkout -- turtle_guard/turtle_guard/safety.py
echo "safety.py restored. CI should go green again on the next push."
