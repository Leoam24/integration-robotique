#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, PositionConstraint, OrientationConstraint, BoundingVolume
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class MoveItActionClient(Node):
    def __init__(self):
        super().__init__('moveit_python_client')
        # Se connecte au serveur d'action géré par le launch file de ton ami
        self._action_client = ActionClient(self, MoveGroup, 'move_action')

    def send_goal(self, x, y, z):
        self.get_logger().info('Attente de MoveIt (RViz)...')
        self._action_client.wait_for_server()

        goal_msg = MoveGroup.Goal()
        goal_msg.request.group_name = 'manipulator'
        goal_msg.request.allowed_planning_time = 5.0
        
        # Indique à MoveIt de planifier ET d'exécuter la trajectoire
        goal_msg.planning_options.plan_only = False
        
        # 1. Contrainte de Position
        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = 'base_link'
        pos_constraint.link_name = 'link_6_t'
        
        # Tolérance spatiale de la cible (un cube de 1cm)
        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.01, 0.01, 0.01]
        
        bv = BoundingVolume()
        bv.primitives.append(box)
        pose = Pose()
        pose.position.x = float(x)
        pose.position.y = float(y)
        pose.position.z = float(z)
        bv.primitive_poses.append(pose)
        
        pos_constraint.constraint_region = bv
        pos_constraint.weight = 1.0
        
        # 2. Contrainte d'Orientation (orientation neutre face à l'avant)
        ori_constraint = OrientationConstraint()
        ori_constraint.header.frame_id = 'base_link'
        ori_constraint.link_name = 'link_6_t'
        ori_constraint.orientation.w = 1.0
        ori_constraint.absolute_x_axis_tolerance = 0.1
        ori_constraint.absolute_y_axis_tolerance = 0.1
        ori_constraint.absolute_z_axis_tolerance = 0.1
        ori_constraint.weight = 1.0
        
        # Assemblage des contraintes
        constraint = Constraints()
        constraint.position_constraints.append(pos_constraint)
        constraint.orientation_constraints.append(ori_constraint)
        goal_msg.request.goal_constraints.append(constraint)

        self.get_logger().info(f'Envoi des coordonnees (X:{x}, Y:{y}, Z:{z}) a MoveIt...')
        self._action_client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    client = MoveItActionClient()
    
    # Modifie ces valeurs pour cibler d'autres coordonnées
    client.send_goal(0.5, 0.0, 0.5)
    
    rclpy.spin(client)

if __name__ == '__main__':
    main()
