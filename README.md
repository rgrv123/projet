# Projet de Fin d'Année BTS CIEL - Système de Poubelles Urbaines Connectées

## 📖 Présentation du Projet
Dans le cadre de la modernisation et de l'optimisation de la gestion des déchets, ce projet propose la mise en place d'un **système de poubelles urbaines connectées**. L'objectif est d'améliorer l'efficacité des collectes, de réduire les coûts et de promouvoir un environnement plus propre.  

---

## 🚀 Objectifs
1. **Optimisation des collectes de déchets** grâce à des capteurs et à une infrastructure connectée.
2. **Réduction des coûts** via une planification intelligente des tournées de collecte.
3. **Préservation de l’environnement** en diminuant les débordements et en surveillant les risques tels que les incendies.

---

## 🛠️ Répartition des Tâches et Contributions

### **Étudiant 1 : Acquisition de Données**
- Développement des systèmes de mesure via des capteurs :
  - Niveau de remplissage
  - Poids des déchets
  - Température (prévention des incendies)
- Interface avec le Raspberry Pi pour la récupération des données des capteurs.
- Mise en place de la connexion **LoRa** entre le Raspberry Pi et le serveur du quartier.
- **Livrables** :
  - Code pour l'acquisition des données.
  - Configuration des capteurs et du Raspberry Pi.
  - Documentation technique détaillée.

---

### **Étudiant 2 : Infrastructure Réseau**
- Mise en place de la connexion **LoRa** entre :
  - Raspberry Pi ↔ Serveur quartier
  - Serveur quartier ↔ Serveur central
- Configuration des serveurs pour assurer une communication fiable et sécurisée.
- Conception d'une base de données sécurisée pour le stockage des données IoT.
- **Livrables** :
  - Infrastructure réseau opérationnelle.
  - Documentation réseau et base de données.

---

### **Étudiant 3 : Développement de l'Interface Web**
- Développement d'une interface web pour le suivi des données en temps réel :
  - Visualisation des données collectées par capteurs.
  - Génération d'alertes basées sur des seuils prédéfinis.
- **Livrables** :
  - Interface web fonctionnelle et responsive.
  - Documentation utilisateur et guide d'installation.

---

### **Étudiant 4 : Organisation de la Collecte**
- Développement d'un système pour organiser les tournées de collecte :
  - Récupération et stockage des données de localisation des conteneurs (id, coordonnées GPS, adresse postale).
  - Gestion des tournées à partir des données collectées.
- Mise en œuvre du serveur et de la base de données associés.
- **Livrables** :
  - Système de gestion des collectes.
  - Documentation technique.

---

## ⚙️ Technologies Utilisées

### Langages
- **HTML, CSS, JavaScript** : Pour le développement de l'interface web.
- **Python** : Pour le traitement des données et la gestion des capteurs.
- **MySQL** : Pour la gestion de la base de données sécurisée.

### Frameworks et Bibliothèques
- **Tailwind CSS** : Framework CSS pour des interfaces rapides et modernes.
- **Notie** : Librairie JavaScript pour des notifications interactives.
- **Leaflet** : Librairie JavaScript pour la gestion et la visualisation de cartes.

### Communication IoT
- **LoRa** : Technologie pour la communication longue distance entre les capteurs et les serveurs.

---

## 📄 Documentation
Chaque partie du projet est accompagnée de sa propre documentation :
- **Installation et configuration des capteurs et serveurs.**
- **Utilisation de l'interface web.**
- **Explication des tournées.**

---

## ✨ Auteurs
- **Étudiant 1** : Acquisition de données.
- **Étudiant 2** : Infrastructure réseau.
- **Étudiant 3** : Développement de l'interface web.
- **Étudiant 4** : Organisation de la collecte.
