# 🌸 CelebalTech Data Engineering Internship — Assignments Portfolio

Welcome to my pastel‑aesthetic showcase of **CelebalTech Data Engineering Internship (Assignments 1–8)**.  
This repository reflects my journey of learning, building, and presenting data engineering tasks with a blend of **technical depth + creative clarity** 💎  

---

## 🧠 Assignment 1 — Python Basics & Data Exploration
- Practiced Python fundamentals with Pandas.
- Explored datasets using `head()`, `tail()`, and `info()`.
- Understood data types and basic cleaning.

## 🧹 Assignment 2 — Data Cleaning & Transformation
- Handled missing values and duplicates.
- Applied transformations for structured datasets.
- Exported cleaned data for analysis.

## 📊 Assignment 3 — Data Aggregation & Analysis
- Implemented `groupby`, pivot tables, and KPIs.
- Derived insights like category‑wise sales and profit.
- Enhanced readability with formatted outputs.

## 🧾 Assignment 4 — Delta Lake MERGE Implementation
- Learned upsert operations and dataset versioning.
- Practiced scalable data handling with Delta Lake.
- Combined Python + Databricks workflows.

## ⚙️ Assignment 5 — Data Validation & Integrity
- Built validation checks for schema consistency.
- Ensured accuracy and reliability of datasets.
- Documented validation logic for audit readiness.

## 🔄 Assignment 6 — Data Transformation Pipeline
- Designed a mini ETL pipeline with joins and derivations.
- Focused on modular, reusable code.
- Simulated real‑world data flow.

## 🧮 Assignment 7 — Superstore Data Cleaning
- Cleaned Superstore dataset using Pandas.
- Created derived column `total_amount = price * quantity`.
- Exported cleaned CSV + notebook proof.

## 🛍️ Assignment 8 — E‑Commerce Order Analytics System
- Developed analytics workflow for e‑commerce orders.
- Cleaned inconsistent data, wrote SQL queries for segmentation, revenue trends, and cohort analysis.
- Delivered notebook, SQL script, and proof screenshots.

---



# 🔄 Project Task — Cross System Data Drift

## 📖 Description
This project focuses on building a system that compares data across **CRM, Billing, and Analytics systems** to ensure consistency and reliability.  
The goal is to detect and resolve **data quality issues** such as:
- Missing records  
- Duplicate entries  
- Value mismatches  
- Data drift over time  

The system also calculates a **Data Trust Score** to measure overall data integrity and presents results in a clear, structured format for stakeholders.

---

## 🖥️ Implementation (Python Draft)

```python

import pandas as pd

# Load sample datasets
crm = pd.read_csv("CRM.csv")
billing = pd.read_csv("Billing.csv")
analytics = pd.read_csv("Analytics.csv")

# 1. Missing records
missing_in_billing = crm[~crm["OrderID"].isin(billing["OrderID"])]

# 2. Duplicate entries
duplicates = billing[billing.duplicated("OrderID")]

# 3. Value mismatches
mismatch = crm.merge(billing, on="OrderID")
mismatch = mismatch[mismatch["Amount_x"] != mismatch["Amount_y"]]

# 4. Data drift (monthly average comparison)
crm_monthly = crm.groupby("Month")["Amount"].mean()
billing_monthly = billing.groupby("Month")["Amount"].mean()
drift = crm_monthly - billing_monthly

# 5. Data Trust Score
valid_records = len(crm) - len(missing_in_billing) - len(duplicates) - len(mismatch)
trust_score = (valid_records / len(crm)) * 100
print("Data Trust Score:", trust_score)

## ✨ Outcome
This repo captures my **end‑to‑end data engineering journey** — from Python basics to advanced SQL analytics.  
It’s not just assignments, it’s a **classy pastel portfolio** that blends technical precision with aesthetic clarity 🌷💫  

---
