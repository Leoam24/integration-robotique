import time
import threading

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory
from sensor_msgs.msg import JointState


class FollowJointTrajectoryBridge(Node):

    def __init__(self):
        super().__init__('hc10_follow_joint_trajectory_bridge')

        self.callback_group = ReentrantCallbackGroup()

        self.expected_joints = [
            'joint_1_s',
            'joint_2_l',
            'joint_3_u',
            'joint_4_r',
            'joint_5_b',
            'joint_6_t',
        ]

        self.current_positions = {}
        self.lock = threading.Lock()

        self.trajectory_pub = self.create_publisher(
            JointTrajectory,
            '/yaskawa_hc10_1/joint_trajectory',
            10,
        )

        self.joint_state_sub = self.create_subscription(
            JointState,
            '/yaskawa_hc10_1/joint_states',
            self.joint_state_callback,
            20,
            callback_group=self.callback_group,
        )

        self.action_server = ActionServer(
            self,
            FollowJointTrajectory,
            '/manipulator_controller/follow_joint_trajectory',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group,
        )

        self.get_logger().info(
            'Bridge ready: '
            '/manipulator_controller/follow_joint_trajectory '
            '-> /yaskawa_hc10_1/joint_trajectory'
        )

    def joint_state_callback(self, msg):
        with self.lock:
            for name, position in zip(msg.name, msg.position):
                self.current_positions[name] = position

    def goal_callback(self, goal_request):
        names = goal_request.trajectory.joint_names

        if not names:
            self.get_logger().error('Rejected trajectory: no joints')
            return GoalResponse.REJECT

        if set(names) != set(self.expected_joints):
            self.get_logger().error(
                f'Rejected joints: {names}'
            )
            return GoalResponse.REJECT

        if not goal_request.trajectory.points:
            self.get_logger().error('Rejected trajectory: no points')
            return GoalResponse.REJECT

        self.get_logger().info(
            f'Accepted trajectory with '
            f'{len(goal_request.trajectory.points)} points'
        )

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().warn('Trajectory cancellation requested')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        trajectory = goal_handle.request.trajectory

        # Transmettre directement la trajectoire calculée par MoveIt à Gazebo
        self.trajectory_pub.publish(trajectory)

        self.get_logger().info(
            f'Published trajectory to Gazebo '
            f'({len(trajectory.points)} points)'
        )

        last_point = trajectory.points[-1]

        final_positions = dict(
            zip(trajectory.joint_names, last_point.positions)
        )

        duration = (
            last_point.time_from_start.sec
            + last_point.time_from_start.nanosec * 1e-9
        )

        timeout = max(duration + 5.0, 8.0)
        tolerance = 0.02

        start = time.monotonic()

        result = FollowJointTrajectory.Result()

        while rclpy.ok():

            if goal_handle.is_cancel_requested:
                goal_handle.canceled()

                result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
                result.error_string = 'Goal canceled'

                return result

            with self.lock:
                available = all(
                    joint in self.current_positions
                    for joint in final_positions
                )

                if available:
                    reached = all(
                        abs(
                            self.current_positions[joint]
                            - target
                        ) < tolerance
                        for joint, target in final_positions.items()
                    )
                else:
                    reached = False

            if reached:
                goal_handle.succeed()

                result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
                result.error_string = ''

                self.get_logger().info(
                    'Gazebo reached final trajectory state'
                )

                return result

            if time.monotonic() - start > timeout:
                goal_handle.abort()

                result.error_code = (
                    FollowJointTrajectory.Result.GOAL_TOLERANCE_VIOLATED
                )
                result.error_string = (
                    'Gazebo did not reach final position before timeout'
                )

                self.get_logger().error(result.error_string)

                return result

            time.sleep(0.05)


def main(args=None):
    rclpy.init(args=args)

    node = FollowJointTrajectoryBridge()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass

    executor.shutdown()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
