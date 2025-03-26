# Simplon Analyse Ventes

Ce projet est une application d'analyse des ventes développée dans le cadre de la formation Simplon. Il permet de télécharger des données de ventes, de produits, et de magasins à partir de fichiers CSV, de les stocker dans une base de données SQLite, et d'effectuer des analyses (chiffre d'affaires total, ventes par produit, ventes par région, quantité moyenne par produit par magasin).

## Structure du projet

- `architecture/` : Contient les fichiers png : Architecture Simplifiée - MCD avec Cardinalités (Merise) - UML Style - Système de ventes, 
- `scripts/` : Contient les fichiers Python pour le pipeline de traitement des données.
  - `main.py` : Point d'entrée principal.
  - `downloader.py` : Gestion du téléchargement des fichiers CSV.
  - `database.py` : Gestion de la base de données SQLite.
  - `analyzer.py` : Exécution des analyses.
- `data/` : Répertoire pour les fichiers CSV téléchargés (non versionné).
- `database/` : Répertoire pour la base de données SQLite (non versionné).
- `docker-compose.yml` : Configuration Docker Compose.
- `Dockerfile` : Dockerfile pour le service scripts.

## Prérequis

- Docker et Docker Compose installés.
- Python 3.9+ (si vous exécutez localement).

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/simplon_analyse_ventes.git
   cd simplon_analyse_ventes

2. Lancez les conteneurs avec Docker Compose : 
   ```bash
   docker-compose up --build

3. Vérifiez les résultats dans la base de données : 
   ```bash
   docker exec -it scripts-service sqlite3 /app/database/database.db
   SELECT * FROM resultats_analyses;
   
4. Vérifier les logs ert la description des données: 
   ```bash
   cd simplon_analyse_ventes
   docker logs scripts-service

## Fonctionnalités

- Téléchargement automatique des fichiers CSV depuis des URLs.
- Création des répertoires data et database
- Stockage des données dans une base de données SQLite.
- Analyses :
    - Chiffre d'affaires total.
    - Ventes par produit.
    - Ventes par région.
    - Quantité moyenne vendue par produit par magasin (nouvelle analyse)
- Importation des données de ventes sans doublons (uniquement les nouvelles lignes).