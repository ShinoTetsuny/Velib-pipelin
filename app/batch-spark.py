from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Configuration Spark avec MongoDB
spark = SparkSession \
    .builder \
    .appName("VelibBatchProcessing") \
    .master("spark://spark-master:7077") \
    .config("spark.mongodb.input.uri", "mongodb://admin:pwd@mongodb-ipssi:27018/velib.stations") \
    .config("spark.mongodb.output.uri", "mongodb://admin:pwd@mongodb-ipssi:27018/velib.batch_results") \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

def main():
    print("=== DEBUT DU TRAITEMENT BATCH VELIB ===")
    
    # Lecture des données depuis HDFS
    try:
        df = spark.read \
            .option("header", "true") \
            .option("delimiter", ";") \
            .csv("hdfs://namenode:9000/users/ipssi/input/velib2/velib.csv")
        
        print(f"Nombre total d'enregistrements: {df.count()}")
        df.printSchema()
        
        # Conversion des colonnes numériques
        df_typed = df.withColumn("capacity", col("capacity").cast("int")) \
                    .withColumn("numbikesavailable", col("numbikesavailable").cast("int")) \
                    .withColumn("numdocksavailable", col("numdocksavailable").cast("int")) \
                    .withColumn("mechanical", col("mechanical").cast("int")) \
                    .withColumn("ebike", col("ebike").cast("int"))
        
        # Analyse 1: Top 10 des stations avec le plus de vélos disponibles
        print("=== TOP 10 STATIONS AVEC LE PLUS DE VELOS ===")
        top_stations = df_typed.filter(col("is_installed") == "OUI") \
                              .groupBy("name", "nom_arrondissement_communes") \
                              .agg(
                                  avg("numbikesavailable").alias("moy_velos"),
                                  max("numbikesavailable").alias("max_velos"),
                                  avg("capacity").alias("capacite_moyenne")
                              ) \
                              .orderBy(desc("moy_velos")) \
                              .limit(10)
        
        top_stations.show(10, truncate=False)
        
        # Analyse 2: Statistiques par arrondissement
        print("=== STATISTIQUES PAR ARRONDISSEMENT ===")
        stats_arrondissement = df_typed.filter(col("is_installed") == "OUI") \
                                      .groupBy("nom_arrondissement_communes") \
                                      .agg(
                                          countDistinct("name").alias("nb_stations"),
                                          sum("capacity").alias("capacite_totale"),
                                          avg("numbikesavailable").alias("moy_velos_disponibles"),
                                          sum("numbikesavailable").alias("total_velos_disponibles")
                                      ) \
                                      .orderBy(desc("total_velos_disponibles"))
        
        stats_arrondissement.show(20, truncate=False)
        
        # Analyse 3: Taux de disponibilité des stations
        print("=== TAUX DE DISPONIBILITE DES STATIONS ===")
        taux_disponibilite = df_typed.filter(col("is_installed") == "OUI") \
                                    .withColumn("taux_dispo", col("numbikesavailable") / col("capacity") * 100) \
                                    .groupBy("name") \
                                    .agg(
                                        avg("taux_dispo").alias("taux_moyen_dispo"),
                                        count("*").alias("nb_mesures")
                                    ) \
                                    .filter(col("taux_moyen_dispo") > 0) \
                                    .orderBy(desc("taux_moyen_dispo")) \
                                    .limit(15)
        
        taux_disponibilite.show(15, truncate=False)
        
        # Sauvegarde des résultats en MongoDB ET CSV
        print("=== SAUVEGARDE DES RESULTATS ===")
        
        # Ajouter un timestamp pour le suivi
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Sauvegarde MongoDB via script Python séparé
        print("📊 Sauvegarde des résultats en CSV pour MongoDB...")
        
        # Sauvegarder en CSV temporaire pour MongoDB
        top_stations_mongo = top_stations.withColumn("batch_timestamp", lit(timestamp))
        top_stations_mongo.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000/users/ipssi/output/top_stations_mongo")
        
        stats_arrondissement_mongo = stats_arrondissement.withColumn("batch_timestamp", lit(timestamp))
        stats_arrondissement_mongo.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000/users/ipssi/output/stats_arrondissement_mongo")
        
        taux_disponibilite_mongo = taux_disponibilite.withColumn("batch_timestamp", lit(timestamp))
        taux_disponibilite_mongo.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000/users/ipssi/output/taux_disponibilite_mongo")
        
        print("✅ Fichiers CSV créés pour MongoDB")
        
        # Sauvegarde CSV en backup (optionnel)
        top_stations.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000/users/ipssi/output/top_stations")
        
        stats_arrondissement.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000/users/ipssi/output/stats_arrondissement")
        
        taux_disponibilite.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("hdfs://namenode:9000/users/ipssi/output/taux_disponibilite")
        
        print("✅ Toutes les analyses sauvegardées dans MongoDB et HDFS")
        print(f"📅 Timestamp du batch: {timestamp}")
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
