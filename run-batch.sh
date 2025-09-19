#!/bin/bash

echo "=== LANCEMENT DU JOB BATCH VELIB ==="

# Vérifier que le cluster est en cours d'exécution
if ! docker ps | grep -q "spark-master"; then
    echo "❌ Le cluster Spark n'est pas démarré. Lancez d'abord: docker-compose up -d"
    exit 1
fi

# Vérifier que les données sont en HDFS
echo "Vérification des données HDFS..."
docker exec namenode hdfs dfs -ls /users/ipssi/input/velib2/

if [ $? -ne 0 ]; then
    echo "❌ Les données ne sont pas en HDFS. Lancez d'abord l'initialisation HDFS"
    exit 1
fi

echo "✅ Cluster et données prêts"
echo ""

# Lancer le job Spark
echo "🚀 Lancement du job batch-spark.py..."
docker exec spark-master /spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.2 \
    --conf "spark.mongodb.output.uri=mongodb://admin:pwd@mongodb-ipssi:27018/velib.batch_results" \
    /app/batch-spark.py

echo ""
echo "=== CHARGEMENT VERS MONGODB ==="
python3 load-to-mongodb.py

echo "=== JOB TERMINE ==="
echo "Vérifiez les résultats dans MongoDB:"
echo "docker exec -it mongodb-ipssi mongosh"
echo "use velib"
echo "db.top_stations.find().limit(5)"
