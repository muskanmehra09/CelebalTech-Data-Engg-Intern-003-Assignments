"""
GOLD LAYER — aggregation mismatch
------------------------------------
Rolls Billing transactions up to a daily grain and compares against the
Analytics system's reported daily KPIs (total_customers, total_revenue,
avg_transaction). Flags any day where the two systems disagree beyond
tolerance, or where a day exists in one system but not the other.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from utils.config import SILVER_PATH, GOLD_PATH, AMOUNT_TOLERANCE_PCT


def run(spark: SparkSession):
    billing = spark.read.format("delta").load(f"{SILVER_PATH}/billing")
    analytics = spark.read.format("delta").load(f"{SILVER_PATH}/analytics")

    completed = billing.filter(F.col("status") == "completed").filter(F.col("transaction_date").isNotNull())

    daily_billing = (
        completed.groupBy(F.col("transaction_date").alias("date"))
        .agg(
            F.countDistinct("customer_id").alias("billing_total_customers"),
            F.sum("amount").alias("billing_total_revenue"),
            F.avg("amount").alias("billing_avg_transaction"),
        )
    )

    merged = analytics.join(daily_billing, on="date", how="full_outer")

    def pct_diff(a, b):
        return F.when(
            a.isNull() | b.isNull() | (b == 0), None
        ).otherwise(F.abs(a - b) / F.abs(b))

    merged = (
        merged
        .withColumn("customers_diff_pct", pct_diff(F.col("total_customers").cast("double"), F.col("billing_total_customers").cast("double")))
        .withColumn("revenue_diff_pct", pct_diff(F.col("total_revenue"), F.col("billing_total_revenue")))
        .withColumn("avg_txn_diff_pct", pct_diff(F.col("avg_transaction"), F.col("billing_avg_transaction")))
        .withColumn(
            "mismatch_flag",
            (F.coalesce(F.col("customers_diff_pct"), F.lit(0.0)) > AMOUNT_TOLERANCE_PCT)
            | (F.coalesce(F.col("revenue_diff_pct"), F.lit(0.0)) > AMOUNT_TOLERANCE_PCT)
            | (F.coalesce(F.col("avg_txn_diff_pct"), F.lit(0.0)) > AMOUNT_TOLERANCE_PCT)
            | F.col("total_customers").isNull()
            | F.col("billing_total_customers").isNull()
        )
    )

    merged.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/daily_aggregation_comparison")

    n_days = merged.count()
    n_mismatch = merged.filter(F.col("mismatch_flag")).count()
    n_missing_in_analytics = merged.filter(F.col("total_customers").isNull()).count()
    n_missing_in_billing = merged.filter(F.col("billing_total_customers").isNull()).count()
    avg_revenue_diff = merged.agg(F.avg("revenue_diff_pct")).first()[0]

    summary = {
        "days_compared": n_days,
        "days_missing_in_analytics": n_missing_in_analytics,
        "days_missing_in_billing": n_missing_in_billing,
        "days_with_mismatch": n_mismatch,
        "mismatch_rate_pct": round(n_mismatch / n_days * 100, 2) if n_days else None,
        "avg_revenue_diff_pct": round(avg_revenue_diff * 100, 2) if avg_revenue_diff is not None else None,
    }
    return summary


if __name__ == "__main__":
    from utils.spark_session import get_spark
    spark = get_spark()
    print(run(spark))
