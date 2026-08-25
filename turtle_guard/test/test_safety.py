# Copyright 2026 Robotics Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for the pure safety logic.  These need no ROS graph at all."""

import pytest

from turtle_guard.safety import (
    clamp,
    clamp_twist,
    is_stale,
    UnsafeLimitError,
)


def test_value_inside_limit_is_untouched():
    assert clamp(0.3, 0.5) == pytest.approx(0.3)


def test_value_above_limit_is_saturated():
    assert clamp(2.0, 0.5) == pytest.approx(0.5)


def test_negative_value_is_saturated_symmetrically():
    assert clamp(-2.0, 0.5) == pytest.approx(-0.5)


def test_zero_limit_means_full_stop():
    assert clamp(9.9, 0.0) == pytest.approx(0.0)


def test_negative_limit_is_rejected():
    with pytest.raises(UnsafeLimitError):
        clamp(0.1, -1.0)


def test_clamp_twist_limits_both_axes_independently():
    linear_x, angular_z = clamp_twist(5.0, -5.0, 0.5, 1.0)
    assert linear_x == pytest.approx(0.5)
    assert angular_z == pytest.approx(-1.0)


def test_watchdog_fires_after_timeout():
    assert is_stale(now_sec=10.0, last_msg_sec=9.0, timeout_sec=0.5)


def test_watchdog_quiet_while_commands_are_fresh():
    assert not is_stale(now_sec=10.0, last_msg_sec=9.9, timeout_sec=0.5)


def test_watchdog_disabled_by_non_positive_timeout():
    assert not is_stale(now_sec=1e6, last_msg_sec=0.0, timeout_sec=0.0)
