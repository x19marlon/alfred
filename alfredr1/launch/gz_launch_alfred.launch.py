import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable,
                            IncludeLaunchDescription, SetLaunchConfiguration)
from launch.conditions import IfCondition
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from nav2_common.launch import ReplaceString

ARGUMENTS = [
    DeclareLaunchArgument('world_name', default_value='world_r1.sdf', description='Name of the world to load. Match with map if using Nav2.'),
    DeclareLaunchArgument('ros_bridge', default_value='True', description='Run ROS bridge node.'),
    DeclareLaunchArgument('initial_pose_x', default_value='0.0', description='Initial x pose of rasbot in the simulation.'),
    DeclareLaunchArgument('initial_pose_y', default_value='0.0', description='Initial y pose of rasbot in the simulation.'),
    DeclareLaunchArgument('initial_pose_z', default_value='1', description='Initial z pose of rasbot in the simulation.'),
    DeclareLaunchArgument('initial_pose_yaw', default_value='0.0', description='Initial yaw pose of rasbot in the simulation.'),
    DeclareLaunchArgument('robot_description_topic', default_value='robot_description', description='Robot description topic.'),
    DeclareLaunchArgument('rsp_frequency', default_value='30.0', description='Robot State Publisher frequency.'),
    DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (Gazebo) clock if true'),
    DeclareLaunchArgument('entity', default_value='FIAR_bot', description='Name of the robot'),
    DeclareLaunchArgument('robot_description_topic', default_value='robot_description', description='Robot description topic.'),
]

def get_robot_description():
    #Take package direction
    pkg_fiar_gazebo = get_package_share_directory('alfredr1')
    #Take xacro direction
    robot_description = os.path.join(pkg_fiar_gazebo, 'urdf', 'R1.urdf')

    
    
    #chage relative route to definitive route
    with open(robot_description, 'r') as file:
        robot_desc = file.read()
    
    return robot_desc

def generate_launch_description():
    #generate lauch description
    ld = LaunchDescription(ARGUMENTS)
    #take gazebo package direction
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    #take package direction
    pkg_rasbot_gazebo = get_package_share_directory('alfredr1')
    #take gazebo lauch direction
    gz_launch_path = PathJoinSubstitution([pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])
    #take wolrd name from arguments
    world_name = LaunchConfiguration('world_name')
    #take bridge name form arguments
    ros_bridge = LaunchConfiguration('ros_bridge')
    #take worlds direction
    world_path = PathJoinSubstitution([pkg_rasbot_gazebo,'worlds',world_name])
    #take bridges direction
    #bridge_config_file_path = os.path.join(pkg_rasbot_gazebo, 'config', 'bridge_config.yaml')

    #lauch gazebo
    ld.add_action(
            SetEnvironmentVariable(
                name='GZ_SIM_RESOURCE_PATH',
                value=os.path.dirname(pkg_rasbot_gazebo)
            )
        )
    
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                'gz_args': [world_path], 
                'on_exit_shutdown': 'True'
            }.items(),
        ),
    )
    #lauch bridge node and sincronize ros2 clock and gz clock
    ld.add_action(
        Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
                output='screen',
                condition=IfCondition(ros_bridge),
            ),
    )

    #take arguments from the lauch
    use_sim_time = LaunchConfiguration('use_sim_time')
    rsp_frequency = LaunchConfiguration('rsp_frequency')

    #lauch robot_state_publisher and sends with parameter the clock synchronization and robot description
    ld.add_action(
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='both',
            parameters=[
                {
                    'use_sim_time': use_sim_time,
                    'publish_frequency':  rsp_frequency,
                    'robot_description': get_robot_description(),
                }
            ],
            remappings=[
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static'),
            ],
        )
    )
    #take arguments from the lauch
    entity = LaunchConfiguration('entity')
    initial_pose_x = LaunchConfiguration('initial_pose_x')
    initial_pose_y = LaunchConfiguration('initial_pose_y')
    initial_pose_z = LaunchConfiguration('initial_pose_z')
    initial_pose_yaw = LaunchConfiguration('initial_pose_yaw')
    robot_description_topic = LaunchConfiguration('robot_description_topic')

    #generate and create my robot in the gazebo world
    ld.add_action(
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', entity,
                '-topic', robot_description_topic,
                '-x', initial_pose_x,
                '-y', initial_pose_y,
                '-z', initial_pose_z,
                '-R', '0',
                '-P', '0',
                '-Y', initial_pose_yaw,
            ],
            output='screen',
        )
    )
    # bridge_config = ReplaceString(
    #     source_file=bridge_config_file_path,
    #     replacements={'<entity>': entity},
    # )

    # ld.add_action(
    #     Node(
    #         package='ros_gz_bridge',
    #         executable='parameter_bridge',
    #         output='screen',
    #         parameters=[{
    #             'config_file': bridge_config
    #         }],
    #     )
    # )

    # ld.add_action(
    #     Node(
    #         package='rviz2',
    #         executable='rviz2',
    #         arguments=['-d', os.path.join(pkg_rasbot_gazebo, 'rviz', 'robot_config.rviz')],
    #         parameters=[{'use_sim_time': True}],
    #         remappings=[
    #             ('/tf', 'tf'),
    #             ('/tf_static', 'tf_static'),
    #         ],
    #     ),
    # )
    return ld