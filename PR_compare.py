"""
SILVER LAYER — cross-system comparison
----------------------------------------
Record-level and field-level comparison between CRM and Billing:
- Duplicate detection (within each system)
- Missing / orphan record detection (billing referencing unknown customers)
- Field-level completeness checks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from utils.config import SILVER_PATH


def run(spark: SparkSession):
    crm = spark.read.format("delta").load(f"{SILVER_PATH}/crm")
    billing = spark.read.format("delta").load(f"{SILVER_PATH}/billing")

    n_crm = crm.count()
    n_billing = billing.count()

    # --- Duplicate detection ---
    crm_dupes = (
        crm.groupBy("customer_id").count().filter(F.col("count") > 1)
    )
    n_crm_dupes = crm_dupes.agg(F.sum(F.col("count") - 1)).first()[0] or 0

    billing_dupes = (
        billing.groupBy("transaction_id").count().filter(F.col("count") > 1)
    )
    n_billing_dupes = billing_dupes.agg(F.sum(F.col("count") - 1)).first()[0] or 0

    # --- Missing / orphan records: billing customer_id not present in CRM ---
    orphan_billing = billing.join(crm.select("customer_id"), on="customer_id", how="left_anti")
    n_orphan = orphan_billing.count()

    # --- Extra records: CRM customers who never appear in billing ---
    customers_no_txn = crm.select("customer_id").join(
        billing.select("customer_id").distinct(), on="customer_id", how="left_anti"
    )
    n_no_txn = customers_no_txn.count()

    # --- Field-level completeness ---
    n_missing_email = crm.filter(F.col("email").isNull()).count()
    n_missing_city = crm.filter(F.col("city").isNull()).count()
    n_missing_amount = billing.filter(F.col("amount").isNull()).count()

    results = {
        "crm_row_count": n_crm,
        "billing_row_count": n_billing,
        "crm_duplicate_customer_ids": int(n_crm_dupes),
        "billing_duplicate_transaction_ids": int(n_billing_dupes),
        "billing_orphan_records": n_orphan,
        "billing_orphan_pct": round(n_orphan / n_billing * 100, 2) if n_billing else None,
        "crm_customers_with_no_transactions": n_no_txn,
        "crm_missing_email": n_missing_email,
        "crm_missing_city": n_missing_city,
        "billing_missing_amount": n_missing_amount,
    }

    # Persist detail tables for investigation
    orphan_billing.write.format("delta").mode("overwrite").save(f"{SILVER_PATH}/_orphan_billing_records")
    crm_dupes.write.format("delta").mode("overwrite").save(f"{SILVER_PATH}/_duplicate_crm_customer_ids")

    return results


if __name__ == "__main__":
    from utils.spark_session import get_spark
    spark = get_spark()
    print(run(spark))
