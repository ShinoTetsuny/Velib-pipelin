#!/bin/bash

echo "=== TEST CONNEXION MONGODB ==="

# Vérifier que MongoDB est en cours d'exécution
if ! docker ps | grep -q "mongodb-ipssi"; then
    echo "❌ MongoDB n'est pas démarré"
    exit 1
fi

echo "✅ MongoDB est en cours d'exécution"

# Tester la connexion
echo "🔍 Test de connexion MongoDB..."
docker exec mongodb-ipssi mongosh --eval "
    use velib;
    print('✅ Connexion MongoDB réussie');
    print('Collections disponibles:');
    db.getCollectionNames();
"

# Vérifier les données après exécution du batch
echo "📊 Vérification des données..."
docker exec mongodb-ipssi mongosh --eval "
    use velib;
    print('=== DONNEES DANS MONGODB ===');
    
    print('\\n📈 Top stations:');
    db.top_stations.find().limit(3).pretty();
    
    print('\\n🏘️ Stats arrondissement:');
    db.stats_arrondissement.find().limit(3).pretty();
    
    print('\\n📊 Taux de disponibilité:');
    db.taux_disponibilite.find().limit(3).pretty();
    
    print('\\n📅 Dernière mise à jour:');
    db.top_stations.findOne({}, {batch_timestamp: 1});
"
