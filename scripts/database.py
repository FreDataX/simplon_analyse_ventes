# scripts/database.py
import os
from typing import Any

import pandas as pd
import sqlite3


class DatabaseManager:
    """Classe pour gérer la base de données SQLite (création des tables, import des données)."""

    def __init__(self, db_path: str = "/app/database/database.db") -> None:
        """
        Initialise le DatabaseManager avec le chemin de la base de données SQLite.

        Args:
            db_path: Chemin vers le fichier database.db.
        """
        self.db_path: str = db_path
        # Créer le répertoire de la base de données s'il n'existe pas
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(self.db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()

    def create_tables(self) -> None:
        """Crée les tables SQLite nécessaires pour le projet."""
        # Table des produits
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            prix REAL NOT NULL,
            stock INTEGER
        )
        ''')

        # Table des magasins
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS magasins (
            id INTEGER PRIMARY KEY,
            ville TEXT NOT NULL,
            nombre_salaries INTEGER
        )
        ''')

        # Table des ventes
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            produit_id TEXT NOT NULL,
            magasin_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            UNIQUE(date, produit_id, magasin_id, quantite),
            FOREIGN KEY (produit_id) REFERENCES produits(id),
            FOREIGN KEY (magasin_id) REFERENCES magasins(id)
        )
        ''')

        # Table pour les résultats des analyses
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultats_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_analyse TEXT NOT NULL,
            valeur TEXT NOT NULL
        )
        ''')

        self.conn.commit()

    def import_data(self, data_dir: str = "/app/data") -> None:
        """
        Importe les données des fichiers CSV dans la base de données SQLite.

        Args:
            data_dir: Répertoire contenant les fichiers CSV.
        """
        # Produits
        produits_df: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'produits.csv'))
        produits_df = produits_df.rename(columns={
            'ID Référence produit': 'id',
            'Nom': 'nom',
            'Prix': 'prix',
            'Stock': 'stock'
        })
        produits_df.to_sql('produits', self.conn, if_exists='replace', index=False)

        # Magasins
        magasins_df: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'magasins.csv'))
        magasins_df = magasins_df.rename(columns={
            'ID Magasin': 'id',
            'Ville': 'ville',
            'Nombre de salariés': 'nombre_salaries'
        })
        magasins_df.to_sql('magasins', self.conn, if_exists='replace', index=False)

        # Ventes : Importer uniquement les nouvelles données
        ventes_df: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'ventes.csv'))
        ventes_df = ventes_df.rename(columns={
            'Date': 'date',
            'ID Référence produit': 'produit_id',
            'Quantité': 'quantite',
            'ID Magasin': 'magasin_id'
        })

        # Insérer les lignes avec INSERT OR IGNORE pour éviter les doublons
        for _, row in ventes_df.iterrows():
            self.cursor.execute('''
            INSERT OR IGNORE INTO ventes (date, produit_id, magasin_id, quantite)
            VALUES (?, ?, ?, ?)
            ''', (row['date'], row['produit_id'], row['magasin_id'], row['quantite']))
        self.conn.commit()

    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        self.conn.close()