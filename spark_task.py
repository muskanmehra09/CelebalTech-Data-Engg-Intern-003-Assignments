from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# Spark session
spark = SparkSession.builder.appName("DataEngineeringTask").getOrCreate()

# Load dataset
df = spark.read.csv("backpacks.csv", header=True, inferSchema=True)

# first 5 rows
df.show(5)

# Cleaning
df_clean = df.dropna().dropDuplicates()

# Transformation: rename + new column
df_transformed = df_clean.withColumnRenamed("Item", "Product") \
                         .withColumn("DiscountPrice", F.col("Price") * 0.9)

# Aggregation
df_transformed.groupBy("Category").agg(
    F.count("*").alias("TotalItems"),
    F.avg("Price").alias("AvgPrice"),
    F.min("Price").alias("MinPrice"),
    F.max("Price").alias("MaxPrice")
).show()
