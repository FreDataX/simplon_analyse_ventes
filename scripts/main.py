# scripts/main.py
from typing import Dict

from analyzer import Analyzer
from database import DatabaseManager
from downloader import Downloader


# URLs des fichiers
urls: Dict[str, str] = {
    "ventes": (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/"
        "pub?gid=760830694&single=true&output=csv"
    ),
    "produits": (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/"
        "pub?gid=0&single=true&output=csv"
    ),
    "magasins": (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/"
        "pub?gid=714623615&single=true&output=csv"
    ),
}


def main() -> None:
    """
    Point d'entrée principal pour exécuter le pipeline de traitement des données.
    """
    # Étape 1 : Télécharger les fichiers CSV
    downloader: Downloader = Downloader(urls, download_dir="/app/data")
    downloader.download_files()

    # Étape 2 : Gérer la base de données (création des tables et import des données)
    db_manager: DatabaseManager = DatabaseManager(db_path="/app/database/database.db")
    db_manager.create_tables()
    db_manager.import_data(data_dir="/app/data")

    # Étape 3 : Exécuter les analyses
    analyzer: Analyzer = Analyzer(db_manager)
    analyzer.analyze()

    # Étape 4 : Fermer la connexion à la base de données
    db_manager.close()


if __name__ == "__main__":
    main()