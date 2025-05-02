import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
import launch_ros

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

import xacro

def generate_launch_description():

    # Check if we're told to use sim time
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Process the URDF file
    pkg_path = os.path.join(get_package_share_directory('race_it'))
    xacro_file = os.path.join(pkg_path, 'description', 'race_car.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # Path to the controllers YAML file
    controllers_yaml = os.path.join(pkg_path, 'config', 'my_controllers.yaml')
    
    # Controller Manager Node
    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[robot_description, controllers_yaml, {'use_sim_time': use_sim_time}],
        output='screen',
    )

    # Nodes
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_path, 'config/rviz/urdf_config.rviz')],
    )

    # Spawn both controllers
    spawn_ackermann = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["asc", "jsc"],
        output="screen",
        # Wait 10 seconds for controller_manager
        parameters=[{'startup_delay': 10.0}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false', description='Use sim time'),
        ros2_control_node,
        node_robot_state_publisher,
        joint_state_publisher_node,
        rviz_node,
        spawn_ackermann,
    ])