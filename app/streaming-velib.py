from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime
import json

# Initialisation de la SparkSession
spark = SparkSession \
    .builder \
    .appName("velib-streaming-advanced") \
    .master("spark://spark-master:7077") \
    .config("spark.mongodb.input.uri", "mongodb://admin:pwd@mongodb-ipssi:27017/admin.my_collection") \
    .config("spark.mongodb.output.uri", "mongodb://admin:pwd@mongodb-ipssi:27017/admin.my_collection") \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
    .getOrCreate()

spark.sql("set spark.sql.streaming.schemaInference=true")
spark.sparkContext.setLogLevel("WARN")

# Définition du schéma complet pour les données Velib
velib_schema = StructType([
    StructField("stationcode", StringType(), True),
    StructField("name", StringType(), True),
    StructField("is_installed", StringType(), True),
    StructField("capacity", IntegerType(), True),
    StructField("numdocksavailable", IntegerType(), True),
    StructField("numbikesavailable", IntegerType(), True),
    StructField("mechanical", IntegerType(), True),
    StructField("ebike", IntegerType(), True),
    StructField("is_renting", StringType(), True),
    StructField("is_returning", StringType(), True),
    StructField("duedate", StringType(), True),
    StructField("coordonnees_geo", StringType(), True),
    StructField("nom_arrondissement_communes", StringType(), True),
    StructField("code_insee_commune", StringType(), True)
])

# Initialisation du streaming avec schéma défini
streamDf = spark \
    .readStream \
    .option("delimiter", ";") \
    .option("header", "true") \
    .schema(velib_schema) \
    .csv("hdfs://namenode:9000/users/ipssi/input/velib2")

print(f"Streaming actif: {streamDf.isStreaming}")

# Ajout de colonnes calculées et transformation des données
streamDf_processed = streamDf \
    .withColumn("timestamp", current_timestamp()) \
    .withColumn("taux_occupation", (col("numbikesavailable") / col("capacity")) * 100) \
    .withColumn("taux_disponibilite", (col("numdocksavailable") / col("capacity")) * 100) \
    .withColumn("latitude", split(col("coordonnees_geo"), ",")[0].cast("double")) \
    .withColumn("longitude", split(col("coordonnees_geo"), ",")[1].cast("double")) \
    .withColumn("is_installed_bool", when(col("is_installed") == "OUI", True).otherwise(False)) \
    .withColumn("is_renting_bool", when(col("is_renting") == "OUI", True).otherwise(False)) \
    .withColumn("is_returning_bool", when(col("is_returning") == "OUI", True).otherwise(False)) \
    .withColumn("duedate_parsed", to_timestamp(col("duedate"), "yyyy-MM-dd'T'HH:mm:ssXXX"))

# Vue temporaire pour requêtes SQL
streamDf_processed.createOrReplaceTempView("velib_stream")

print("=== ANALYSES EN TEMPS RÉEL ===")

# 1. Stations vides (aucun vélo disponible)
def query_stations_vides():
    return spark.sql("""
        SELECT stationcode, name, numbikesavailable, nom_arrondissement_communes, timestamp
        FROM velib_stream 
        WHERE numbikesavailable = 0 AND is_installed_bool = true
        ORDER BY timestamp DESC
    """)

# 2. Stations pleines (aucune place disponible)
def query_stations_pleines():
    return spark.sql("""
        SELECT stationcode, name, numdocksavailable, nom_arrondissement_communes, timestamp
        FROM velib_stream 
        WHERE numdocksavailable = 0 AND is_installed_bool = true
        ORDER BY timestamp DESC
    """)

# 3. Top stations par nombre de vélos disponibles
def query_top_stations():
    return spark.sql("""
        SELECT stationcode, name, numbikesavailable, mechanical, ebike, 
               nom_arrondissement_communes, taux_occupation, timestamp
        FROM velib_stream 
        WHERE is_installed_bool = true
        ORDER BY numbikesavailable DESC
        LIMIT 20
    """)

# 4. Statistiques par arrondissement
def query_stats_arrondissement():
    return spark.sql("""
        SELECT nom_arrondissement_communes,
               COUNT(*) as nb_stations,
               AVG(numbikesavailable) as avg_bikes,
               AVG(numdocksavailable) as avg_docks,
               AVG(taux_occupation) as avg_occupation_rate,
               SUM(mechanical) as total_mechanical,
               SUM(ebike) as total_ebike
        FROM velib_stream 
        WHERE is_installed_bool = true
        GROUP BY nom_arrondissement_communes
        ORDER BY avg_occupation_rate DESC
    """)

# 5. Stations avec vélos électriques
def query_stations_ebike():
    return spark.sql("""
        SELECT stationcode, name, ebike, mechanical, numbikesavailable,
               nom_arrondissement_communes, timestamp
        FROM velib_stream 
        WHERE ebike > 0 AND is_installed_bool = true
        ORDER BY ebike DESC
    """)

# 6. Stations non fonctionnelles
def query_stations_non_fonctionnelles():
    return spark.sql("""
        SELECT stationcode, name, is_installed, is_renting, is_returning,
               nom_arrondissement_communes, timestamp
        FROM velib_stream 
        WHERE is_installed_bool = false OR is_renting_bool = false OR is_returning_bool = false
        ORDER BY timestamp DESC
    """)

# Fonction d'écriture dans MongoDB
def write_to_mongodb(batch_df, batch_id):
    try:
        # Écriture des données brutes
        batch_df.write.format("mongodb").mode("append").save()
        
        # Écriture des analyses
        if not batch_df.isEmpty():
            # Top stations du batch
            top_batch = batch_df.orderBy(col("numbikesavailable").desc()).limit(10)
            top_batch.write.format("mongodb").mode("append").option("collection", "top_stations").save()
            
            # Stats par arrondissement du batch
            stats_batch = batch_df.groupBy("nom_arrondissement_communes") \
                .agg(
                    count("*").alias("nb_stations"),
                    avg("numbikesavailable").alias("avg_bikes"),
                    avg("taux_occupation").alias("avg_occupation")
                )
            stats_batch.write.format("mongodb").mode("append").option("collection", "stats_arrondissement").save()
            
        print(f"Batch {batch_id} écrit avec succès dans MongoDB")
    except Exception as e:
        print(f"Erreur lors de l'écriture du batch {batch_id}: {str(e)}")

# Démarrage des requêtes de streaming
print("Démarrage des analyses de streaming...")

# Query 1: Stations vides
query1 = query_stations_vides() \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime='30 seconds') \
    .queryName("stations_vides") \
    .start()

# Query 2: Top stations
query2 = query_top_stations() \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime='60 seconds') \
    .queryName("top_stations") \
    .start()

# Query 3: Stats par arrondissement
query3 = query_stats_arrondissement() \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime='60 seconds') \
    .queryName("stats_arrondissement") \
    .start()

# Query 4: Écriture dans MongoDB
query4 = streamDf_processed \
    .writeStream \
    .foreachBatch(write_to_mongodb) \
    .trigger(processingTime='30 seconds') \
    .queryName("mongodb_write") \
    .start()

# Attendre la terminaison
try:
    query1.awaitTermination()
    query2.awaitTermination()
    query3.awaitTermination()
    query4.awaitTermination()
except KeyboardInterrupt:
    print("Arrêt des requêtes de streaming...")
    query1.stop()
    query2.stop()
    query3.stop()
    query4.stop()
    spark.stop()

