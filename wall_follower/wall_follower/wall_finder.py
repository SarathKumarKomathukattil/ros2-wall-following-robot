#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from custom_interfaces.srv import FindWall
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.executors import MultiThreadedExecutor
import time
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup


class WallFinderServiceServer(Node):
    def __init__(self):
        super().__init__('wall_finder_service_server')

        self.mutuallyexclusive_group_1 = MutuallyExclusiveCallbackGroup()
        self.mutuallyexclusive_group_2 = MutuallyExclusiveCallbackGroup()

        self.srv = self.create_service(
            FindWall, 'find_wall', self.find_wall_callback,
            callback_group=self.mutuallyexclusive_group_2)

        self.subscription_laser = self.create_subscription(
            LaserScan, '/scan', self.scan_callback,
            10, callback_group=self.mutuallyexclusive_group_1)

        self.publisher = self.create_publisher(Twist, '/cmd_vel_safe', 10)
        self.laser_msg = None

    def scan_callback(self, msg):
        self.laser_msg = msg

    def get_front(self):
        front_rays = list(self.laser_msg.ranges[0:5]) + list(self.laser_msg.ranges[445:])
        valid = [r for r in front_rays if not math.isinf(r) and r > 0.1]
        if not valid:
            return 999.0
        return sum(valid) / len(valid)

    def find_wall_callback(self, request, response):
        action = Twist()

        while self.laser_msg is None:
            pass

        # filter invalid readings
        valid_ranges = [r for r in self.laser_msg.ranges
                        if not math.isinf(r) and r > 0.15]
        initial_min_distance = min(valid_ranges)

        # Step 1 - rotate to face wall
        while self.get_front() > initial_min_distance + 0.1:
            action.angular.z = 0.3
            self.publisher.publish(action)
            time.sleep(0.1)

        action.angular.z = 0.0
        self.publisher.publish(action)

        # Step 2 - move forward
        while self.get_front() > 0.4:
            action.linear.x = 0.1
            self.publisher.publish(action)
            time.sleep(0.1)

        action.linear.x = 0.0
        self.publisher.publish(action)
        time.sleep(0.5)

        # Step 3 - rotate until wall on right
        while self.laser_msg.ranges[336] > 0.35:
            action.angular.z = 0.3
            self.publisher.publish(action)
            time.sleep(0.1)

        action.angular.z = 0.0
        self.publisher.publish(action)
        time.sleep(0.5)

        response.wallfound = True
        return response


def main(args=None):
    rclpy.init(args=args)
    wall_finder_node = WallFinderServiceServer()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(wall_finder_node)
    try:
        executor.spin()
    finally:
        wall_finder_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()