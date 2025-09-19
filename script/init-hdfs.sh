#!/bin/bash

# Script d'initialisation HDFS pour le cluster Velib
# Utilisation: ./init-hdfs.sh

echo "=== INITIALISATION HDFS VELIB ==="
echo "Ce script initialise le système HDFS avec les données Velib"
echo ""

# Vérifier que le cluster est en cours d'exécution
echo "Vérification du cluster..."
running_containers=$(docker-compose ps -q)
if [ -z "$running_containers" ]; then
    echo "❌ Le cluster n'est pas démarré. Lancez d'abord ./deploy-cluster.sh"
    echo ""
    echo "Usage:"
    echo "1. ./deploy-cluster.sh    # Démarrer le cluster"
    echo "2. ./init-hdfs.sh         # Initialiser HDFS (ce script)"
    exit 1
fi

echo "Création des dossiers HDFS..."

# Créer les dossiers HDFS
docker exec namenode hdfs dfs -mkdir -p /users/ipssi/input/velib2
docker exec namenode hdfs dfs -mkdir -p /users/ipssi/output

echo "Copie du fichier velib.csv vers HDFS..."

# Copier le fichier vers le conteneur namenode puis vers HDFS
docker cp app/velib.csv namenode:/tmp/velib.csv
docker exec namenode hdfs dfs -put /tmp/velib.csv /users/ipssi/input/velib2/

# Vérifier que le fichier est bien copié
echo "Vérification des fichiers dans HDFS..."
docker exec namenode hdfs dfs -ls /users/ipssi/input/velib2/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ INITIALISATION HDFS TERMINÉE AVEC SUCCÈS"
    echo ""
    echo "📊 Données disponibles dans HDFS:"
    echo "• Chemin HDFS: hdfs://namenode:9000/users/ipssi/input/velib2/velib.csv"
    echo "• Nombre d'enregistrements: ~1453 lignes"
    echo "• Dossier de sortie: hdfs://namenode:9000/users/ipssi/output/"
else
    echo "❌ Erreur lors de l'initialisation HDFS"
    exit 1
fi

echo ""
echo "🎯 NEXT STEPS POUR VOS COLLÈGUES:"
echo "• BATCH: Développer les analyses des données (Spark SQL, agrégations, etc.)"
echo "• STREAMING: Implémenter le traitement temps réel (Structured Streaming)"

echo ""
echo "=== COMMANDES UTILES ==="
echo "• Vérifier HDFS:          docker exec namenode hdfs dfs -ls /users/ipssi/input/velib2/"
echo "• Interface Hadoop:       http://localhost:9870"
echo "• Interface Spark:        http://localhost:8080"
echo "• Accéder à MongoDB:      docker exec -it mongodb-ipssi mongosh"
