#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from custom_interfaces.srv import FindWall
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.action import ActionClient
from custom_interfaces.action import OdomRecord

class WallFollowing(Node):
    def __init__(self):
        super().__init__('wall_following_node')

        mutuallyexclusive_group_1 = MutuallyExclusiveCallbackGroup()
        mutuallyexclusive_group_2 = MutuallyExclusiveCallbackGroup()
        mutuallyexclusive_group_3 = MutuallyExclusiveCallbackGroup()

        self.client = self.create_client(FindWall, 'find_wall', callback_group=mutuallyexclusive_group_1)
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for find_wall service..')

        self.record_client = ActionClient(self, OdomRecord, 'record_odom', callback_group=mutuallyexclusive_group_2)
        while not self.record_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info('Waiting for record_odom action server..')

        self.subscription_laser = self.create_subscription(
            LaserScan, '/scan', self.scan_callback,
            10, callback_group=mutuallyexclusive_group_3)

        self.publisher = self.create_publisher(Twist, '/cmd_vel_safe', 10)  

        self.is_aligning = True
        self.call_find_wall_service()
        self.is_aligning = False
        self.call_record_odom_action()

    def scan_callback(self, msg):
        if self.is_aligning:
            return

        action = Twist()
        distance_to_side_wall = msg.ranges[336]   
        distance_to_front_wall = msg.ranges[0]

        if distance_to_front_wall > 0.65:       
            if distance_to_side_wall > 0.35:
                action.angular.z = -0.1
                action.linear.x = 0.1
            elif distance_to_side_wall < 0.30:
                action.angular.z = 0.1
                action.linear.x = 0.1
            else:
                action.linear.x = 0.1
                action.angular.z = 0.0
            self.publisher.publish(action)
        else:
            action.angular.z = 1.5                 
            action.linear.x = 0.1
            self.publisher.publish(action)

    def call_find_wall_service(self):
        request = FindWall.Request()
        future = self.client.call_async(request)
        while not future.done():
            rclpy.spin_once(self)
        return future.result()

    def call_record_odom_action(self):
        goal = OdomRecord.Goal()
        self.record_client.send_goal_async(goal)


def main(args=None):
    rclpy.init(args=args)
    wall_following_node = WallFollowing()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(wall_following_node)
    try:
        executor.spin()
    finally:
        wall_following_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()