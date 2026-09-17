# 🤖 Intégration ROS 2 - Bras Manipulateur Yaskawa HC10

Ce projet d'intégration a pour objectif de concevoir un pipeline complet de génération de trajectoires sans collision appliqué au bras manipulateur Yaskawa HC10. Réalisé sous la forme d'une étude de faisabilité, il démontre l'intégration d'un environnement ROS 2 pour la robotique industrielle.

## 📑 Table des matières
- [Contexte et Objectifs](#contexte-et-objectifs)
- [Architecture du Projet (Work Packages)](#architecture-du-projet)
- [Prérequis et Technologies](#prérequis-et-technologies)
- [Démonstrations Vidéos](#démonstrations-vidéos)
- [Équipe du Projet](#équipe-du-projet)

## 🎯 Contexte et Objectifs

L'objectif principal est de permettre au robot d'évoluer de manière autonome dans un espace encombré sans entrer en collision avec les éléments de sa cellule. Le système repose sur trois piliers fondamentaux :
* **Simulation et modélisation réaliste :** Déploiement d'un jumeau numérique sous Gazebo reproduisant le comportement cinématique du HC10.
* **Perception volumétrique active :** Intégration d'une caméra 3D (RGB-D) pour capturer la géométrie des obstacles et alimenter la scène en continu.
* **Planification et pilotage :** Utilisation de MoveIt 2 pour le calcul de trajectoires en temps réel et interface avec MotoROS2 pour la commande industrielle.

## 🏗️ Architecture du Projet

Le projet est divisé en 4 axes majeurs (Work Packages) :

* **WP1 | Environnement & Simulation :** Mise en place de l'environnement de simulation de la MFJA sous Ubuntu 24.04, ROS 2 Jazzy et Gazebo.
* **WP2 | Perception 3D & Vision :** Intégration d'un capteur RGB-D, traitement des nuages de points et publication des données (Octomap) décrivant l'encombrement de l'espace.
* **WP3 | Génération de trajectoires (MoveIt 2) :** Implémentation de l'API de Motion Planning de MoveIt 2 pour générer des trajectoires d'évitement d'obstacles.
* **WP4 | Contrôle industriel (MotoROS2) :** Établissement de la chaîne de communication entre ROS 2 et le contrôleur Yaskawa YRC1000 pour l'exécution des mouvements.

## 💻 Prérequis et Technologies

Pour reproduire les résultats de ce projet, l'environnement suivant est nécessaire :
* Système d'exploitation : **Ubuntu 24.04 (Noble Numbat)**.
* Middleware : **ROS 2 Jazzy**.
* Simulation : **Gazebo**.
* Planification : **MoveIt 2**.
* Contrôle Yaskawa : **MotoROS2**.

## 🎥 Démonstrations Vidéos

Voici les résultats obtenus lors de nos différentes phases de test en simulation :

### 1. Application Pick and Place
Démonstration de la séquence complète de préhension, manipulation et dépose d'un objet par le bras Yaskawa HC10.

https://github.com/user-attachments/assets/aac10849-25bc-4b47-96ef-9a31878a78d5




---

### 2. Contrôle via l'API Python MoveIt
Démonstration de la génération dynamique de trajectoires articulaires sans collision via script Python, outrepassant les contrôles manuels de RVIZ.

https://github.com/user-attachments/assets/d92ce481-725b-4ef7-9960-911568607399



---

### 3. Perception 3D et Détection d'Obstacles (Caméra RGB-D)
Démonstration de l'intégration du flux de la caméra 3D dans Gazebo et de la mise à jour dynamique de l'environnement (Planning Scene / OctoMap) lors de l'apparition d'un obstacle.

https://github.com/user-attachments/assets/74d32fe4-4c4f-41f5-a97a-7030bd452230


## 👥 Équipe du Projet

Ce projet a été réalisé en groupe avec une répartition par pôles d'expertise :
* **WP1 (Simulation) :** Niel.
* **WP2 (Vision 3D) :** Djibril, Marius.
* **WP3 (MoveIt 2) :** Léo, Imran, Niel.
* **WP4 (MotoROS2) :** Mohamed, Wassim, Wissal.
