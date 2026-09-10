# HC10 - MoveIt 2 + Gazebo

Configuration validée pour le projet d'intégration robotique Yaskawa HC10.

Environnement utilisé :

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- MoveIt 2
- Yaskawa HC10
- `mfja_3rd_floor_gz`
- branche `INTERNSHIP-ALI-2026`

## Architecture

```text
Gazebo HC10
    |
    | /yaskawa_hc10_1/joint_states
    v
MoveIt 2 + OMPL
    |
    | FollowJointTrajectory
    v
hc10_gazebo_bridge
    |
    | /yaskawa_hc10_1/joint_trajectory
    v
Gazebo HC10
```

## Packages ajoutés

### hc10_moveit_config

Configuration MoveIt 2 du Yaskawa HC10 :

- groupe de planning `manipulator`
- cinématique KDL
- planning OMPL
- limites articulaires
- géométries de collision du bras
- lecture des `joint_states` depuis Gazebo
- launch `gazebo_moveit.launch.py`

### hc10_gazebo_bridge

Bridge ROS 2 entre l'action attendue par MoveIt :

```text
/manipulator_controller/follow_joint_trajectory
```

et la commande utilisée par Gazebo :

```text
/yaskawa_hc10_1/joint_trajectory
```

Le retour d'état du robot est récupéré depuis :

```text
/yaskawa_hc10_1/joint_states
```

## Installation

### 1. Créer le workspace

```bash
mkdir -p ~/mfja_3rd_floor_ros2_ws/src
cd ~/mfja_3rd_floor_ros2_ws/src
```

### 2. Cloner la simulation

```bash
git clone -b INTERNSHIP-ALI-2026 \
https://github.com/aip-primeca-occitanie/mfja_3rd_floor_gz.git
```

### 3. Cloner le dépôt du projet

```bash
cd ~

git clone -b moveit-hc10-gazebo \
https://github.com/Leoam24/integration-robotique.git
```

### 4. Appliquer les modifications du modèle HC10

Le patch ajoute notamment les géométries de collision nécessaires à MoveIt.

```bash
cd ~/mfja_3rd_floor_ros2_ws/src/mfja_3rd_floor_gz

git apply \
~/integration-robotique/patches/mfja_3rd_floor_gz.patch
```

### 5. Copier les packages ROS 2

```bash
cp -a \
~/integration-robotique/hc10_moveit_config \
~/mfja_3rd_floor_ros2_ws/src/

cp -a \
~/integration-robotique/hc10_gazebo_bridge \
~/mfja_3rd_floor_ros2_ws/src/
```

### 6. Compiler

```bash
cd ~/mfja_3rd_floor_ros2_ws

source /opt/ros/jazzy/setup.bash

colcon build --symlink-install

source install/setup.bash
```

## Lancement

Trois terminaux sont utilisés.

### Terminal 1 - Gazebo

```bash
export LIBGL_ALWAYS_SOFTWARE=1

source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 launch mfja_3rd_floor_bringup room_315_only.launch.py \
  robots:=all \
  gui:=true \
  start_paused:=false \
  enable_room315_kinematic_shuttles:=true \
  room315_right_shuttle_count:=1 \
  room315_left_shuttle_count:=0 \
  room315_shuttles_start_enabled:=false
```

### Terminal 2 - MoveIt 2

```bash
export LIBGL_ALWAYS_SOFTWARE=1

source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 launch hc10_moveit_config gazebo_moveit.launch.py
```

### Terminal 3 - Bridge MoveIt vers Gazebo

```bash
source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 run hc10_gazebo_bridge follow_joint_trajectory_bridge
```

Le bridge doit afficher :

```text
Bridge ready: /manipulator_controller/follow_joint_trajectory -> /yaskawa_hc10_1/joint_trajectory
```

## Test dans RViz

Dans le panneau MotionPlanning :

- Planning Group : `manipulator`
- Start State : `<current>`
- Goal State : `<random valid>`

Cliquer d'abord sur :

```text
Plan
```

Puis tester :

```text
Execute
```

ou :

```text
Plan & Execute
```

Le HC10 doit bouger dans Gazebo et sa position doit être mise à jour simultanément dans RViz.

## Vérifications utiles

Vérifier les états articulaires Gazebo :

```bash
ros2 topic echo /yaskawa_hc10_1/joint_states --once
```

Vérifier l'action utilisée par MoveIt :

```bash
ros2 action list | grep follow_joint_trajectory
```

Résultat attendu :

```text
/manipulator_controller/follow_joint_trajectory
```

Vérifier le bridge :

```bash
ros2 action info /manipulator_controller/follow_joint_trajectory
```

Vérifier la chaîne TF utilisée par MoveIt :

```bash
ros2 run tf2_ros tf2_echo base_link link_6_t
```

## État actuel

Fonctionnel et validé :

- HC10 dans Gazebo
- synchronisation Gazebo / RViz
- récupération des `joint_states` Gazebo
- robot_state_publisher dédié à MoveIt
- cinématique KDL
- planning OMPL
- génération de trajectoires MoveIt
- bridge `FollowJointTrajectory`
- exécution des trajectoires dans Gazebo
- retour des positions Gazebo vers MoveIt

## Suite du projet

La prochaine étape est l'intégration de la perception 3D :

```text
Caméra RGB-D
    |
    v
PointCloud2
    |
    v
MoveIt PointCloudOctomapUpdater
    |
    v
OctoMap
    |
    v
Planning Scene
    |
    v
OMPL
    |
    v
Trajectoire évitant les obstacles
```

L'objectif final est de détecter les obstacles présents dans l'environnement simulé avec la caméra RGB-D et de les intégrer automatiquement dans la Planning Scene de MoveIt afin que le HC10 génère des trajectoires sans collision.
