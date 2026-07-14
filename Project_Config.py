"""
Central configuration: paths, expected schemas, and thresholds.
Adjust BASE_PATH to point at your Databricks workspace / DBFS / Unity Catalog
volume path, or a local path when testing.
"""

BASE_PATH = "/mnt/data_drift_platform"   # change to your DBFS / volume mount

RAW_PATH = f"{BASE_PATH}/raw"
BRONZE_PATH = f"{BASE_PATH}/bronze"
SILVER_PATH = f"{BASE_PATH}/silver"
GOLD_PATH = f"{BASE_PATH}/gold"

RAW_FILES = {
    "crm": f"{RAW_PATH}/crm_dataset.csv",
    "billing": f"{RAW_PATH}/billing_dataset.csv",
    "analytics": f"{RAW_PATH}/analytics_dataset.csv",
}

EXPECTED_SCHEMAS = {
    "crm": ["customer_id", "name", "email", "signup_date", "city"],
    "billing": ["transaction_id", "customer_id", "amount", "transaction_date", "status"],
    "analytics": ["date", "total_customers", "total_revenue", "avg_transaction"],
}

PLACEHOLDER_VALUES = ["UNKNOWN", "XX_CITY", "N/A", "NULL", ""]

# Tolerance before a daily aggregation is flagged as a mismatch
AMOUNT_TOLERANCE_PCT = 0.02  # 2%

# Trust score weights (must sum to 1.0)
TRUST_WEIGHTS = {
    "completeness": 0.30,
    "uniqueness": 0.20,
    "consistency": 0.35,
    "stability": 0.15,
}

# Volume drift: rolling window (days) + z-score anomaly threshold
VOLUME_DRIFT_WINDOW = 30
VOLUME_DRIFT_ZSCORE_THRESHOLD = 3.0

# Distribution drift: comparison window (days) + shift thresholds
DIST_DRIFT_WINDOW_DAYS = 90
DIST_DRIFT_MEAN_SHIFT_PCT = 15.0
DIST_DRIFT_STD_SHIFT_PCT = 25.0
