from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    
    pkg_share = get_package_share_directory('alfredr1')
    
    urdf_file = os.path.join(pkg_share,'urdf','R1.urdf')
    rviz_file = os.path.join(pkg_share,'rviz2','rviz2.rviz')
    
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
        
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),        
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d',rviz_file],
            output = 'screen',
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            output="screen"
        ),
        
        
    ])