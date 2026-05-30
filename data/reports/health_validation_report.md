# Health Connect Core Data Validation Report

This report summarizes the daily physical health aggregates generated in the **Health Connect Drive pipeline**.

## 🏃 Summary Statistics
* **Data Source**: **REAL_DATABASE**
* **Processed Days**: **62** (Aligned with StayFree dates)
* **Average Daily Steps**: **13251.11** steps
* **Average Daily Sleep**: **6.84** hours (410.26 minutes)
* **Total Workout Sessions**: **11** active exercises logged

## 🛡️ Pipeline Mappings
* **Real SQLite Integration**: Steps, logged workouts, and daily calorie totals parsed from standard Health Connect SQLite tables.
* **Correlated Sleep Modeling**: Correlated sleep metrics modeled against StayFree late-night screen times where sleep sessions are blank in source.
