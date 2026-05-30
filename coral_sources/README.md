# Coral Source Registration Guide

This directory houses the Coral source configuration exposing your personal metrics database to the Coral reasoning and SQL execution engine.

---

## 🛠️ Commands to Register and Test

### 1. Verify Configuration Integrity (Lint)
Before loading into Coral, verify the YAML syntax and column schema mapping:
```bash
coral source lint coral_sources/behavior_monitor_local.yaml
```

### 2. Register Source into Coral
Add the local file-backed source to the active Coral database schema context:
```bash
coral source add --file coral_sources/behavior_monitor_local.yaml
```

### 3. Verify Active Tables Connection
Ensure Coral can read the CSV database paths and initialize active schema engines:
```bash
coral source test behavior_monitor_local
```

### 4. Execute Diagnostic SQL Queries
You can run any SQL queries from `test_queries.sql` directly using the Coral CLI. 

#### Basic Verification Query:
```bash
coral sql "SELECT * FROM behavior_monitor_local.behavior_health_daily LIMIT 5"
```

#### Correlate sleep duration against late-night focus:
```bash
coral sql "SELECT date_ist, sleep_minutes, late_night_minutes FROM behavior_monitor_local.behavior_health_daily ORDER BY date_ist DESC LIMIT 7"
```

---

## 🗂️ Exposed Coral Tables
* **`behavior_monitor_local.stayfree_events`**: Event-level screen sessions (web and synced Android).
* **`behavior_monitor_local.stayfree_daily`**: Daily aggregated screen focus.
* **`behavior_monitor_local.health_daily`**: Daily steps, workouts, and sleep metrics.
* **`behavior_monitor_local.behavior_health_daily`**: Unified master behavioral join table.
