#!/usr/bin/env python3
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, PositionConstraint, OrientationConstraint, BoundingVolume
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class MoveItGUIClient(Node):
    def __init__(self):
        super().__init__('moveit_gui_client')
        self._action_client = ActionClient(self, MoveGroup, 'move_action')
        
    def send_goal_sync(self, x, y, z):
        if not self._action_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("Serveur MoveIt non disponible.")
            return False

        goal_msg = MoveGroup.Goal()
        goal_msg.request.group_name = 'manipulator'
        goal_msg.request.allowed_planning_time = 5.0
        goal_msg.planning_options.plan_only = False
        
        # Contrainte de position
        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = 'base_link'
        pos_constraint.link_name = 'link_6_t'
        
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
        
        # Contrainte d'orientation neutre
        ori_constraint = OrientationConstraint()
        ori_constraint.header.frame_id = 'base_link'
        ori_constraint.link_name = 'link_6_t'
        ori_constraint.orientation.w = 1.0
        ori_constraint.absolute_x_axis_tolerance = 0.1
        ori_constraint.absolute_y_axis_tolerance = 0.1
        ori_constraint.absolute_z_axis_tolerance = 0.1
        ori_constraint.weight = 1.0
        
        constraint = Constraints()
        constraint.position_constraints.append(pos_constraint)
        constraint.orientation_constraints.append(ori_constraint)
        goal_msg.request.goal_constraints.append(constraint)

        self.get_logger().info(f'Envoi de la cible (X:{x}, Y:{y}, Z:{z})...')
        
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        
        # Attente sans bloquer l'executor ROS
        while not send_goal_future.done():
            time.sleep(0.05)
            
        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Objectif rejeté par MoveIt.')
            return False

        get_result_future = goal_handle.get_result_async()
        while not get_result_future.done():
            time.sleep(0.05)
            
        result = get_result_future.result().result
        return result.error_code.val == 1

class RobotGUI:
    def __init__(self, ros_node):
        self.node = ros_node
        self.waypoints = []
        
        self.root = tk.Tk()
        self.root.title("Contrôle Yaskawa HC10 - Waypoints")
        self.root.geometry("400x480")
        
        tk.Label(self.root, text="Gestionnaire de Trajectoire", font=("Arial", 12, "bold")).pack(pady=10)
        
        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=5)
        
        tk.Label(frame_inputs, text="X:").grid(row=0, column=0, padx=2)
        self.entry_x = tk.Entry(frame_inputs, width=7)
        self.entry_x.grid(row=0, column=1, padx=5)
        self.entry_x.insert(0, "0.5")
        
        tk.Label(frame_inputs, text="Y:").grid(row=0, column=2, padx=2)
        self.entry_y = tk.Entry(frame_inputs, width=7)
        self.entry_y.grid(row=0, column=3, padx=5)
        self.entry_y.insert(0, "0.0")
        
        tk.Label(frame_inputs, text="Z:").grid(row=0, column=4, padx=2)
        self.entry_z = tk.Entry(frame_inputs, width=7)
        self.entry_z.grid(row=0, column=5, padx=5)
        self.entry_z.insert(0, "0.5")
        
        tk.Button(self.root, text="Ajouter le Waypoint", bg="#4CAF50", fg="white", command=self.add_waypoint).pack(pady=10)
        
        tk.Label(self.root, text="Séquence des points :").pack(anchor="w", padx=25)
        self.listbox = tk.Listbox(self.root, width=45, height=8)
        self.listbox.pack(padx=20, pady=5)
        
        tk.Button(self.root, text="Supprimer le point sélectionné", command=self.remove_waypoint).pack(pady=2)
        
        tk.Button(self.root, text="Lancer toute la séquence", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=self.run_sequence).pack(pady=15)
        
    def add_waypoint(self):
        try:
            x = float(self.entry_x.get())
            y = float(self.entry_y.get())
            z = float(self.entry_z.get())
            self.waypoints.append((x, y, z))
            self.listbox.insert(tk.END, f"X: {x} | Y: {y} | Z: {z}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")
            
    def remove_waypoint(self):
        selected = self.listbox.curselection()
        if selected:
            idx = selected[0]
            self.listbox.delete(idx)
            self.waypoints.pop(idx)
            
    def run_sequence(self):
        if not self.waypoints:
            messagebox.showwarning("Attention", "La liste des waypoints est vide.")
            return
        threading.Thread(target=self._execute_waypoints, daemon=True).start()
        
    def _execute_waypoints(self):
        for i, (x, y, z) in enumerate(self.waypoints):
            print(f"--- Déplacement vers le waypoint {i+1}/{len(self.waypoints)} : X={x}, Y={y}, Z={z} ---")
            success = self.node.send_goal_sync(x, y, z)
            if not success:
                print(f"Échec ou interruption au waypoint {i+1}")
                break
        print("--- Séquence de waypoints terminée ---")

def main(args=None):
    rclpy.init(args=args)
    node = MoveItGUIClient()
    
    ros_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    ros_thread.start()
    
    gui = RobotGUI(node)
    gui.root.mainloop()
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
