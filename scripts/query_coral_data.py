import os
import sys
# Add scripts directory to path to support in-process imports from any context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from coral_analytics_engine import CoralAnalyticsEngine
from path_config import PathConfig

def main():
    print("="*80)
    print("🕸️  WELCOME TO THE CORAL SQL INTERACTIVE CONSOLE EMULATOR")
    print("="*80)
    
    # Initialize PathConfig and CoralAnalyticsEngine
    config = PathConfig()
    analytics_engine = CoralAnalyticsEngine(config.workspace)
    
    if not os.path.exists(analytics_engine.master_csv):
        print(f"❌ Error: Master CSV not found at: {analytics_engine.master_csv}")
        print("Please run the daily pipeline first!")
        return

    print(f"✅ Connected to the local Coral SQL behavior analytics engine.")
    print("Pre-configured Diagnostic Queries available:")
    for num, q in analytics_engine.DIAGNOSTIC_QUERIES.items():
        print(f"  [{num}] {q['title']}")
    print("  [q] Quit Console\n")
    
    while True:
        choice = input("Enter query number (1-7), type custom SQL, or 'q' to quit: ").strip()
        if choice.lower() == 'q':
            print("Exiting console. Stay healthy!")
            break
            
        if choice in analytics_engine.DIAGNOSTIC_QUERIES:
            selected = analytics_engine.DIAGNOSTIC_QUERIES[choice]
            print(f"\nRunning Query [{choice}]: {selected['title']}")
            print("-" * 80)
            print(selected['sql'])
            print("-" * 80)
            
            # Execute through CoralAnalyticsEngine (no auto_sync for fast console response)
            res = analytics_engine.execute_query(selected['sql'], auto_sync=False)
            print(res)
            print("\n" + "="*80 + "\n")
        else:
            if not choice:
                continue
            # Run custom SQL
            print(f"\nRunning custom SQL query...")
            res = analytics_engine.execute_query(choice, auto_sync=False)
            print(res)
            print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
