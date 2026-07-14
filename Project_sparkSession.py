"""
Spark session factory.

On Databricks, `spark` is already provided in the notebook context, so
`get_spark()` simply returns it. This wrapper exists so the same code
can also run on a local Spark install for testing outside Databricks.
"""

from pyspark.sql import SparkSession


def get_spark(app_name: str = "cross-system-data-drift-trust-platform") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )
