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

"""
A thin ROS 2 node that saturates incoming velocity commands.

Subscribes to ``cmd_vel_raw`` and republishes a safe command on ``cmd_vel``.
All of the interesting logic lives in :mod:`turtle_guard.safety` so that CI can
test it without spinning up a ROS graph.
"""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node

from turtle_guard.safety import clamp_twist, is_stale


class VelocityGuard(Node):
    """Republish ``cmd_vel_raw`` as ``cmd_vel``, saturated and watchdogged."""

    def __init__(self):
        super().__init__('velocity_guard')
        self.declare_parameter('linear_limit', 0.5)
        self.declare_parameter('angular_limit', 1.0)
        self.declare_parameter('timeout_sec', 0.5)

        self._last_msg_sec = self._now()
        self._publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self._subscription = self.create_subscription(
            Twist, 'cmd_vel_raw', self._on_cmd, 10)
        self._timer = self.create_timer(0.1, self._on_watchdog)
        self.get_logger().info('velocity_guard is up')

    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _on_cmd(self, msg):
        self._last_msg_sec = self._now()
        linear_limit = self.get_parameter('linear_limit').value
        angular_limit = self.get_parameter('angular_limit').value

        linear_x, angular_z = clamp_twist(
            msg.linear.x, msg.angular.z, linear_limit, angular_limit)

        out = Twist()
        out.linear.x = linear_x
        out.angular.z = angular_z
        self._publisher.publish(out)

    def _on_watchdog(self):
        timeout_sec = self.get_parameter('timeout_sec').value
        if is_stale(self._now(), self._last_msg_sec, timeout_sec):
            self._publisher.publish(Twist())


def main(args=None):
    """Spin the guard node until interrupted."""
    rclpy.init(args=args)
    node = VelocityGuard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
