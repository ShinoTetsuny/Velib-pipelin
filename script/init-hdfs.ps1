# Script d'initialisation HDFS pour le cluster Velib
# Utilisation: .\init-hdfs.ps1

Write-Host "=== INITIALISATION HDFS VELIB ===" -ForegroundColor Green
Write-Host "Ce script initialise le système HDFS avec les données Velib" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le cluster est en cours d'exécution
Write-Host "Vérification du cluster..." -ForegroundColor Yellow
$runningContainers = docker-compose ps -q
if ($runningContainers.Count -eq 0) {
    Write-Host "❌ Le cluster n'est pas démarré. Lancez d'abord .\deploy-cluster.ps1" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "1. .\deploy-cluster.ps1    # Démarrer le cluster" -ForegroundColor White
    Write-Host "2. .\init-hdfs.ps1         # Initialiser HDFS (ce script)" -ForegroundColor White
    exit 1
}

Write-Host "Création des dossiers HDFS..." -ForegroundColor Yellow

# Créer les dossiers HDFS
docker exec namenode hdfs dfs -mkdir -p /users/ipssi/input/velib2
docker exec namenode hdfs dfs -mkdir -p /users/ipssi/output

Write-Host "Copie du fichier velib.csv vers HDFS..." -ForegroundColor Yellow

# Copier le fichier vers le conteneur namenode puis vers HDFS
docker cp app/velib.csv namenode:/tmp/velib.csv
docker exec namenode hdfs dfs -put /tmp/velib.csv /users/ipssi/input/velib2/

# Vérifier que le fichier est bien copié
Write-Host "Vérification des fichiers dans HDFS..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -ls /users/ipssi/input/velib2/

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ INITIALISATION HDFS TERMINÉE AVEC SUCCÈS" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Données disponibles dans HDFS:" -ForegroundColor Cyan
    Write-Host "• Chemin HDFS: hdfs://namenode:9000/users/ipssi/input/velib2/velib.csv" -ForegroundColor White
    Write-Host "• Nombre d'enregistrements: ~1453 lignes" -ForegroundColor White
    Write-Host "• Dossier de sortie: hdfs://namenode:9000/users/ipssi/output/" -ForegroundColor White
} else {
    Write-Host "❌ Erreur lors de l'initialisation HDFS" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎯 NEXT STEPS POUR VOS COLLÈGUES:" -ForegroundColor Green
Write-Host "• BATCH: Développer les analyses des données (Spark SQL, agrégations, etc.)" -ForegroundColor White
Write-Host "• STREAMING: Implémenter le traitement temps réel (Structured Streaming)" -ForegroundColor White

Write-Host ""
Write-Host "=== COMMANDES UTILES ===" -ForegroundColor Cyan
Write-Host "• Vérifier HDFS:          docker exec namenode hdfs dfs -ls /users/ipssi/input/velib2/" -ForegroundColor White
Write-Host "• Interface Hadoop:       http://localhost:9870" -ForegroundColor White
Write-Host "• Interface Spark:        http://localhost:8080" -ForegroundColor White
Write-Host "• Accéder à MongoDB:      docker exec -it mongodb-ipssi mongosh" -ForegroundColor White
