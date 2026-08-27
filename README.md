# turtle_guard — GitHub Actions CI/CD for ROS 2

Demo repository for a 45-minute workshop. It is a deliberately tiny ROS 2 package
(a velocity limiter) wrapped in three progressively more realistic GitHub Actions
workflows.

## What's in here

```
turtle_guard/                  the ROS 2 package (ament_python)
  turtle_guard/safety.py       pure logic — no ROS imports, so it is cheap to test
  turtle_guard/velocity_guard_node.py   thin rclpy wrapper around safety.py
  test/test_safety.py          9 unit tests, run by plain pytest
  test/test_{flake8,pep257,copyright}.py   the standard ament linters
.github/workflows/
  01-hello-ci.yml              event → workflow → job → step, nothing else
  02-ros2-build-test.yml       rosdep + colcon build + colcon test in a container
  03-ros2-ci-full.yml          parallel lint, distro matrix, artifacts, concurrency
demo/break-it.sh               introduce a bug on purpose, live
demo/fix-it.sh                 put it back
```

## The one design idea worth stealing

All the decision-making lives in `safety.py`, which imports nothing from ROS.
The node is a thin shell that moves data in and out of it. That split is what
makes CI possible on a free runner: no DDS, no simulator, no GPU, no hardware —
just `pytest`. Integration tests against a real graph still belong on a machine
in the lab, but they should not be the *only* tests you have.

## Running it locally

```bash
# in a ROS 2 Jazzy environment
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths . --ignore-src -y
colcon build --packages-select turtle_guard
source install/setup.bash           # <- puts turtle_guard on PYTHONPATH for colcon-pytest
colcon test --packages-select turtle_guard --event-handlers console_direct+
colcon test-result --verbose        # <- this is the line that reports failures
```

Or without ROS at all, since the logic is pure Python:

```bash
cd turtle_guard && python3 -m pytest test/test_safety.py -v
```

## Running the node

```bash
source install/setup.bash
ros2 run turtle_guard velocity_guard --ros-args -p linear_limit:=0.5
# in another terminal
ros2 topic pub /cmd_vel_raw geometry_msgs/msg/Twist '{linear: {x: 9.0}}'
ros2 topic echo /cmd_vel            # x is 0.5, not 9.0
```

## Workshop flow

1. Push anything → watch `01-hello-ci.yml` run. Read the log. That's CI.
2. Enable `02` → open a PR → watch build+test gate the merge.
3. `./demo/break-it.sh` → commit → push → watch it go red, read the failure.
4. `./demo/fix-it.sh` → push → green.
5. Look at `03` and talk about what you'd add next.

## Notes on versions (August 2026)

- `ubuntu-latest` runners are Ubuntu 24.04.
- ROS 2 Jazzy Jalisco is the LTS most labs are on (supported to May 2029).
  Kilted Kaiju goes EOL December 2026; Lyrical Luth (May 2026) is the newest LTS.
- `actions/checkout@v7` is current; v7 tightened `pull_request_target` defaults.
- The official `ros:<distro>-ros-base` images already contain colcon and rosdep.
- Inside a `container:`, set `defaults: {run: {shell: bash}}`. GitHub's default shell is
  `bash -e {0}` but falls back to `sh` when bash is not on the container's PATH, and
  `source` is a bashism — the symptom is `setup.bash: 1: source: not found`. The POSIX
  alternative is `. /opt/ros/<distro>/setup.sh`.
- `turtle_guard/setup.py` must declare `tests_require=['pytest']`. Without it, `colcon test`
  falls back to Python's unittest runner, which ignores plain `def test_*()` functions.
  Python 3.12 (Ubuntu 24.04) changed unittest to exit with code 5 and print "NO TESTS RAN"
  in this case — the failure is obvious once you know what to look for.
- `source install/setup.bash` before `colcon test` is not optional: `colcon-pytest` spawns
  pytest as a subprocess that inherits the parent shell's `PYTHONPATH`. Without sourcing the
  install space first, the subprocess cannot import the package and collects zero tests.
- `ros-tooling/action-ros-ci` is a batteries-included alternative to writing the
  colcon steps by hand — worth knowing about, but the explicit version above is
  better for learning what is actually happening.
# workshop 14:54 
