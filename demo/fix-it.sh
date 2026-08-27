#!/usr/bin/env bash
# Undo whatever break-it.sh did, so the demo is repeatable.
#
# `git checkout -- safety.py` is NOT enough: by the time CI has gone red, the
# break is already a commit, so checkout just restores the broken HEAD. Instead
# rewrite the two lines break-it.sh touches back to their pristine form. This is
# idempotent and works whether the break was committed or not.
#
# Leaves the fix UNSTAGED, exactly like break-it.sh -- then:
#   git commit -am "fix: restore symmetric clamp" && git push
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
from pathlib import Path

p = Path('turtle_guard/turtle_guard/safety.py')
s = p.read_text()
before = s

# logic bug: restore the symmetric lower bound
s = s.replace(
    '    return min(limit, value)\n',
    '    return max(-limit, min(limit, value))\n',
)

# lint bug: restore the well-formed signature
s = s.replace(
    ('def is_stale( now_sec: float,last_msg_sec: float,timeout_sec: float )'
     ' -> bool :   # this signature is deliberately misspaced and far, far'
     ' too long to pass the linter'),
    'def is_stale(now_sec: float, last_msg_sec: float, timeout_sec: float) -> bool:',
)

if s == before:
    print("safety.py already pristine -- nothing to fix.")
else:
    p.write_text(s)
    print("safety.py restored.")
PY

echo "Now: git commit -am 'fix: restore symmetric clamp' && git push"
git --no-pager diff --stat
