# scripts/analyzer.py
from typing import Any, Tuple

from database import DatabaseManager


class Analyzer:
    """Classe pour exécuter les analyses et stocker les résultats dans la base de données."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialise l'Analyzer avec un DatabaseManager pour accéder à la base de données.

        Args:
            db_manager: Instance de DatabaseManager.
        """
        self.db_manager: DatabaseManager = db_manager
        self.cursor: Any = self.db_manager.cursor  # sqlite3.Cursor n'a pas de type officiel

    def analyze(self) -> None:
        """
        Exécute les analyses et stocke les résultats dans la table resultats_analyses.
        """
        self.cursor.execute('DELETE FROM resultats_analyses')
        self.db_manager.conn.commit()
        
        # Chiffre d'affaires total
        self.cursor.execute('''
        SELECT SUM(v.quantite * p.prix) AS total
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        ''')
        total_ca: float = self.cursor.fetchone()[0]
        self.cursor.execute(
            'INSERT INTO resultats_analyses (type_analyse, valeur) VALUES (?, ?)',
            ('chiffre_affaires_total', str(total_ca))
        )

        # Ventes par produit
        self.cursor.execute('''
        SELECT p.nom, SUM(v.quantite) AS quantite_totale
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        GROUP BY p.nom
        ''')
        for row in self.cursor.fetchall():
            nom_produit: str
            quantite_totale: int
            nom_produit, quantite_totale = row
            self.cursor.execute(
                'INSERT INTO resultats_analyses (type_analyse, valeur) VALUES (?, ?)',
                ('ventes_par_produit', f'{nom_produit}: {quantite_totale}')
            )

        # Ventes par région
        self.cursor.execute('''
        SELECT m.ville, SUM(v.quantite * p.prix) AS total
        FROM ventes v
        JOIN magasins m ON v.magasin_id = m.id
        JOIN produits p ON v.produit_id = p.id
        GROUP BY m.ville
        ''')
        for row in self.cursor.fetchall():
            ville: str
            total: float
            ville, total = row
            self.cursor.execute(
                'INSERT INTO resultats_analyses (type_analyse, valeur) VALUES (?, ?)',
                ('ventes_par_region', f'{ville}: {total}')
            )

        self.db_manager.conn.commit()