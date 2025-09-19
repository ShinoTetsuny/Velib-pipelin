#!/bin/bash

# Script de déploiement du cluster Big Data Velib
# Utilisation: ./deploy-cluster.sh

echo "=== DEPLOIEMENT DU CLUSTER BIG DATA VELIB ==="

# Vérifier si Docker est en cours d'exécution
echo "Vérification de Docker..."
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker n'est pas installé ou n'est pas en cours d'exécution"
    exit 1
fi

# Arrêter tous les conteneurs existants
echo "Arrêt des conteneurs existants..."
docker-compose down -v

# Nettoyer les images inutiles (optionnel)
echo "Nettoyage des ressources Docker..."
docker system prune -f

# Créer les dossiers nécessaires
echo "Création des dossiers nécessaires..."
mkdir -p app

# Copier le fichier de données dans le dossier app
echo "Copie du fichier velib.csv dans le dossier app..."
if [ -f "velib.csv" ]; then
    cp "velib.csv" "app/velib.csv"
    echo "✅ Fichier velib.csv copié"
else
    echo "⚠️  Fichier velib.csv introuvable dans le répertoire racine"
fi

# Lancer le cluster
echo "Démarrage du cluster..."
docker-compose up -d

# Attendre que les services démarrent
echo "Attente du démarrage des services (60 secondes)..."
sleep 60

# Vérifier le statut des conteneurs
echo ""
echo "=== STATUT DES CONTENEURS ==="
docker-compose ps

echo ""
echo "=== INTERFACES WEB DISPONIBLES ==="
echo "🟢 Hadoop NameNode:     http://localhost:9870"
echo "🟢 YARN ResourceManager: http://localhost:8088"
echo "🟢 Spark Master:        http://localhost:8080"
echo "🟢 History Server:      http://localhost:8188"
echo ""
echo "=== COMMANDES UTILES ==="
echo "• Arrêter le cluster:    docker-compose down"
echo "• Voir les logs:         docker-compose logs [service]"
echo "• Se connecter à un service: docker exec -it [container] bash"

echo ""
echo "✅ CLUSTER DEPLOYE AVEC SUCCES !"
