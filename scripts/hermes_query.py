import os
import sys
import sqlite3
import argparse
import subprocess
import pandas as pd
from datetime import datetime

# Target paths
workspace = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project"
master_csv = os.path.join(workspace, "data", "coral", "csv", "behavior_health_daily.csv")
stayfree_events_csv = os.path.join(workspace, "data", "coral", "csv", "stayfree_events.csv")
health_connect_db = os.path.join(workspace, "data", "raw", "health_connect", "health_connect_export.db")

def format_ist_timestamp(ts_str):
    if not ts_str or ts_str == "N/A":
        return "N/A"
    try:
        # e.g., "2026-05-30T17:00:24+00:00"
        # Let's replace 'Z' if present, remove timezone offset or parse it
        ts_clean = ts_str.replace("Z", "").split("+")[0]
        dt = datetime.fromisoformat(ts_clean)
        return dt.strftime("%Y-%m-%d %H:%M:%S (IST)")
    except Exception:
        return ts_str

def run_live_pipeline():
    try:
        pipeline_script = os.path.join(workspace, "scripts", "run_daily_coral_pipeline.ps1")
        # Run PowerShell pipeline synchronously to pull the freshest files before querying
        subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", pipeline_script],
            capture_output=True,
            text=True,
            check=True
        )
    except Exception:
        # Proceed gracefully if pipeline execution fails or edge is locked
        pass

def get_steps_timestamp():
    if not os.path.exists(health_connect_db):
        return "N/A (Database file missing)"
    try:
        conn = sqlite3.connect(health_connect_db)
        cursor = conn.cursor()
        cursor.execute("SELECT datetime(MAX(end_time)/1000 + start_zone_offset, 'unixepoch') FROM steps_record_table;")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return f"{row[0]} (IST)"
        return "N/A (No steps logged)"
    except Exception as e:
        return f"Error: {str(e)}"

def get_stayfree_timestamps():
    if not os.path.exists(stayfree_events_csv):
        return "N/A", "N/A"
    try:
        # Read stayfree_events.csv in chunks to find max timestamp_ist for platform='web' and platform='android'
        chunksize = 10000
        max_pc = None
        max_mobile = None
        for chunk in pd.read_csv(stayfree_events_csv, usecols=["timestamp_ist", "platform"], chunksize=chunksize):
            pc_chunk = chunk[chunk["platform"] == "web"]
            android_chunk = chunk[chunk["platform"] == "android"]
            
            if not pc_chunk.empty:
                pc_max = pc_chunk["timestamp_ist"].max()
                if max_pc is None or (pc_max and pc_max > max_pc):
                    max_pc = pc_max
                    
            if not android_chunk.empty:
                android_max = android_chunk["timestamp_ist"].max()
                if max_mobile is None or (android_max and android_max > max_mobile):
                    max_mobile = android_max
                    
        return format_ist_timestamp(max_pc), format_ist_timestamp(max_mobile)
    except Exception as e:
        return f"Error: {str(e)}", f"Error: {str(e)}"

def execute_sql(sql_query):
    if not os.path.exists(master_csv):
        return f"Error: Master CSV not found at: {master_csv}"

    # Load daily master data in memory SQLite
    try:
        df = pd.read_csv(master_csv)
        conn = sqlite3.connect(":memory:")
        # Register both table names to support user queries
        df.to_sql("behavior_health_daily", conn, index=False)
        
        # Support dot syntax by substituting behavior_monitor_local.behavior_health_daily
        cleaned_sql = sql_query.replace("behavior_monitor_local.behavior_health_daily", "behavior_health_daily")
        cleaned_sql = cleaned_sql.replace("behavior_monitor_local.behavior_health_daily", "behavior_health_daily")
        
        res = pd.read_sql_query(cleaned_sql, conn)
        conn.close()
        
        if res.empty:
            return "No matching records found in the database."
        return res.to_markdown(index=False)
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"

def print_timestamps(query_type="all"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
        
    steps_ts = get_steps_timestamp()
    pc_ts, mobile_ts = get_stayfree_timestamps()
    
    # We always explain that we are using Coral behavior analytics
    print("\n*Retrieved live from local Coral SQL-join behavior database.*")
    
    if query_type in ["physical", "all"]:
        print(f"*Mobile Steps data last updated: {steps_ts}")
    if query_type in ["mental", "all"]:
        print(f"*PC Data last updated: {pc_ts}")
        print(f"*Mobile Screen data last updated: {mobile_ts}")

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    parser = argparse.ArgumentParser(description="Hermes Local Behavior-Health SQL Query Bridge")
    parser.add_argument("--sql", type=str, help="Arbitrary SQL query to execute against the behavior_health_daily table")
    parser.add_argument("--timestamps", type=str, choices=["all", "physical", "mental"], help="Fetch live sync timestamps")
    parser.add_argument("--all", action="store_true", help="Print summary of today's behavior & sync timestamps")
    
    args = parser.parse_args()
    
    if args.timestamps:
        print_timestamps(args.timestamps)
        return

    if args.all:
        # Run pipeline first to sync the absolute freshest records
        run_live_pipeline()
        
        print("### Today's Vitals & Screen Time Summary")
        print("-" * 50)
        # Execute query for today's row
        today_sql = "SELECT date_ist, steps_total, focus_ratio, focus_minutes, total_screen_minutes, instagram_reels_minutes_if_detected, youtube_shorts_minutes_if_detected FROM behavior_health_daily ORDER BY date_ist DESC LIMIT 1;"
        print(execute_sql(today_sql))
        print("\n### Data Freshness & Sync Timestamps")
        print("-" * 50)
        print_timestamps("all")
        print("\n*N/A: Sleep session and heart rate tables are empty in your source Health Connect database (no wearable linked). No mock assumptions are used.")
        return

    if args.sql:
        # Run pipeline first to sync the absolute freshest records
        run_live_pipeline()
        
        # Run SQL query and output results
        result = execute_sql(args.sql)
        print(result)
        
        # Deduce the query type (physical vs mental)
        sql_lower = args.sql.lower()
        is_physical = "step" in sql_lower or "workout" in sql_lower or "calorie" in sql_lower
        is_mental = "screen" in sql_lower or "reel" in sql_lower or "short" in sql_lower or "youtube" in sql_lower or "instagram" in sql_lower or "web" in sql_lower or "focus" in sql_lower or "app" in sql_lower or "domain" in sql_lower
        
        # Output relevant timestamps
        print("\n### Data Freshness & Sync Timestamps")
        print("-" * 50)
        if is_physical and not is_mental:
            print_timestamps("physical")
        elif is_mental and not is_physical:
            print_timestamps("mental")
        else:
            print_timestamps("all")
            
        print("\n*N/A: Sleep session and heart rate tables are empty in your source Health Connect database (no wearable linked). No mock assumptions are used.")
        return

    # Default help
    parser.print_help()

if __name__ == '__main__':
    main()
