# StayFree Core Data Validation Report

This report summarizes the data verification, transformation, and load (ETL) run for **StayFree screen-time data**.

## 📊 Summary Statistics

* **Processed Event Rows**: **18964** (Deduplicated & validated)
* **Processed Days**: **63** (Local IST Date Boundary)
* **Clean Events Ratio**: **88.44%**
* **Anomaly Records Filtered**: **2479**

## 🛡️ Anomalies and Quality Alerts

| Category | Count | Resolution Strategy |
| :--- | :---: | :--- |
| **Negative/Zero Durations** | 0 | Removed from core dataset to protect integrity. |
| **Impossible Long Durations** | 0 | Exceeded 24 hours focus. Filtered as crash anomalies. |
| **Invalid Timestamps** | 0 | Removed records lacking ISO timestamps. |
| **Duplicate Keys** | 2479 | Ignored records with matching MD5 hashes to prevent duplicate double-counting. |

## 🌟 Schema Compliance Check
* **stayfree_events**: Verified **22** fields. Deterministic Primary Key `event_id` verified.
* **stayfree_daily**: Verified **44** fields. Clean aggregation on `date_ist` timezone mapping verified.
