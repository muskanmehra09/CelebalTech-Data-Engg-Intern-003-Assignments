"""
SILVER LAYER — cleaning & standardization
------------------------------------------
- Casts types
- Standardizes placeholder/junk values to null
- Checks for schema drift against the expected contract
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, DateType, IntegerType

from utils.config import BRONZE_PATH, SILVER_PATH, EXPECTED_SCHEMAS, PLACEHOLDER_VALUES


def check_schema_drift(df: DataFrame, name: str) -> dict:
    expected = EXPECTED_SCHEMAS[name]
    actual = [c for c in df.columns if not c.startswith("_")]
    missing_cols = [c for c in expected if c not in actual]
    extra_cols = [c for c in actual if c not in expected]
    return {
        "dataset": name,
        "expected_columns": expected,
        "actual_columns": actual,
        "missing_columns": missing_cols,
        "extra_columns": extra_cols,
        "drift_detected": bool(missing_cols or extra_cols),
    }


def clean_crm(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("signup_date", F.to_date("signup_date"))
        .withColumn(
            "city",
            F.when(F.col("city").isin(PLACEHOLDER_VALUES), None).otherwise(F.col("city"))
        )
        .withColumn(
            "email",
            F.when(F.col("email").isin(PLACEHOLDER_VALUES), None).otherwise(F.col("email"))
        )
    )


def clean_billing(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("amount", F.col("amount").cast(DoubleType()))
        .withColumn("transaction_date", F.to_date("transaction_date"))
    )


def clean_analytics(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("date", F.to_date("date"))
        .withColumn("total_customers", F.col("total_customers").cast(IntegerType()))
        .withColumn("total_revenue", F.col("total_revenue").cast(DoubleType()))
        .withColumn("avg_transaction", F.col("avg_transaction").cast(DoubleType()))
    )


CLEANERS = {"crm": clean_crm, "billing": clean_billing, "analytics": clean_analytics}


def run(spark: SparkSession):
    schema_report = []
    for name, cleaner in CLEANERS.items():
        bronze_df = spark.read.format("delta").load(f"{BRONZE_PATH}/{name}")
        schema_report.append(check_schema_drift(bronze_df, name))

        silver_df = cleaner(bronze_df)
        out_path = f"{SILVER_PATH}/{name}"
        silver_df.write.format("delta").mode("overwrite").save(out_path)
        print(f"[silver] {name}: cleaned and written to {out_path}")

    return schema_report


if __name__ == "__main__":
    from utils.spark_session import get_spark
    spark = get_spark()
    report = run(spark)
    for r in report:
        print(r)
