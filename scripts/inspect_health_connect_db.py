import os
import sys
# Add scripts directory to path to support in-process imports from any context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
from path_config import PathConfig

config = PathConfig()
report_md_path = os.path.join(config.report_dir, "health_connect_schema_report.md")
report_json_path = os.path.join(config.report_dir, "health_connect_schema_report.json")

os.makedirs(os.path.dirname(report_md_path), exist_ok=True)

def inspect_health():
    print("Health Connect Google Drive Connection Architect Tool")
    print("Configured to mount via direct Coral Google Drive MCP/Source Connector later.")
    
    # Write a highly descriptive audit report
    report_json = {
        "status": "INTEGRATION_DRAFT",
        "configured_source": "https://github.com/withcoral/coral/tree/main/sources/community/google_drive",
        "description": "User has chosen to integrate Google Drive directly into Coral. A local health data generator is active to seed behavior-health daily joints with mock metrics for testing.",
        "schema_mapped": {
            "steps_table": "health_daily.steps_total",
            "sleep_table": "health_daily.sleep_minutes",
            "workout_table": "health_daily.workout_minutes"
        }
    }
    
    with open(report_json_path, "w", encoding="utf-8") as rj:
        json.dump(report_json, rj, indent=2)
        
    report_md = """# Health Connect Schema Integration Report

This report outlines the strategy for connecting your **Google Drive Health Connect Daily Backup** directly to Coral using the official Google Drive Source Connector.

## 🚀 Target Connection Pipeline
```mermaid
graph LR
    A[Google Drive Daily SQLite Export] -->|Coral Google Drive Source| B[Coral SQL Reasoning Layer]
    C[StayFree Local Settings LevelDB] -->|Coral Local CSV/JSONL Source| B
    B -->|Cross-Source Join| D[behavior_health_daily master]
```

## 🛠️ Schema Mapping Mappings

The Google Drive SQL DB maps to the following standard **Health Connect Data Contract** columns:
* **Steps**: Extracted from daily record counts.
* **Sleep**: Extracted from Android Health Sleep sessions, mapped to local wake-up date.
* **Workouts**: Compiled from Exercise sessions.

## 🌟 Local Sandbox Seeding
Until the Coral Google Drive remote source is fully mounted, the project pipeline generates a highly realistic, statistically correlated local daily health table (`health_daily.csv`) matching your exact date range, facilitating full local SQL cross-joins!
"""
    with open(report_md_path, "w", encoding="utf-8") as rm:
        rm.write(report_md)
        
    print("Successfully wrote Health Connect schema reports.")

if __name__ == '__main__':
    inspect_health()
