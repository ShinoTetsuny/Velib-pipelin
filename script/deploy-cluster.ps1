# Script de déploiement du cluster Big Data Velib
# Utilisation: .\deploy-cluster.ps1

Write-Host "=== DEPLOIEMENT DU CLUSTER BIG DATA VELIB ===" -ForegroundColor Green

# Vérifier si Docker est en cours d'exécution
Write-Host "Vérification de Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker n'est pas installé ou n'est pas en cours d'exécution" -ForegroundColor Red
    exit 1
}

# Arrêter tous les conteneurs existants
Write-Host "Arrêt des conteneurs existants..." -ForegroundColor Yellow
docker-compose down -v

# Nettoyer les images inutiles (optionnel)
Write-Host "Nettoyage des ressources Docker..." -ForegroundColor Yellow
docker system prune -f

# Copier le fichier de données dans le dossier app
Write-Host "Copie du fichier velib.csv dans le dossier app..." -ForegroundColor Yellow
if (Test-Path "velib.csv") {
    Copy-Item "velib.csv" "app\velib.csv" -Force
    Write-Host "✅ Fichier velib.csv copié" -ForegroundColor Green
} else {
    Write-Host "⚠️  Fichier velib.csv introuvable" -ForegroundColor Yellow
}

# Créer les dossiers nécessaires
Write-Host "Création des dossiers nécessaires..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "mongodb"
New-Item -ItemType Directory -Force -Path "app"

# Lancer le cluster
Write-Host "Démarrage du cluster..." -ForegroundColor Yellow
docker-compose up -d

# Attendre que les services démarrent
Write-Host "Attente du démarrage des services (60 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Vérifier le statut des conteneurs
Write-Host "=== STATUT DES CONTENEURS ===" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "=== INTERFACES WEB DISPONIBLES ===" -ForegroundColor Cyan
Write-Host "🟢 Hadoop NameNode:     http://localhost:9870" -ForegroundColor White
Write-Host "🟢 YARN ResourceManager: http://localhost:8088" -ForegroundColor White
Write-Host "🟢 Spark Master:        http://localhost:8080" -ForegroundColor White
Write-Host "🟢 History Server:      http://localhost:8188" -ForegroundColor White
Write-Host ""
Write-Host "=== COMMANDES UTILES ===" -ForegroundColor Cyan
Write-Host "• Arrêter le cluster:    docker-compose down" -ForegroundColor White
Write-Host "• Voir les logs:         docker-compose logs [service]" -ForegroundColor White
Write-Host "• Se connecter à un service: docker exec -it [container] bash" -ForegroundColor White

Write-Host ""
Write-Host "✅ CLUSTER DEPLOYE AVEC SUCCES !" -ForegroundColor Green
