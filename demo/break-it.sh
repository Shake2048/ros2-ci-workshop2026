#!/usr/bin/env bash
# Introduce a realistic bug so CI can catch it in front of the room.
#
#   ./demo/break-it.sh            # subtle logic bug (tests catch it)
#   ./demo/break-it.sh lint       # style violation  (linters catch it)
#
# Then:  git checkout -b fix/reverse-limit && git commit -am "..." && git push
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-logic}"

case "$MODE" in
  logic)
    # Drop the lower bound. Forward speed is still limited, so it looks fine in
    # a quick manual test -- but the robot can now reverse at unlimited speed.
    python3 - <<'PY'
from pathlib import Path
p = Path('turtle_guard/turtle_guard/safety.py')
s = p.read_text()
old = '    return max(-limit, min(limit, value))'
new = '    return min(limit, value)'
assert old in s, 'safety.py is not in its pristine state -- run ./demo/fix-it.sh first'
p.write_text(s.replace(old, new))
PY
    echo "Broken: clamp() no longer limits reverse speed."
    echo "Expect test_negative_value_is_saturated_symmetrically to fail."
    ;;

  lint)
    python3 - <<'PY'
from pathlib import Path
p = Path('turtle_guard/turtle_guard/safety.py')
s = p.read_text()
old = 'def is_stale(now_sec: float, last_msg_sec: float, timeout_sec: float) -> bool:'
new = ('def is_stale( now_sec: float,last_msg_sec: float,timeout_sec: float )'
       ' -> bool :   # this signature is deliberately misspaced and far, far'
       ' too long to pass the linter')
assert old in s, 'safety.py is not in its pristine state -- run ./demo/fix-it.sh first'
p.write_text(s.replace(old, new))
PY
    echo "Broken: whitespace and line-length violations added."
    echo "Expect the ament_flake8 job to fail in about 40 seconds."
    ;;

  *)
    echo "usage: $0 [logic|lint]" >&2
    exit 2
    ;;
esac

git --no-pager diff --stat
