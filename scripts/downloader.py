# scripts/downloader.py
import os
from typing import Dict

import pandas as pd
import requests
from skimpy import skim

class Downloader:
    """Classe pour gérer le téléchargement des fichiers CSV à partir d'URLs."""

    def __init__(self, urls: Dict[str, str], download_dir: str = "/app/data") -> None:
        """
        Initialise le Downloader avec les URLs des fichiers CSV et le répertoire de téléchargement.

        Args:
            urls: Dictionnaire des URLs {nom: url}.
            download_dir: Répertoire où stocker les fichiers téléchargés.
        """
        self.urls: Dict[str, str] = urls
        self.download_dir: str = download_dir
        # Créer le répertoire de téléchargement s'il n'existe pas
        os.makedirs(self.download_dir, exist_ok=True)

    def download_files(self) -> None:
        """
        Télécharge les fichiers CSV à partir des URLs et les enregistre dans download_dir.
        Affiche également un aperçu des données avec pandas et skim.
        """
        for nom, url in self.urls.items():
            file_path: str = os.path.join(self.download_dir, f"{nom}.csv")
            print(f"Téléchargement de {nom} depuis {url}...")
            response: requests.Response = requests.get(url)
            with open(file_path, "wb") as file:
                file.write(response.content)

            # Afficher un aperçu des données
            dataframe: pd.DataFrame = pd.read_csv(file_path)
            print(f"\nAperçu de {nom}.csv :")
            print(dataframe.head())
            print(dataframe.info())
            print(skim(dataframe))
            