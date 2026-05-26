#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from custom_interfaces.action import OdomRecord
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
import time
import math


class OdomRecorder(Node):
    def __init__(self):
        super().__init__('odom_recorder_server')

        self.callback_group = ReentrantCallbackGroup()

        self.odom_subscriber = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10,
            callback_group=self.callback_group)

        self.action_server = ActionServer(
            self, OdomRecord, 'record_odom',
            self.record_odom_callback,
            callback_group=self.callback_group)

        self.last_odom = Point()
        self.first_odom = Point()
        self.odom_record = []
        self.total_distance = 0.0
        self.last_x = 0.0
        self.last_y = 0.0

    def odom_callback(self, msg):
        self.last_odom.x = msg.pose.pose.position.x
        self.last_odom.y = msg.pose.pose.position.y
        o = msg.pose.pose.orientation
        siny_cosp = 2.0 * (o.w * o.z + o.x * o.y)
        cosy_cosp = 1.0 - 2.0 * (o.y * o.y + o.z * o.z)
        self.last_odom.z = math.atan2(siny_cosp, cosy_cosp)

    def record_odom_callback(self, goal_handle):
        self.first_odom.x = self.last_odom.x
        self.first_odom.y = self.last_odom.y
        self.first_odom.z = self.last_odom.z
        self.last_x = self.last_odom.x
        self.last_y = self.last_odom.y
        self.total_distance = 0.0
        self.odom_record = []

        has_moved_away = False

        while True:
            time.sleep(1)

            # record current position
            point = Point()
            point.x = self.last_odom.x
            point.y = self.last_odom.y
            point.z = self.last_odom.z
            self.odom_record.append(point)

            # calculate distance from last position
            current_total = math.hypot(
                self.last_odom.x - self.last_x,
                self.last_odom.y - self.last_y)
            self.total_distance += current_total

            # update last position
            self.last_x = self.last_odom.x
            self.last_y = self.last_odom.y

            # send feedback
            feedback = OdomRecord.Feedback()
            feedback.current_total = self.total_distance
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(f'Total distance: {self.total_distance:.2f}m')

            # check if robot has moved away from start
            dist_from_start = math.hypot(
                self.last_odom.x - self.first_odom.x,
                self.last_odom.y - self.first_odom.y)
            
            if not has_moved_away:
                if dist_from_start > 0.5:
                    has_moved_away = True
                    

            # check if lap complete
            if has_moved_away and dist_from_start < 0.1:
                self.get_logger().info('Lap complete!')
                break

        goal_handle.succeed()
        result = OdomRecord.Result()
        result.list_of_odoms = self.odom_record
        return result


def main(args=None):
    rclpy.init(args=args)
    odom_recorder = OdomRecorder()
    executor = MultiThreadedExecutor()
    executor.add_node(odom_recorder)
    try:
        executor.spin()
    finally:
        odom_recorder.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()