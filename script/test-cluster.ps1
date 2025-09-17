# Script de test du cluster Big Data Velib
# Utilisation: .\test-cluster.ps1

Write-Host "=== TEST DU CLUSTER BIG DATA VELIB ===" -ForegroundColor Green

Write-Host "1. Test de connectivité des services..." -ForegroundColor Yellow

# Fonction pour tester un endpoint
function Test-Endpoint {
    param($url, $name)
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $name : OK" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ $name : ECHEC" -ForegroundColor Red
        return $false
    }
}

# Tests des interfaces web
$tests = @(
    @{url="http://localhost:9870"; name="Hadoop NameNode"},
    @{url="http://localhost:8088"; name="YARN ResourceManager"},
    @{url="http://localhost:8080"; name="Spark Master"},
    @{url="http://localhost:8188"; name="History Server"}
)

$successCount = 0
foreach ($test in $tests) {
    if (Test-Endpoint $test.url $test.name) {
        $successCount++
    }
}

Write-Host ""
Write-Host "2. Test des conteneurs..." -ForegroundColor Yellow
$containers = docker-compose ps --services
$runningContainers = docker-compose ps -q
Write-Host "Conteneurs définis: $($containers.Count)" -ForegroundColor White
Write-Host "Conteneurs en cours: $($runningContainers.Count)" -ForegroundColor White

Write-Host ""
Write-Host "3. Test HDFS..." -ForegroundColor Yellow
try {
    $hdfsTest = docker exec namenode hdfs dfs -ls / 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ HDFS : Accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ HDFS : Problème d'accès" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ HDFS : Erreur lors du test" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Test MongoDB..." -ForegroundColor Yellow
try {
    $mongoTest = docker exec mongodb-ipssi mongosh --eval "db.adminCommand('ismaster')" --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MongoDB : Accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ MongoDB : Problème d'accès" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ MongoDB : Erreur lors du test" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== RESUME DES TESTS ===" -ForegroundColor Cyan
Write-Host "Interfaces web fonctionnelles: $successCount/4" -ForegroundColor White

if ($successCount -ge 3) {
    Write-Host "🎉 CLUSTER OPERATIONNEL !" -ForegroundColor Green
} else {
    Write-Host "⚠️  CLUSTER PARTIELLEMENT OPERATIONNEL" -ForegroundColor Yellow
    Write-Host "Vérifiez les logs: docker-compose logs" -ForegroundColor White
}
