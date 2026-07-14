"""
BRONZE LAYER
------------
Raw ingestion of CRM, Billing, and Analytics source data into Delta Lake,
with no transformation applied (schema-on-read, source of truth for audit).

Supports batch ingestion today; the same `read_csv` call can be swapped for
`spark.readStream` against an autoloader / cloudFiles source to extend this
to streaming ingestion per the architecture's "batch + streaming" goal.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import RAW_FILES, BRONZE_PATH


def ingest_source(spark: SparkSession, name: str, path: str) -> DataFrame:
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(path)
        .withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_file", input_file_name())
    )
    return df


def run(spark: SparkSession):
    results = {}
    for name, path in RAW_FILES.items():
        df = ingest_source(spark, name, path)
        out_path = f"{BRONZE_PATH}/{name}"
        (
            df.write
            .format("delta")
            .mode("overwrite")
            .save(out_path)
        )
        results[name] = df.count()
        print(f"[bronze] {name}: {results[name]} rows written to {out_path}")
    return results


if __name__ == "__main__":
    from utils.spark_session import get_spark
    spark = get_spark()
    run(spark)
