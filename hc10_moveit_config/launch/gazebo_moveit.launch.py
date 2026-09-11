import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    moveit_config = (
    MoveItConfigsBuilder(
        "yaskawa_hc10",
        package_name="hc10_moveit_config",
    )
    .planning_scene_monitor(
        publish_robot_description=True,
        publish_robot_description_semantic=True,
    )
    .sensors_3d(
        file_path="config/sensors_3d.yaml"
    )
    .to_moveit_configs()
)

    # MoveIt utilise directement les joint_states du robot Gazebo
    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": True},
        ],
        remappings=[
            ("joint_states", "/yaskawa_hc10_1/joint_states"),
        ],
    )

    # Génère un arbre TF NON préfixé pour MoveIt :
    # base_link -> link_1_s -> ... -> tool0
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="hc10_moveit_robot_state_publisher",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            {"use_sim_time": True},
        ],
        remappings=[
            ("joint_states", "/yaskawa_hc10_1/joint_states"),
        ],
    )

    # Position du HC10 dans la salle 315
    world_to_robot = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="hc10_world_tf",
        output="screen",
        arguments=[
            "--x", "-15.1622",
            "--y", "-3.0",
            "--z", "0.62",
            "--yaw", "1.57",
            "--frame-id", "world",
            "--child-frame-id", "base_link",
    ],
    )

    world_to_camera = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="room315_right_rgbd_tf",
        output="screen",
        arguments=[
            "--x", "-14.559",
            "--y", "-3.465",
            "--z", "4.50",
            "--roll", "0",
            "--pitch", "1.5708",
            "--yaw", "0",
            "--frame-id", "world",
            "--child-frame-id",
            "room315_right_rail_rgbd_optical_frame",
        ],
    )

    rviz_config = os.path.join(
        get_package_share_directory("hc10_moveit_config"),
        "config",
        "moveit.rviz",
    )

    # On conserve exactement la configuration RViz qui fonctionne maintenant.
    # Surtout pas joint_limits ici : on avait le conflit de type.
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription([
        world_to_robot,
    world_to_camera,
        robot_state_publisher,
        move_group,
        rviz,
    ])
