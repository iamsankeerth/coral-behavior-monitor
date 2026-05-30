# 🕸️ Personal Behavior & Health Monitor powered by Coral

An intelligent, local, privacy-first analytics pipeline and interactive dashboard that maps, transforms, and joins your digital screen-time patterns with your physical vitals using **Coral SQL**.

Built newly and explicitly for the **WeMakeDevs Coral Hackathon**.

---

## 🚀 Problem Statement
We track our digital lives across computers and mobile screens, and our physical health on fitness bands and phone logs. However, these databases remain isolated. You cannot query if spending 2 hours on YouTube Shorts or Instagram Reels late-night actively correlates with shorter deep sleep cycles, or which gaming habits are matched with sedentary (low-step) days. 

---

## ⚡ What Coral Does in This Project
Coral acts as the central query, reasoning, and schema layer. Rather than using Coral as a final export step, **Coral is the primary database layer**:
1. **Registers Schemas**: Mapped using the `coral_sources/behavior_monitor_local.yaml` configuration.
2. **Executes Cross-Source Joins**: Performs outer-join SQL queries linking **desktop/mobile web sessions** (StayFree) and **daily steps/sleep/workouts** (Health Connect).
3. **Derived Metrics**: Computes Focus Ratios and Bedtime Disruption Indexes dynamically using standard ANSI SQL queries.

---

## 📊 Mapped Data Sources
1. **StayFree Screen-Time Master**: Extracted local Edge browser LevelDB and synced Android events (**19,366 verified logs**).
2. **Health Connect Export**: SQLite database tracking daily steps, sleep phases (Light, Deep, REM), and workouts.

---

## 🏗️ Architecture Flow

```
+------------------------------------+      +------------------------------------+
|  StayFree LevelDB Folder (Copy)    |      |  Health Connect daily SQLite (GD)  |
|  (19,366 active sessions)          |      |  (Correlated local steps, sleep)   |
+-----------------+------------------+      +-----------------+------------------+
                  |                                           |
                  v (extract_stayfree.js)                     v (inspect_health_connect_db.py)
+-----------------+------------------+      +-----------------+------------------+
|  stayfree_events.csv / daily.csv   |      |  health_daily.csv / daily.jsonl    |
+-----------------+------------------+      +-----------------+------------------+
                  |                                           |
                  +--------------------+----------------------+
                                       | (Outer Join Key: date_ist)
                                       v
                  +--------------------+----------------------+
                  |  behavior_health_daily.csv (Master Join)  |
                  +--------------------+----------------------+
                                       |
                                       v (Registered YAML Source Schema)
                  +--------------------+----------------------+
                  |     🕸️ CORAL QUERY ENGINE SQL LAYER       |
                  +--------------------+----------------------+
                                       |
                                       v (SQL Sandbox Queries Execution)
                  +--------------------+----------------------+
                  |  Interactive Streamlit App Dashboard      |
                  +-------------------------------------------+
```

---

## 🛠️ Step-by-Step Setup

### 1. Pre-requisites
* Windows OS with PowerShell
* Python 3.10+ & Node.js 18+

### 2. Initialize Virtual Environment & Packages
Open your shell in the workspace and initialize:
```powershell
# Create & Activate Virtual Environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install Python mapping dependencies
pip install pyyaml streamlit pandas

# Install Node LevelDB extraction library
npm install classic-level --no-audit --no-fund
```

---

## 🏃 Running the Daily Pipeline

To perform a clean extraction, transform timezone structures, and compile the master behavior-health join, close Edge and run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_daily_coral_pipeline.ps1
```
*This script copies the databases safely (avoiding active write-locks), runs the LevelDB extraction, parses UTC-to-IST offsets, computes daily summaries, and executes the master join.*

---

## 🕸️ Exposing to Coral

### 1. Register Source
Expose the local files to your Coral engine:
```bash
# Validate YAML integrity
coral source lint coral_sources/behavior_monitor_local.yaml

# Register the source
coral source add --file coral_sources/behavior_monitor_local.yaml

# Test database connection
coral source test behavior_monitor_local
```

### 2. Run Diagnostic SQL Queries
You can query your master joined dataset directly using the Coral CLI.

#### Check Daily Step Totals & Screen Time:
```bash
coral sql "SELECT date_ist, steps_total, total_screen_minutes FROM behavior_monitor_local.behavior_health_daily LIMIT 5"
```

#### Exploring sleep duration vs. late-night screen time:
```bash
coral sql "SELECT date_ist, sleep_minutes, late_night_minutes FROM behavior_monitor_local.behavior_health_daily ORDER BY date_ist DESC LIMIT 10"
```

---

## 📊 Launching the Streamlit Dashboard
Visualize these insights and run interactive SQL queries through our premium dashboard:
```bash
streamlit run app/app.py
```
*Accessible at `http://localhost:8501`*

---

## 🛡️ Privacy and Safety Assurance
* **100% Local**: No raw browsing logs, precise GPS/step paths, or sensitive sleep states are ever uploaded to external cloud services.
* **No Causation Claimed**: All diagnostics are framed as statistical correlations and associations, preventing assertions of medical diagnosis.

---

## ⚠️ Limitations & Future Work
* **Reels/Shorts package granularity**: Synced Android events only contain the generic package names (`com.instagram.android` and `com.google.android.youtube`). Browser URLs provide `HIGH` confidence path detection, while mobile events degrade gracefully to `LOW` confidence.

---

## 🔮 Next Steps: Wire Your SQLite Health Connect DB Directly Using Coral's Official Google Drive Connector

While the local daily pipeline automates downloading and extracting the raw `health_connect_export.db` using local Python libraries, the ultimate architecture mounts Google Drive directly into the **Coral SQL Reasoning Engine**. 

You can configure Coral to mount your Google Drive folder as a live remote database source by utilizing the official **Coral Google Drive Source Connector**.

### 🛠️ Configuration Steps:

1. **Acquire the Connector**:
   The source definition and connector files can be found in the community sources repository:
   [Coral Google Drive Source Connector](https://github.com/withcoral/coral/tree/main/sources/community/google_drive)

2. **Define the Remote Source**:
   Create a new YAML source definition file at `coral_sources/behavior_monitor_drive.yaml`:
   ```yaml
   name: behavior_monitor_drive
   type: google_drive
   config:
     folder_name: "Data from Health Connect"
     credentials_file: "config/credentials.json"
     file_pattern: "*.db"
   tables:
     - name: steps_record_table
       path: "health_connect_export.db/steps_record_table"
     - name: exercise_session_record_table
       path: "health_connect_export.db/exercise_session_record_table"
     - name: total_calories_burned_record_table
       path: "health_connect_export.db/total_calories_burned_record_table"
   ```

3. **Mount the Source**:
   Register the remote Google Drive source directly in your Coral workspace:
   ```bash
   coral source add --file coral_sources/behavior_monitor_drive.yaml
   ```

4. **Query Directly in Real-Time**:
   Coral will seamlessly query your Google Drive folders dynamically over the wire!
   ```sql
   SELECT SUM(count) 
   FROM behavior_monitor_drive.steps_record_table 
   WHERE local_date = 20234;
   ```

