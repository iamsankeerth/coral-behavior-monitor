import os
import sqlite3
import pandas as pd

# Target paths
workspace = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project"
master_csv = os.path.join(workspace, "data", "coral", "csv", "behavior_health_daily.csv")

# Diagnostic Queries Map
QUERIES = {
    "1": {
        "title": "Basic Master Table Verification",
        "sql": """SELECT 
    date_ist, 
    steps_total, 
    sleep_minutes, 
    total_screen_minutes, 
    data_quality_flags
FROM behavior_monitor_local.behavior_health_daily 
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
FROM behavior_monitor_local.behavior_health_daily
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
FROM behavior_monitor_local.behavior_health_daily
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
FROM behavior_monitor_local.behavior_health_daily
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
FROM behavior_monitor_local.behavior_health_daily
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
FROM behavior_monitor_local.behavior_health_daily
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
FROM behavior_monitor_local.behavior_health_daily
WHERE sleep_minutes IS NOT NULL
ORDER BY sleep_disruption_index DESC
LIMIT 10;"""
    }
}

def execute_query(sql, conn):
    # Support Coral dot syntax inside Python sqlite by replacing it
    cleaned_sql = sql.replace("behavior_monitor_local.behavior_health_daily", "behavior_health_daily")
    try:
        res = pd.read_sql_query(cleaned_sql, conn)
        return res, None
    except Exception as e:
        return None, str(e)

def main():
    print("="*80)
    print("🕸️  WELCOME TO THE CORAL SQL INTERACTIVE CONSOLE EMULATOR")
    print("="*80)
    
    if not os.path.exists(master_csv):
        print(f"❌ Error: Master CSV not found at: {master_csv}")
        print("Please run the PowerShell pipeline first!")
        return

    # Load data in memory SQLite
    df = pd.read_csv(master_csv)
    conn = sqlite3.connect(":memory:")
    df.to_sql("behavior_health_daily", conn, index=False)
    
    print(f"✅ Loaded {len(df)} days of verified master aggregates.")
    print("Pre-configured Diagnostic Queries available:")
    for num, q in QUERIES.items():
        print(f"  [{num}] {q['title']}")
    print("  [q] Quit Console\n")
    
    while True:
        choice = input("Enter query number (1-7), type custom SQL, or 'q' to quit: ").strip()
        if choice.lower() == 'q':
            print("Exiting console. Stay healthy!")
            break
            
        if choice in QUERIES:
            selected = QUERIES[choice]
            print(f"\nRunning Query [{choice}]: {selected['title']}")
            print("-" * 80)
            print(selected['sql'])
            print("-" * 80)
            
            res, err = execute_query(selected['sql'], conn)
            if err:
                print(f"❌ SQL Execution Error: {err}\n")
            else:
                print(res.to_markdown(index=False))
                print("\n" + "="*80 + "\n")
        else:
            if not choice:
                continue
            # Run custom SQL
            print(f"\nRunning custom SQL query...")
            res, err = execute_query(choice, conn)
            if err:
                print(f"❌ SQL Execution Error: {err}\n")
            else:
                print(res.to_markdown(index=False))
                print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
