#!/bin/bash

echo "=== INITIALISATION HDFS POUR VELIB ==="

# Attendre que le namenode soit prêt
echo "Attente du démarrage du namenode..."
sleep 30

# Créer les répertoires HDFS
echo "Création des répertoires HDFS..."
hdfs dfs -mkdir -p /users/ipssi/input/velib2
hdfs dfs -mkdir -p /users/ipssi/output

# Copier le fichier velib.csv vers HDFS
echo "Copie du fichier velib.csv vers HDFS..."
hdfs dfs -put /app/velib.csv /users/ipssi/input/velib2/

# Vérifier que le fichier a été copié
echo "Vérification des fichiers dans HDFS:"
hdfs dfs -ls /users/ipssi/input/velib2/

echo "✅ Initialisation HDFS terminée!"
