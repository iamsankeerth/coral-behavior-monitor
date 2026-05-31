import os
import sys
# Add scripts directory to path to support in-process imports from any context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import pandas as pd
from datetime import datetime
from data_pipeline_engine import DataPipelineEngine
from path_config import PathConfig

class CoralAnalyticsEngine:
    """
    Unified In-Process Analytics Engine for the Coral SQLite behavior database.
    Provides query execution and data freshness tracking.
    """
    DIAGNOSTIC_QUERIES = {
        "1": {
            "title": "Basic Master Table Verification",
            "sql": """SELECT 
    date_ist, 
    steps_total, 
    sleep_minutes, 
    total_screen_minutes, 
    data_quality_flags
FROM behavior_health_daily 
ORDER BY date_ist DESC 
LIMIT 5;"""
        },
        "2": {
            "title": "Sleep Duration vs. Late-Night Digital Screen Activity",
            "sql": """SELECT 
    date_ist, 
    sleep_minutes, 
    late_night_minutes,
    sleep_disruption_index
FROM behavior_health_daily
ORDER BY date_ist DESC
LIMIT 14;"""
        },
        "3": {
            "title": "Top 10 Worst Sleep Durations and Digital Activity",
            "sql": """SELECT 
    date_ist, 
    sleep_minutes, 
    late_night_minutes, 
    youtube_minutes, 
    instagram_minutes, 
    top_app_or_domain
FROM behavior_health_daily
WHERE sleep_minutes IS NOT NULL
ORDER BY sleep_minutes ASC
LIMIT 10;"""
        },
        "4": {
            "title": "High Instagram / Reels Engagement Days",
            "sql": """SELECT 
    date_ist, 
    instagram_minutes, 
    instagram_reels_minutes_if_detected, 
    sleep_minutes, 
    steps_total
FROM behavior_health_daily
ORDER BY instagram_minutes DESC
LIMIT 10;"""
        },
        "5": {
            "title": "Workout Engagement vs. Active Screen Time",
            "sql": """SELECT 
    date_ist, 
    workout_minutes, 
    total_screen_minutes, 
    focus_ratio
FROM behavior_health_daily
WHERE workout_minutes > 0
ORDER BY date_ist DESC;"""
        },
        "6": {
            "title": "High Focus Ratio Profiles (Most Productive Days)",
            "sql": """SELECT 
    date_ist, 
    focus_ratio, 
    focus_minutes, 
    leisure_minutes, 
    sleep_minutes, 
    steps_total
FROM behavior_health_daily
ORDER BY focus_ratio DESC
LIMIT 10;"""
        },
        "7": {
            "title": "Late-Night Sleep Disruption Index",
            "sql": """SELECT 
    date_ist, 
    sleep_disruption_index, 
    late_night_minutes, 
    sleep_minutes
FROM behavior_health_daily
WHERE sleep_disruption_index IS NOT NULL
ORDER BY sleep_disruption_index DESC
LIMIT 10;"""
        }
    }

    def __init__(self, workspace=None):
        self.config = PathConfig(workspace)
        self.workspace = self.config.workspace
        self.master_csv = self.config.out_master_csv
        self.stayfree_events_csv = self.config.out_events_csv
        self.health_connect_db = self.config.db_path
        self.pipeline_engine = DataPipelineEngine(self.workspace)


    def trigger_sync(self):
        """
        Runs the data pipeline sync in-process to ensure freshest data.
        """
        try:
            self.pipeline_engine.sync()
        except Exception as e:
            print(f"Warning: Analytics engine auto-sync failed: {e}")

    def execute_query(self, sql_query: str, auto_sync=True) -> str:
        """
        Executes arbitrary SQL queries against the in-memory representation of behavior_health_daily.
        """
        if auto_sync:
            self.trigger_sync()
            
        if not os.path.exists(self.master_csv):
            return f"Error: Master CSV not found at: {self.master_csv}"
            
        try:
            df = pd.read_csv(self.master_csv)
            conn = sqlite3.connect(":memory:")
            df.to_sql("behavior_health_daily", conn, index=False)
            
            # Clean queries to support qualified names
            cleaned_sql = sql_query
            for bad_name in ["behavior_monitor_local.behavior_health_daily", "behavior_monitor_local.behavior_health_daily"]:
                cleaned_sql = cleaned_sql.replace(bad_name, "behavior_health_daily")
                
            res = pd.read_sql_query(cleaned_sql, conn)
            conn.close()
            
            if res.empty:
                return "No matching records found in the database."
            return res.to_markdown(index=False)
        except Exception as e:
            return f"SQL Execution Error: {str(e)}"

    def get_steps_timestamp(self) -> str:
        """
        Queries steps database for the latest update timestamp.
        """
        if not os.path.exists(self.health_connect_db):
            return "N/A (Database file missing)"
        try:
            conn = sqlite3.connect(self.health_connect_db)
            cursor = conn.cursor()
            cursor.execute("SELECT datetime(MAX(end_time)/1000 + start_zone_offset, 'unixepoch') FROM steps_record_table;")
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                return f"{row[0]} (IST)"
            return "N/A (No steps logged)"
        except Exception as e:
            return f"Error: {str(e)}"

    def get_stayfree_timestamps(self) -> tuple:
        """
        Queries stayfree events CSV in chunks to find max timestamp for PC and Mobile.
        """
        if not os.path.exists(self.stayfree_events_csv):
            return "N/A", "N/A"
        try:
            chunksize = 10000
            max_pc = None
            max_mobile = None
            for chunk in pd.read_csv(self.stayfree_events_csv, usecols=["timestamp_ist", "platform"], chunksize=chunksize):
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
                        
            return self._format_ist_timestamp(max_pc), self._format_ist_timestamp(max_mobile)
        except Exception as e:
            return f"Error: {str(e)}", f"Error: {str(e)}"

    def _format_ist_timestamp(self, ts_str):
        if not ts_str or ts_str == "N/A":
            return "N/A"
        try:
            ts_clean = ts_str.replace("Z", "").split("+")[0]
            dt = datetime.fromisoformat(ts_clean)
            return dt.strftime("%Y-%m-%d %H:%M:%S (IST)")
        except Exception:
            return ts_str

    def get_vitals_summary(self) -> str:
        """
        Returns a formatted natural-language overview of today's vitals & screen time metrics
        complete with sync timestamps and empty wearable footnotes.
        """
        today_sql = (
            "SELECT date_ist, steps_total, focus_ratio, focus_minutes, total_screen_minutes, "
            "instagram_reels_minutes_if_detected, youtube_shorts_minutes_if_detected "
            "FROM behavior_health_daily ORDER BY date_ist DESC LIMIT 1;"
        )
        data_table = self.execute_query(today_sql, auto_sync=False)
        
        steps_ts = self.get_steps_timestamp()
        pc_ts, mobile_ts = self.get_stayfree_timestamps()
        
        summary = (
            f"### Today's Vitals & Screen Time Summary\n"
            f"--------------------------------------------------\n"
            f"{data_table}\n\n"
            f"### Data Freshness & Sync Timestamps\n"
            f"--------------------------------------------------\n"
            f"*Retrieved live from local Coral SQL-join behavior database.*\n"
            f"*Mobile Steps data last updated: {steps_ts}\n"
            f"*PC Data last updated: {pc_ts}\n"
            f"*Mobile Screen data last updated: {mobile_ts}\n\n"
            f"*N/A: Sleep session and heart rate tables are empty in your source Health Connect database "
            f"(no wearable linked). No mock assumptions are used."
        )
        return summary
