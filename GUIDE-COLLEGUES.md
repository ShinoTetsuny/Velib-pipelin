# 🚀 Guide Installation Cluster Velib - Pour les Collègues

## 🎯 **Prérequis**
- Docker Desktop installé et démarré
- PowerShell (ou Terminal Windows)
- Au minimum 6GB RAM libre

## ⚡ **Installation en 3 étapes**

### 1. **Démarrer le cluster**
```powershell
.\deploy-cluster.ps1
```
→ Lance tous les conteneurs (namenode, spark, mongodb...)

### 2. **Initialiser les données**
```powershell
.\init-hdfs.ps1
```
→ Copie velib.csv vers HDFS et créé l'arborescence

### 3. **Développer vos parties**
Maintenant vous pouvez travailler sur votre partie :
- **Batch** : Créer des scripts d'analyse Spark
- **Streaming** : Développer le traitement temps réel

## 🌐 **Interfaces disponibles**

| Interface | URL | Description |
|-----------|-----|-------------|
| Hadoop | http://localhost:9870 | Système de fichiers HDFS |
| Spark | http://localhost:8080 | Cluster de traitement |
| YARN | http://localhost:8088 | Gestionnaire de jobs |

## 🔧 **Commandes utiles**

### Initialisation
```powershell
.\init-hdfs.ps1          # Initialiser HDFS avec les données
```

### Développement des jobs (à faire)
```powershell
# À créer par l'équipe BATCH
.\run-batch-analysis.ps1

# À créer par l'équipe STREAMING  
.\run-streaming.ps1
```

### Dépannage
```powershell
# Tester le cluster
.\test-cluster.ps1

# Voir les logs d'un service
docker-compose logs spark-master

# Redémarrer le cluster
docker-compose restart

# Arrêter le cluster
docker-compose down
```

### Accéder aux conteneurs
```powershell
# HDFS (pour vérifier les fichiers)
docker exec -it namenode bash
hdfs dfs -ls /users/ipssi/input/velib2/

# MongoDB (pour voir les résultats)
docker exec -it mongodb-ipssi mongosh
use velib
db.batch_results.find().limit(5)

# Spark Master
docker exec -it spark-master bash
```

## 📊 **Développement**

### Pour le **BATCH** :
- Modifier : `app/batch-spark.py`
- Tester : `.\run-jobs.ps1 batch`
- Résultats : MongoDB collection `velib.batch_results`

### Pour le **STREAMING** :
- Modifier : `streaming-velib.py` (dans le dossier racine)  
- Tester : `.\run-jobs.ps1 streaming`
- Résultats : Console + MongoDB

### Pour l'**INFRASTRUCTURE** :
- Config cluster : `docker-compose.yml`
- Variables Hadoop : `hadoop.env`
- Scripts : `deploy-cluster.ps1`, `run-jobs.ps1`

## ❌ **Résolution des problèmes courants**

### Le cluster ne démarre pas
```powershell
# Vérifier Docker
docker --version

# Nettoyer et relancer
docker-compose down -v
.\deploy-cluster.ps1
```

### "hdfs command not found"
→ **Normal**, c'est pour ça qu'on utilise `docker exec namenode hdfs ...`

### Job Spark échoue
```powershell
# Vérifier que l'init est fait
docker exec namenode hdfs dfs -ls /users/ipssi/input/velib2/

# Voir les logs détaillés
docker-compose logs spark-master
```

### Ports occupés
```powershell
netstat -an | findstr "8080\|8088\|9870"
# Si occupés, arrêter les autres services
```

## 🎉 **C'est prêt !**

Le cluster est maintenant opérationnel. Chacun peut travailler sur sa partie :
- **Batch** : Analyses complexes des données historiques
- **Streaming** : Traitement temps réel des nouvelles données  
- **Infrastructure** : Monitoring, optimisation, sécurité

**Bon développement ! 🚀**
