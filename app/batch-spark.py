from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Configuration Spark avec MongoDB
spark = SparkSession \
    .builder \
    .appName("VelibBatchProcessing") \
    .master("spark://spark-master:7077") \
    .config("spark.mongodb.input.uri", "mongodb://admin:pwd@mongodb-ipssi:27017/velib.stations") \
    .config("spark.mongodb.output.uri", "mongodb://admin:pwd@mongodb-ipssi:27017/velib.batch_results") \
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
        
        # Analyse 1: Capacité totale par station
        capacity_analysis = df.groupBy("name", "capacity") \
            .agg(
                count("*").alias("nb_mesures"),
                avg("numbikesavailable").alias("moy_velos_disponibles"),
                max("numbikesavailable").alias("max_velos"),
                min("numbikesavailable").alias("min_velos")
            )
        
        print("=== ANALYSE DES CAPACITES ===")
        capacity_analysis.show(20, truncate=False)
        
        # Sauvegarde en MongoDB
        capacity_analysis.write \
            .format("mongodb") \
            .mode("overwrite") \
            .option("collection", "station_capacity_analysis") \
            .save()
        
        print("✅ Données sauvegardées dans MongoDB")
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
