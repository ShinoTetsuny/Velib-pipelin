from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import* 


# Initialisation de la SparkSession
spark = SparkSession \
    .builder \
    .appName("streaming-test") \
    .master("spark://spark-master:7077") \
    .config("spark.mongodb.input.uri", "mongodb://admin:pwd@mongo:27017/admin.my_collection") \
    .config("spark.mongodb.output.uri", "mongodb://admin:pwd@mongo:27017/admin.my_collection") \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
    .getOrCreate()

spark.sql("set spark.sql.streaming.schemaInference=true")

spark.sparkContext.setLogLevel("WARN")

# Initialisation
streamDf = spark \
    .readStream \
    .option("delimiter", ";") \
    .option("header", "true") \
    .csv("hdfs://namenode:9000/users/ipssi/input/velib2")

print(streamDf.isStreaming)


simpleQuery = streamDf \
    .writeStream \
    .format("console")
simpleQuery.start().awaitTermination()

# Vue temporaire pour utilisÃ© des query SQL 
streamDf.createOrReplaceTempView("tempdf")

dfclean = spark.sql("Select name,numbikesavailable FROM tempdf where numbikesavailable == '0' ")

dfclean \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start().awaitTermination() \


df1 = streamDf \
    .groupBy("name") \
    .agg(sum("numbikesavailable")) \
    .orderBy("sum(numbikesavailable)", ascending=False) \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start().awaitTermination()

df1 = streamDf \
    .groupBy("name") \
    .agg(sum("numbikesavailable")) \
    .orderBy("sum(numbikesavailable)", ascending=False)


# Ã‰criture dans mongoDb
def write_row(batch_df , batch_id):
    batch_df.write.format("mongodb").mode("append").save()
    pass

streamDf.writeStream.foreachBatch(write_row).start().awaitTermination()

