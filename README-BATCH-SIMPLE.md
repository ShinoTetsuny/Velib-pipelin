# 🚀 Batch Processing - Velib Analytics

## 📊 Fonctionnalités Batch

### Analyses effectuées :
- **🏆 Top 10 stations** avec le plus de vélos disponibles
- **🏘️ Statistiques par arrondissement** (capacité, vélos disponibles)
- **📈 Taux de disponibilité** des stations
- **💾 Export des résultats** en CSV dans HDFS

## 🚀 Comment lancer

### 1. Démarrer le cluster
```bash
docker-compose up -d
```

### 2. Initialiser les données
```bash
docker exec namenode hdfs dfs -mkdir -p /users/ipssi/input/velib2
docker exec namenode hdfs dfs -mkdir -p /users/ipssi/output
docker cp app/velib.csv namenode:/tmp/velib.csv
docker exec namenode hdfs dfs -put /tmp/velib.csv /users/ipssi/input/velib2/
```

### 3. Lancer les analyses
```bash
chmod +x run-batch.sh
./run-batch.sh
```

## 📁 Résultats

Les résultats sont sauvegardés dans HDFS :
- `/users/ipssi/output/top_stations/` - Top 10 stations
- `/users/ipssi/output/stats_arrondissement/` - Stats par arrondissement  
- `/users/ipssi/output/taux_disponibilite/` - Taux de disponibilité

## 🔍 Vérifier les résultats

```bash
# Voir les fichiers générés
docker exec namenode hdfs dfs -ls /users/ipssi/output/

# Voir le contenu des résultats
docker exec namenode hdfs dfs -cat /users/ipssi/output/top_stations/part-00000-*.csv | head -5
```

## 🌐 Interfaces web

- **Hadoop** : http://localhost:9870
- **Spark** : http://localhost:8080
- **YARN** : http://localhost:8088

## 📊 Dashboard Streamlit

### Lancer le frontend
```bash
chmod +x run-streamlit.sh
./run-streamlit.sh
```

### Accéder au dashboard
- **URL** : http://localhost:8501
- **Fonctionnalités** : 8 pages d'analyse interactives
- **Graphiques** : Barres, lignes, scatter, pie charts
- **Filtres** : Par arrondissement, date, vélos

## 🛠️ Commandes utiles

```bash
# Arrêter le cluster
docker-compose down

# Voir les logs
docker-compose logs spark-master

# Redémarrer
docker-compose restart
```

---
**✅ Prêt ! Vos analyses Batch sont terminées.**
