# Projet d'Intégration Robotique : Yaskawa HC10 & ROS 2

Dépôt officiel du projet de groupe pour l'intégration de ROS 2 avec le bras manipulateur Yaskawa HC10 (Étude de faisabilité - UPSSITECH SRI).

## Documentation Officielle
- [Sujet officiel du projet (Google Doc)](https://docs.google.com/document/d/1znpp6cdlQR97A_atjmb55jRE1lBgRqDBimBcdWyu_ww/edit?tab=t.0#heading=h.9zo5dtp9fi5d) 

---

## Répartition des Rôles (Équipe)
- **Simulation (ROS 2 / Gazebo)** : Niel
- **Intégration de capteurs (Caméra RGB-D)** : Djibril et Marius
- **Génération de trajectoire (MoveIt 2)** : Léo et Imran
- **Contrôle & MotoROS2** : Mohamed et Wassim

---

## 1. Environnement de Simulation & Prérequis
- **OS** : Ubuntu 24.04.4 (Noble Numbat)
  - *Configuration VM recommandée* : 50 Go min. (Disque), 8 Go min. (RAM), 4 cœurs min. (Processeur), Accélération 3D cochée, Mémoire graphique au maximum.
- **Middleware** : [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/Installation/Alternatives/Ubuntu-Development-Setup.html)
- **Référence Simulation** : [mfja_3rd_floor_gz (INTERNSHIP-ALI-2026)](https://github.com/aip-primeca-occitanie/mfja_3rd_floor_gz/tree/INTERNSHIP-ALI-2026) 

---

## Étapes du Projet

### 1. Mise en place de l'environnement de simulation
- Installation de ROS 2 Jazzy et Gazebo sur Ubuntu 24.04.4.
- Prise en main et configuration de l'environnement fourni.
- Vérification du bon fonctionnement du robot et de sa scène simulée .

### 2. Perception 3D de l'environnement
- Intégration d'une caméra RGB-D dans la simulation pour détecter la position, dimensions (longueur, largeur, hauteur) et orientation des obstacles.
- Référence outil : [ros2_rgbd_mapping](https://github.com/yangyonggit/ros2_rgbd_mapping) (odométrie visuelle, fusion volumétrique, grille d'occupation 2D).

### 3. Traitement des données capteur par ROS 2
- Récupération et traitement des flux de la caméra 3D par les nœuds ROS 2 pour alimenter la carte d'occupation.

### 4. Motion Planning avec MoveIt 2
- Installation et configuration de MoveIt 2 à l'aide du *Setup Assistant*.
- Génération et exécution de trajectoires sans collisions pour le bras manipulateur.
- Utilisation de l'API MoveIt 2 (C++/Python) .
- **Références** : 
  - [Documentation MoveIt 2](https://moveit.picknik.ai/main/index.html) 
  - [Setup Assistant Tutorial](https://moveit.picknik.ai/main/doc/examples/setup_assistant/setup_assistant_tutorial.html) 

### 5. Contrôle du Yaskawa HC10 via MotoROS2
- Prise en main de MotoROS2 et de son architecture.
- Établissement de la communication entre ROS 2 et le contrôleur réel/simulé du Yaskawa HC10 .
- Vérification de l'envoi effectif des commandes de mouvement.
- **Références** :
  - [MotoROS2](https://github.com/yaskawa-global/motoros2) 
  - [ros_yaskawa_hc10](https://github.com/aip-primeca-occitanie/ros_yaskawa_hc10) 

---

## 📚 Ressources & Documentation Utiles
- **Projets / Starters similaires** :
  - [YaskawaEurope/ros2-starter-for-yaskawa-robots](https://github.com/YaskawaEurope/ros2-starter-for-yaskawa-robots) 
  - [Démonstration Vidéo YouTube](https://youtu.be/-TZbwtD8xG0?t=382) 
- **Documentation Matériel (Yaskawa HC10)** :
  - Flyer & Fiches techniques HC10 / HC10DT
