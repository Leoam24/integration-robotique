from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder(
            "yaskawa_hc10",
            package_name="hc10_moveit_config",
        )
        .to_moveit_configs()
    )

    rviz_config = DeclareLaunchArgument(
        "rviz_config",
        default_value=str(
            moveit_config.package_path / "config" / "moveit.rviz"
        ),
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=[
            "-d",
            LaunchConfiguration("rviz_config"),
        ],
        parameters=[
    moveit_config.robot_description,
    moveit_config.robot_description_semantic,
    moveit_config.robot_description_kinematics,
    moveit_config.planning_pipelines,
],
    )

    return LaunchDescription([
        rviz_config,
        rviz_node,
    ])
