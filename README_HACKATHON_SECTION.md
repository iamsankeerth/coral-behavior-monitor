# 🏆 Hackathon Spotlight: Why Coral is Central

This project is built **specifically and newly** for the **WeMakeDevs Coral Hackathon**. Rather than treating Coral as a post-processing export or final reporting step, **Coral is the primary engine** of the entire application.

---

## ⚡ Core Coral Features Utilized

1. **Coral Local SQL Source Integration**:
   * We configured a structured schema configuration in `coral_sources/behavior_monitor_local.yaml` to register and expose 4 unified tables to Coral's SQL engine.
2. **Cross-Source Database Joins**:
   * We executed ANSI SQL queries joining two completely separate real-world data scopes: **desktop/mobile web sessions** (StayFree) and **vitals/sleep metrics** (Health Connect).
3. **Coral SQL CLI Execution**:
   * The pipeline utilizes the Coral query processor to compute focus scores, daily splits, and bedtime sleep correlations directly from files without requiring heavy databases.

---

## 🏗️ Text Architecture Diagram

```
+------------------------------------------+
|  StayFree LevelDB (Copy)                 |
|  (19,366 raw sessions)                   |
+-------------------+----------------------+
                    |
                    v (extract_stayfree.js)
+-------------------+----------------------+
|  stayfree_events.csv / stayfree_daily.csv|
+-------------------+----------------------+
                    |
                    | (Outer Join Key: date_ist) <---+
                    v                                 |
+-------------------+----------------------+          |
|  behavior_health_daily.csv (Master Join) |          |
+-------------------+----------------------+          |
                    |                                 |
                    v (Registered YAML Source)        |
+-------------------+----------------------+          |
|       🕸️ CORAL QUERY ENGINE SQL LAYER    |          |
+-------------------+----------------------+          |
                    |                                 |
                    v                                 |
+-------------------+----------------------+          |
|  Interactive Streamlit App Dashboard     |          |
|  (Local SQL Sandbox Tab)                 |          |
+------------------------------------------+          |
                                                      |
+------------------------------------------+          |
|  Health Connect daily SQLite (GDrive)    |----------+
|  (Correlated local steps, sleep)         |
+------------------------------------------+
```

---

## 🔒 Absolute Local Data Privacy
* Health metrics and detailed browsing logs are highly sensitive personal information.
* **Our Promise**: Zero bits of your raw logs are uploaded anywhere!
* The V8 database lock states and large raw JSON copies are strictly `.gitignored`. Coral reads clean, anonymous daily aggregates and registers them locally. Your data remains **your data**.
