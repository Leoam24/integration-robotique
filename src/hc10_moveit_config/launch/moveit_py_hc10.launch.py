import os
from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("hc10", package_name="hc10_moveit_config").to_moveit_configs()

    moveit_py_yaml = os.path.join(
        get_package_share_directory('hc10_moveit_config'),
        'config',
        'moveit_py_config.yaml'
    )

    moveit_py_node = Node(
        package="hc10_gazebo_bridge",
        executable="run_moveit_py.py",
        name="moveit_py_hc10",
        parameters=[
            moveit_config.to_dict(),
            moveit_py_yaml,
            {'use_sim_time': True}
        ],
        remappings=[
            ('/joint_states', '/yaskawa_hc10_1/joint_states')
        ]
    )

    return LaunchDescription([moveit_py_node])
