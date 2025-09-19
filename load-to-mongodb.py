#!/usr/bin/env python3
"""
Script pour charger les résultats Spark dans MongoDB
"""

import pandas as pd
import pymongo
from pymongo import MongoClient
import os
import glob

def load_csv_from_hdfs(csv_path):
    """Charge un fichier CSV depuis HDFS via Docker"""
    try:
        # Copier le fichier depuis HDFS vers le conteneur
        os.system(f"docker exec namenode hdfs dfs -get {csv_path}/* /tmp/")
        
        # Trouver le fichier CSV généré dans le conteneur
        result = os.popen("docker exec namenode find /tmp -name 'part-*.csv' | head -1").read().strip()
        
        if not result:
            print(f"❌ Aucun fichier CSV trouvé dans {csv_path}")
            return None
        
        # Copier le fichier vers l'hôte
        local_file = f"/tmp/velib_data_{os.path.basename(csv_path)}.csv"
        os.system(f"docker cp namenode:{result} {local_file}")
        
        # Charger le CSV
        df = pd.read_csv(local_file)
        print(f"✅ Chargé {len(df)} lignes depuis {csv_path}")
        
        # Nettoyer
        os.remove(local_file)
        os.system(f"docker exec namenode rm -rf /tmp/{os.path.basename(csv_path)}")
        
        return df
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {csv_path}: {e}")
        return None

def connect_mongodb():
    """Connexion à MongoDB"""
    try:
        client = MongoClient("mongodb://localhost:27018/velib")
        db = client.velib
        print("✅ Connexion MongoDB réussie")
        return db
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return None

def load_to_mongodb():
    """Charge tous les résultats dans MongoDB"""
    print("=== CHARGEMENT VERS MONGODB ===")
    
    # Connexion MongoDB
    db = connect_mongodb()
    if db is None:
        return
    
    # Charger les données
    collections = {
        "top_stations": "hdfs://namenode:9000/users/ipssi/output/top_stations_mongo",
        "stats_arrondissement": "hdfs://namenode:9000/users/ipssi/output/stats_arrondissement_mongo", 
        "taux_disponibilite": "hdfs://namenode:9000/users/ipssi/output/taux_disponibilite_mongo"
    }
    
    for collection_name, hdfs_path in collections.items():
        print(f"\n📊 Chargement de {collection_name}...")
        
        # Charger le CSV
        df = load_csv_from_hdfs(hdfs_path)
        if df is not None:
            # Insérer les nouvelles données (sans vider la collection)
            records = df.to_dict('records')
            db[collection_name].insert_many(records)
            
            print(f"✅ {collection_name}: {len(records)} documents insérés")
        else:
            print(f"❌ Échec du chargement de {collection_name}")
    
    print("\n🎉 Chargement MongoDB terminé !")

if __name__ == "__main__":
    load_to_mongodb()
