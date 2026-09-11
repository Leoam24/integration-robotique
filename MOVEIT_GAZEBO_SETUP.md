# Yaskawa HC10 — MoveIt 2 + Gazebo + perception RGB-D + OctoMap

Configuration validée pour le projet d'intégration robotique autour du Yaskawa HC10.

Cette branche ajoute à l'intégration MoveIt / Gazebo :

- la perception RGB-D déjà présente dans la simulation Room 315 ;
- le bridge Gazebo → ROS 2 pour le nuage de points ;
- l'intégration du `PointCloud2` dans MoveIt ;
- la génération d'une OctoMap ;
- le self-filter du robot et de la pince ;
- la prise en compte des obstacles dans le planning OMPL ;
- l'exécution des trajectoires MoveIt dans Gazebo.

## Environnement utilisé

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- MoveIt 2
- Yaskawa HC10
- simulation `mfja_3rd_floor_gz`
- branche simulation : `INTERNSHIP-ALI-2026`
- branche de ce dépôt : `moveit-hc10-octomap`

---

# 1. Architecture

```text
Caméra RGB-D Gazebo
        |
        | gz.msgs.PointCloudPacked
        v
ros_gz_bridge
        |
        | sensor_msgs/msg/PointCloud2
        v
/room_315/perception/right_rail_rgbd/points
        |
        v
MoveIt PointCloudOctomapUpdater
        |
        v
OctoMap / Planning Scene
        |
        v
OMPL
        |
        | FollowJointTrajectory
        v
hc10_gazebo_bridge
        |
        | /yaskawa_hc10_1/joint_trajectory
        v
Gazebo HC10
```

Le retour d'état du robot est récupéré depuis :

```text
/yaskawa_hc10_1/joint_states
```

---

# 2. Caméra RGB-D

Les caméras sont déjà intégrées à la simulation Room 315.

Elles appartiennent au modèle Gazebo :

```text
room315_visual_observation_rig
```

Deux caméras RGB-D sont présentes dans la simulation :

- caméra droite ;
- caméra gauche.

Pour cette intégration MoveIt, seule la caméra droite est utilisée.

Topic PointCloud ROS 2 :

```text
/room_315/perception/right_rail_rgbd/points
```

Frame caméra :

```text
room315_right_rail_rgbd_optical_frame
```

La TF caméra est publiée depuis le launch MoveIt :

```text
world
  |
  v
room315_right_rail_rgbd_optical_frame
```

---

# 3. Packages utilisés

## `hc10_moveit_config`

Configuration MoveIt 2 du Yaskawa HC10 :

- groupe de planning `manipulator` ;
- cinématique KDL ;
- planning OMPL ;
- limites articulaires ;
- géométries de collision ;
- SRDF ;
- règles de collision internes de la pince ;
- récupération des `joint_states` Gazebo ;
- TF `world -> base_link` ;
- TF `world -> room315_right_rail_rgbd_optical_frame` ;
- `PointCloudOctomapUpdater` ;
- configuration OctoMap ;
- launch `gazebo_moveit.launch.py`.

## `hc10_gazebo_bridge`

Bridge entre l'action attendue par MoveIt :

```text
/manipulator_controller/follow_joint_trajectory
```

et le topic de commande du HC10 dans Gazebo :

```text
/yaskawa_hc10_1/joint_trajectory
```

Le bridge récupère également :

```text
/yaskawa_hc10_1/joint_states
```

afin de vérifier que Gazebo a atteint la position finale.

---

# 4. Récupération du projet

## Première installation

Créer le workspace ROS 2 :

```bash
mkdir -p ~/mfja_3rd_floor_ros2_ws/src
cd ~/mfja_3rd_floor_ros2_ws/src
```

Cloner la simulation MFJA :

```bash
git clone -b INTERNSHIP-ALI-2026 \
  https://github.com/aip-primeca-occitanie/mfja_3rd_floor_gz.git
```

Cloner ensuite le dépôt d'intégration avec la branche contenant MoveIt + OctoMap :

```bash
cd ~

git clone -b moveit-hc10-octomap \
  https://github.com/Leoam24/integration-robotique.git
```

La branche à utiliser est :

```text
moveit-hc10-octomap
```

## Si `integration-robotique` est déjà cloné

```bash
cd ~/integration-robotique

git fetch origin
git checkout moveit-hc10-octomap
git pull origin moveit-hc10-octomap
```

---

# 5. Récupérer les packages ROS 2

Les packages se trouvent dans le dépôt `integration-robotique`.

Copier `hc10_moveit_config` dans le workspace :

```bash
cp -a \
  ~/integration-robotique/hc10_moveit_config \
  ~/mfja_3rd_floor_ros2_ws/src/
```

Copier ensuite le bridge d'exécution :

```bash
cp -a \
  ~/integration-robotique/hc10_gazebo_bridge \
  ~/mfja_3rd_floor_ros2_ws/src/
```

Le workspace doit ensuite contenir :

```text
~/mfja_3rd_floor_ros2_ws/src/
├── mfja_3rd_floor_gz/
├── hc10_moveit_config/
└── hc10_gazebo_bridge/
```

---

# 6. Appliquer le patch au HC10

Le dépôt MFJA original nécessite quelques modifications pour fonctionner correctement avec MoveIt.

Le patch ajoute notamment :

- les géométries de collision du bras ;
- les géométries de collision du gripper ;
- les géométries de collision des mâchoires.

Se placer dans le dépôt MFJA :

```bash
cd ~/mfja_3rd_floor_ros2_ws/src/mfja_3rd_floor_gz
```

Vérifier que le patch peut être appliqué :

```bash
git apply --check \
  ~/integration-robotique/patches/mfja_3rd_floor_gz.patch
```

Si aucune erreur n'est affichée :

```bash
git apply \
  ~/integration-robotique/patches/mfja_3rd_floor_gz.patch
```

Ne pas appliquer plusieurs fois le patch sur le même dépôt.

---

# 7. Compiler

```bash
cd ~/mfja_3rd_floor_ros2_ws

source /opt/ros/jazzy/setup.bash

colcon build --symlink-install

source install/setup.bash
```

---

# 8. Lancement du système

Le système complet utilise quatre terminaux.

## Terminal 1 — Gazebo Room 315

Une partition Gazebo fixe est utilisée pour permettre au bridge caméra de retrouver les topics Gazebo.

```bash
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
```

`LIBGL_ALWAYS_SOFTWARE=1` est utilisé dans notre VM VMware pour garder Ogre2 et les capteurs RGB-D fonctionnels.

---

## Terminal 2 — Bridge caméra Gazebo → ROS 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

export GZ_PARTITION=room315_moveit

ros2 launch mfja_robot_control_config \
  room_315_perception_and_safety.launch.py \
  enable_camera_bridge:=true \
  enable_supervisor:=false \
  enable_dataset_recorder:=false
```

Le bridge fournit notamment :

```text
/room_315/perception/right_rail_rgbd/image
/room_315/perception/right_rail_rgbd/depth_image
/room_315/perception/right_rail_rgbd/camera_info
/room_315/perception/right_rail_rgbd/points
```

Vérification :

```bash
ros2 topic info \
  /room_315/perception/right_rail_rgbd/points \
  -v
```

Le type attendu est :

```text
sensor_msgs/msg/PointCloud2
```

---

## Terminal 3 — MoveIt + OctoMap

```bash
export LIBGL_ALWAYS_SOFTWARE=1

source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 launch hc10_moveit_config gazebo_moveit.launch.py
```

MoveIt utilise :

```text
/room_315/perception/right_rail_rgbd/points
```

avec le plugin :

```text
occupancy_map_monitor/PointCloudOctomapUpdater
```

Configuration actuelle :

```text
OctoMap frame      : world
OctoMap resolution : 0.05 m
max update rate    : 1 Hz
point subsample    : 4
```

---

## Terminal 4 — Bridge MoveIt → Gazebo

```bash
source /opt/ros/jazzy/setup.bash
source ~/mfja_3rd_floor_ros2_ws/install/setup.bash

ros2 run hc10_gazebo_bridge follow_joint_trajectory_bridge
```

Le bridge doit afficher :

```text
Bridge ready: /manipulator_controller/follow_joint_trajectory -> /yaskawa_hc10_1/joint_trajectory
```

Vérification :

```bash
ros2 action info \
  /manipulator_controller/follow_joint_trajectory
```

Un serveur d'action doit être présent.

---

# 9. Vérification de l'OctoMap

Dans RViz, l'OctoMap doit apparaître dans la Planning Scene.

Vérifier que MoveIt est abonné au PointCloud :

```bash
ros2 topic info \
  /room_315/perception/right_rail_rgbd/points \
  -v
```

Un subscriber nommé :

```text
move_group
```

doit apparaître.

Vérifier les paramètres :

```bash
ros2 param get /move_group octomap_frame
ros2 param get /move_group octomap_resolution
```

Résultat attendu :

```text
String value is: world
Double value is: 0.05
```

Pour vider l'OctoMap :

```bash
ros2 service call \
  /clear_octomap \
  std_srvs/srv/Empty \
  "{}"
```

Si le bridge caméra reste actif, la carte est automatiquement reconstruite.

---

# 10. Test dans RViz

Dans le panneau `MotionPlanning` :

```text
Planning Group : manipulator
Start State    : <current>
```

Choisir ensuite une cible valide.

Pour les tests, utiliser de préférence :

```text
Plan & Execute
```

Cela évite qu'une différence apparaisse entre la position utilisée pour le planning et la position réelle au moment de l'exécution.

Le HC10 doit :

1. générer une trajectoire avec OMPL ;
2. vérifier la trajectoire vis-à-vis de l'OctoMap ;
3. envoyer la trajectoire au bridge ;
4. exécuter le mouvement dans Gazebo ;
5. mettre à jour sa position dans RViz.

---

# 11. Self-filter du robot

La caméra RGB-D voit également le HC10.

MoveIt utilise les géométries de collision pour retirer le robot du nuage de points avant l'insertion dans l'OctoMap.

Les collisions ont été ajoutées pour :

```text
base_link
link_1_s
link_2_l
link_3_u
link_4_r
link_5_b
link_6_t
gripper
gripper_left_jaw
gripper_right_jaw
```

Sans les collisions de la pince, celle-ci était détectée par la caméra et apparaissait dans l'OctoMap comme un obstacle.

Le SRDF autorise les contacts mécaniques normaux suivants :

```text
gripper <-> gripper_left_jaw
gripper <-> gripper_right_jaw
gripper_left_jaw <-> gripper_right_jaw
```

---

# 12. Vérifier une configuration

Exemple avec la position `home` :

```bash
ros2 service call \
  /check_state_validity \
  moveit_msgs/srv/GetStateValidity \
  "{
    robot_state: {
      joint_state: {
        name: [
          'joint_1_s',
          'joint_2_l',
          'joint_3_u',
          'joint_4_r',
          'joint_5_b',
          'joint_6_t'
        ],
        position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
      }
    },
    group_name: 'manipulator'
  }"
```

Résultat attendu :

```text
valid=True
contacts=[]
```

---

# 13. Commandes utiles

États articulaires :

```bash
ros2 topic echo \
  /yaskawa_hc10_1/joint_states \
  --once
```

Action utilisée par MoveIt :

```bash
ros2 action list | grep follow_joint_trajectory
```

TF robot :

```bash
ros2 run tf2_ros tf2_echo \
  world base_link
```

TF caméra :

```bash
ros2 run tf2_ros tf2_echo \
  world room315_right_rail_rgbd_optical_frame
```

PointCloud :

```bash
ros2 topic info \
  /room_315/perception/right_rail_rgbd/points \
  -v
```

---

# 14. État actuel

Fonctionnel et testé :

- HC10 dans Gazebo ;
- MoveIt 2 ;
- cinématique KDL ;
- OMPL ;
- synchronisation Gazebo / RViz ;
- récupération des `joint_states` ;
- génération de trajectoires ;
- exécution MoveIt → Gazebo ;
- caméra RGB-D Room 315 ;
- bridge Gazebo → ROS 2 ;
- PointCloud2 ;
- TF caméra ;
- `PointCloudOctomapUpdater` ;
- génération dynamique de l'OctoMap ;
- self-filter du bras ;
- self-filter de la pince ;
- détection des collisions robot / OctoMap ;
- planning et exécution avec perception active ;
- retour vers la position `home`.

---

# 15. Remarque sur l'OctoMap dynamique

L'OctoMap est mise à jour en permanence lorsque le bridge caméra fonctionne.

Il est possible qu'OMPL trouve une trajectoire, puis que `ValidateSolution` la refuse si l'OctoMap est modifiée entre le calcul et la validation.

Exemple :

```text
Computed path is not valid.
Found a contact between '<octomap>' and 'link_2_l'
```

Pour diagnostiquer ce comportement, il est possible de stopper temporairement le bridge caméra.

Dans ce cas, ne pas appeler `/clear_octomap` : la carte reste présente mais n'est plus mise à jour.

Cela permet de tester une trajectoire avec une OctoMap figée.

---

# 16. Résumé

```text
Terminal 1
Gazebo Room 315
        |
Terminal 2
Bridge RGB-D Gazebo -> ROS 2
        |
Terminal 3
MoveIt + OctoMap
        |
Terminal 4
Bridge MoveIt -> Gazebo
```

Le système permet maintenant à MoveIt d'utiliser le nuage de points produit par la caméra RGB-D simulée afin d'intégrer l'environnement dans sa Planning Scene et de tenir compte des obstacles lors du planning du Yaskawa HC10.
