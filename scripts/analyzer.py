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
        self._analyze_total_revenue()

        # Ventes par produit
        self._analyze_sales_by_product()

        # Ventes par région
        self._analyze_sales_by_region()

        # Nouvelle analyse : Quantité moyenne vendue par produit par magasin
        self._analyze_avg_quantity_by_product_and_store()

        self.db_manager.conn.commit()

    def _analyze_total_revenue(self) -> None:
        """Calcule le chiffre d'affaires total et stocke le résultat."""
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

    def _analyze_sales_by_product(self) -> None:
        """Calcule les ventes totales par produit et stocke les résultats."""
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

    def _analyze_sales_by_region(self) -> None:
        """Calcule les ventes totales par région et stocke les résultats."""
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

    def _analyze_avg_quantity_by_product_and_store(self) -> None:
        """
        Calcule la quantité moyenne vendue par produit par magasin et stocke les résultats.
        """
        self.cursor.execute('''
        SELECT p.nom, m.ville, AVG(v.quantite) AS quantite_moyenne
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        JOIN magasins m ON v.magasin_id = m.id
        GROUP BY p.nom, m.ville
        ''')
        for row in self.cursor.fetchall():
            nom_produit: str
            ville: str
            quantite_moyenne: float
            nom_produit, ville, quantite_moyenne = row
            self.cursor.execute(
                'INSERT INTO resultats_analyses (type_analyse, valeur) VALUES (?, ?)',
                ('quantite_moyenne_par_produit_par_magasin', f'{nom_produit} - {ville}: {quantite_moyenne}')
            )