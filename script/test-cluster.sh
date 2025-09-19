#!/bin/bash

# Script de test du cluster Big Data Velib
# Utilisation: ./test-cluster.sh

echo "=== TEST DU CLUSTER BIG DATA VELIB ==="

echo "1. Test de connectivité des services..."

# Fonction pour tester un endpoint
test_endpoint() {
    local url=$1
    local name=$2
    if curl -s --connect-timeout 10 "$url" > /dev/null 2>&1; then
        echo "✅ $name : OK"
        return 0
    else
        echo "❌ $name : ECHEC"
        return 1
    fi
}

# Tests des interfaces web
declare -a tests=(
    "http://localhost:9870:Hadoop NameNode"
    "http://localhost:8088:YARN ResourceManager"
    "http://localhost:8080:Spark Master"
    "http://localhost:8188:History Server"
)

success_count=0
for test in "${tests[@]}"; do
    IFS=':' read -r url name <<< "$test"
    if test_endpoint "$url" "$name"; then
        ((success_count++))
    fi
done

echo ""
echo "2. Test des conteneurs..."
containers=$(docker-compose ps --services | wc -l)
running_containers=$(docker-compose ps -q | wc -l)
echo "Conteneurs définis: $containers"
echo "Conteneurs en cours: $running_containers"

echo ""
echo "3. Test HDFS..."
if docker exec namenode hdfs dfs -ls / > /dev/null 2>&1; then
    echo "✅ HDFS : Accessible"
else
    echo "❌ HDFS : Problème d'accès"
fi

echo ""
echo "4. Test MongoDB..."
if docker exec mongodb-ipssi mongosh --eval "db.adminCommand('ismaster')" --quiet > /dev/null 2>&1; then
    echo "✅ MongoDB : Accessible"
else
    echo "❌ MongoDB : Problème d'accès"
fi

echo ""
echo "=== RESUME DES TESTS ==="
echo "Interfaces web fonctionnelles: $success_count/4"

if [ $success_count -ge 3 ]; then
    echo "🎉 CLUSTER OPERATIONNEL !"
else
    echo "⚠️  CLUSTER PARTIELLEMENT OPERATIONNEL"
    echo "Vérifiez les logs: docker-compose logs"
fi
