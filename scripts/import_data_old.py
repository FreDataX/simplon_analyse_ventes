import requests
import pandas as pd
import sqlite3
import os

urls = {
    "ventes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=760830694&single=true&output=csv",
    "produits": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=0&single=true&output=csv",
    "magasins": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=714623615&single=true&output=csv",
}

for nom, url in urls.items():
    r = requests.get(url)
    with open(f"data/{nom}.csv", "wb") as f:
        f.write(r.content)

    df = pd.read_csv(f"data/{nom}.csv")
    print(df.head(), df.info())


# Import des données
conn = sqlite3.connect('/app/database/database.db')
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS produits (
    id TEXT PRIMARY KEY,  
    nom TEXT NOT NULL,
    prix REAL NOT NULL,
    stock INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS magasins (
    id INTEGER PRIMARY KEY,
    ville TEXT NOT NULL,
    nombre_salaries INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ventes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Clé primaire auto-incrémentée pour identifier chaque vente
    date TEXT NOT NULL,  -- Correspond à "Date"
    produit_id TEXT NOT NULL,  -- Correspond à "ID Référence produit"
    magasin_id INTEGER NOT NULL,  -- Correspond à "ID Magasin"
    quantite INTEGER NOT NULL,  -- Correspond à "Quantité"
    FOREIGN KEY (produit_id) REFERENCES produits(id),
    FOREIGN KEY (magasin_id) REFERENCES magasins(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS resultats_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_analyse TEXT,
    valeur TEXT
)
''')

conn.commit()

# Produits
produits_df = pd.read_csv('/app/data/produits.csv')
# Produits : Renommer les colonnes avant l'import
produits_df = produits_df.rename(columns={
    'ID Référence produit': 'id',
    'Nom': 'nom',
    'Prix': 'prix',
    'Stock': 'stock'
})
produits_df.to_sql('produits', conn, if_exists='replace', index=False)

# Magasins : Renommer les colonnes avant l'import
magasins_df = pd.read_csv('/app/data/magasins.csv')
magasins_df = magasins_df.rename(columns={
    'ID Magasin': 'id',
    'Ville': 'ville',
    'Nombre de salariés': 'nombre_salaries'
})
magasins_df.to_sql('magasins', conn, if_exists='replace', index=False)

# Ventes : Renommer les colonnes avant l'import
ventes_df = pd.read_csv('/app/data/ventes.csv')
ventes_df = ventes_df.rename(columns={
    'Date': 'date',
    'ID Référence produit': 'produit_id',
    'Quantité': 'quantite',
    'ID Magasin': 'magasin_id'
})
for _, row in ventes_df.iterrows():
    cursor.execute('''
    INSERT INTO ventes (date, produit_id, magasin_id, quantite)
    VALUES (?, ?, ?, ?)
    ''', (row['date'], row['produit_id'], row['magasin_id'], row['quantite']))
    conn.commit()
    
    
# Chiffre d'affaires total
cursor.execute('''
SELECT SUM(v.quantite * p.prix) AS total
FROM ventes v
JOIN produits p ON v.produit_id = p.id
''')
total_ca = cursor.fetchone()[0]
cursor.execute('INSERT INTO resultats_analyses (type_analyse, valeur) VALUES (?, ?)', 
               ('chiffre_affaires_total', str(total_ca)))

# Ventes par produit
cursor.execute('''
SELECT p.nom, SUM(v.quantite) AS quantite_totale
FROM ventes v
JOIN produits p ON v.produit_id = p.id
GROUP BY p.nom
''')
for row in cursor.fetchall():
    cursor.execute('INSERT INTO resultats_analyses (type_analyse, valeur) VALUES (?, ?)', 
                   ('ventes_par_produit', f'{row[0]}: {row[1]}'))

# Ventes par région
cursor.execute('''
SELECT m.ville, SUM(v.quantite * p.prix) AS total
FROM ventes v
JOIN magasins m ON v.magasin_id = m.id
JOIN produits p ON v.produit_id = p.id
GROUP BY m.ville
''')
for row in cursor.fetchall():
    cursor.execute('INSERT INTO resultats_analyses (type_analyse, valeur) VALUES (?, ?)', 
                   ('ventes_par_region', f'{row[0]}: {row[1]}'))

conn.commit()
conn.close()
