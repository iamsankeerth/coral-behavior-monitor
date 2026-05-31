import os
import sys
# Add scripts directory to path to support in-process imports from any context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import argparse
from coral_analytics_engine import CoralAnalyticsEngine

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
    
    # Initialize in-process analytics engine
    engine = CoralAnalyticsEngine()
    
    if args.timestamps:
        steps_ts = engine.get_steps_timestamp()
        pc_ts, mobile_ts = engine.get_stayfree_timestamps()
        
        print("\n*Retrieved live from local Coral SQL-join behavior database.*")
        if args.timestamps in ["physical", "all"]:
            print(f"*Mobile Steps data last updated: {steps_ts}")
        if args.timestamps in ["mental", "all"]:
            print(f"*PC Data last updated: {pc_ts}")
            print(f"*Mobile Screen data last updated: {mobile_ts}")
        return

    if args.all:
        # Runs sync in-process first, then prints the today's vitals & screen time summary
        summary = engine.get_vitals_summary()
        print(summary)
        return

    if args.sql:
        # Trigger the sync and SQL execution in-process
        result = engine.execute_query(args.sql, auto_sync=True)
        print(result)
        
        # Output relevant timestamps based on query terms
        sql_lower = args.sql.lower()
        is_physical = "step" in sql_lower or "workout" in sql_lower or "calorie" in sql_lower
        is_mental = "screen" in sql_lower or "reel" in sql_lower or "short" in sql_lower or "youtube" in sql_lower or "instagram" in sql_lower or "web" in sql_lower or "focus" in sql_lower or "app" in sql_lower or "domain" in sql_lower
        
        steps_ts = engine.get_steps_timestamp()
        pc_ts, mobile_ts = engine.get_stayfree_timestamps()
        
        print("\n### Data Freshness & Sync Timestamps")
        print("-" * 50)
        print("*Retrieved live from local Coral SQL-join behavior database.*")
        
        if is_physical and not is_mental:
            print(f"*Mobile Steps data last updated: {steps_ts}")
        elif is_mental and not is_physical:
            print(f"*PC Data last updated: {pc_ts}")
            print(f"*Mobile Screen data last updated: {mobile_ts}")
        else:
            print(f"*Mobile Steps data last updated: {steps_ts}")
            print(f"*PC Data last updated: {pc_ts}")
            print(f"*Mobile Screen data last updated: {mobile_ts}")
            
        print("\n*N/A: Sleep session and heart rate tables are empty in your source Health Connect database (no wearable linked). No mock assumptions are used.")
        return

    # Default help
    parser.print_help()

if __name__ == '__main__':
    main()
