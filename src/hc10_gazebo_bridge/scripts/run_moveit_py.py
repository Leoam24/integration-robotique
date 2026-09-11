#!/usr/bin/env python3
import rclpy
import rclpy.logging
from moveit.planning import MoveItPy
from geometry_msgs.msg import PoseStamped

def main():
    rclpy.init()
    logger = rclpy.logging.get_logger("moveit_py_hc10")

    # CORRECTION : Le node_name doit correspondre EXACTEMENT à celui déclaré dans le launch file
    hc10_robot = MoveItPy(node_name="moveit_py_hc10")
    hc10_arm = hc10_robot.get_planning_component("manipulator")
    logger.info("MoveItPy instance created")

    # Mettre à jour l'état actuel
    hc10_arm.set_start_state_to_current_state()

    # Définir l'objectif cartésien
    pose_goal = PoseStamped()
    pose_goal.header.frame_id = "base_link" 
    
    # Position (X, Y, Z)
    pose_goal.pose.position.x = 0.5
    pose_goal.pose.position.y = 0.0
    pose_goal.pose.position.z = 0.5
    pose_goal.pose.orientation.w = 1.0
    
    hc10_arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="link_6_t")

    # Planifier
    logger.info("Planning trajectory")
    plan_result = hc10_arm.plan()

    # Exécuter si le plan est valide
    if plan_result:
        logger.info("Executing plan")
        hc10_robot.execute(plan_result.trajectory, controllers=[])
    else:
        logger.error("Planning failed")

if __name__ == '__main__':
    main()
