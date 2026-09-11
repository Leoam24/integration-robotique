# Yaskawa HC10 — Contrôle par API Python & Waypoints (MoveIt 2 + Gazebo)

Guide d'utilisation et d'installation pour le pilotage du Yaskawa HC10 via une interface graphique Python personnalisée et des waypoints cartésiens, s'appuyant sur la simulation Room 315.

---

## 1. Ce qui a été ajouté / Votre travail

Cette configuration intègre :
- Une **interface graphique Python (Tkinter)** (`gui_waypoints.py`) permettant de saisir des coordonnées cartésiennes (`X, Y, Z`) dynamiquement.
- Un gestionnaire de **waypoints séquentiels** pour enchaîner plusieurs positions cibles de l'effecteur terminal (`link_6_t`).
- Un client d'action ROS 2 (`MoveGroup`) communiquant directement avec le serveur MoveIt de la simulation sans passer par la manipulation manuelle dans RViz.

---

## 2. Architecture de contrôle

```text
Interface Graphique Python (Tkinter)
        |
        | Saisie (X, Y, Z) & Séquence de waypoints
        v
Script Python (gui_waypoints.py)
        |
        | Action Client (move_action / MoveGroup)
        v
MoveIt 2 / move_group (Planificateur OMPL + Cinématique KDL)
        |
        | FollowJointTrajectory
        v
hc10_gazebo_bridge
        |
        | /yaskawa_hc10_1/joint_trajectory
        v
Gazebo (Yaskawa HC10)

3. Lancement du système (4 Terminaux requis)

Pour que l'API Python puisse envoyer ses trajectoires, l'environnement de simulation complet doit être actif. Ouvrez 4 terminaux distincts et lancez les services dans cet ordre :
Terminal 1 — Gazebo Room 315

export LIBGL_ALWAYS_SOFTWARE=1
source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 launch mfja_3rd_floor_bringup room_315_only.launch.py \
  gz_partition:=room315_moveit \
  robots:=all \
  gui:=true \
  start_paused:=false \
  enable_room315_kinematic_shuttles:=true \
  room315_right_shuttle_count:=1 \
  room315_left_shuttle_count:=0 \
  room315_shuttles_start_enabled:=false


Termial 2 
export LIBGL_ALWAYS_SOFTWARE=1
source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 launch hc10_moveit_config gazebo_moveit.launch.py

Termianl 3 
source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 run hc10_gazebo_bridge follow_joint_trajectory_bridge

Terminal 4
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash
~/mfja_3rd_floor_ros2_ws/src/hc10_gazebo_bridge/scripts/gui_waypoints.py


Utilisation de l'interface :

    Entrez les coordonnées cibles de l'effecteur (X, Y, Z) dans les champs dédiés (ex: X: 0.5, Y: 0.0, Z: 0.5). Évitez 0,0,0 (centre de la base) ou des valeurs trop extrêmes comme 1.0 de partout pour éviter les erreurs de singularité ou de portée.

    Cliquez sur Ajouter le Waypoint pour empiler le point dans la liste de la séquence.

    Répétez l'opération si vous souhaitez faire enchaîner plusieurs positions au robot.

    Cliquez sur Lancer toute la séquence : le script exécutera les mouvements un par un de manière automatisée dans Gazebo.