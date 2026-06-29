from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

# 1. Spark Session
spark = SparkSession.builder \
    .appName("SparkAssignment") \
    .getOrCreate()

# 2. Read Data (CSV + Parquet)
csv_df = spark.read.option("header", True).csv("input_data.csv", inferSchema=True)
parquet_df = spark.read.parquet("input_data.parquet")

# 3. Schema Handling + Column Selection
df = csv_df.select("id", "name", "age", "salary")

# 4. Filtering
filtered_df = df.filter(col("age") > 25)

# 5. Modify DataFrame
modified_df = filtered_df.withColumnRenamed("salary", "emp_salary") \
    .withColumn("bonus", col("emp_salary") * 0.1) \
    .withColumn("constant_col", lit("CelebalTech"))

# 6. Transformations + Actions
modified_df.show(5)   # safe preview
count_val = modified_df.count()

# 7. Handle Nulls
clean_df = modified_df.na.drop()

# 8. Save Output (CSV + Parquet)
clean_df.write.mode("overwrite").csv("output_csv")
clean_df.write.mode("overwrite").parquet("output_parquet")

print("✅ Pipeline Done | Rows:", count_val)
