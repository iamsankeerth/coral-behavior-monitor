import csv
from datetime import datetime
import os
import json

csv_path = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\stayfree_clean_analytics.csv"
output_summary_path = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\stayfree_analysis_summary.json"

if not os.path.exists(csv_path):
    print(f"Error: CSV file not found at {csv_path}")
    exit(1)

total_events = 0
total_duration_sec = 0.0
platform_duration = {"android": 0.0, "web": 0.0}
platform_events = {"android": 0, "web": 0}

app_duration = {}
app_events = {}

daily_duration = {}
late_night_duration = 0.0 # 11:00 PM (23:00) to 5:00 AM (05:00)

earliest_time = None
latest_time = None

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_events += 1
        
        # Parse duration
        try:
            dur = float(row["duration_seconds"])
        except ValueError:
            dur = 0.0
            
        total_duration_sec += dur
        
        # Parse platform
        plat = row["platform"].lower()
        if plat not in platform_duration:
            platform_duration[plat] = 0.0
            platform_events[plat] = 0
        platform_duration[plat] += dur
        platform_events[plat] += 1
        
        # Parse domain or app
        app = row["domain_or_app"]
        app_duration[app] = app_duration.get(app, 0.0) + dur
        app_events[app] = app_events.get(app, 0) + 1
        
        # Parse timestamp
        time_str = row["date_or_timestamp"]
        if time_str and time_str != "N/A":
            try:
                # Handle ISO format like 2026-04-29T17:30:10.000Z
                dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                
                # Check earliest / latest
                if earliest_time is None or dt < earliest_time:
                    earliest_time = dt
                if latest_time is None or dt > latest_time:
                    latest_time = dt
                
                # Aggregate daily
                date_key = dt.strftime("%Y-%m-%d")
                daily_duration[date_key] = daily_duration.get(date_key, 0.0) + dur
                
                # Check late night (Hour in UTC/local based on string)
                if dt.hour >= 23 or dt.hour < 5:
                    late_night_duration += dur
            except Exception:
                pass

# Calculations
total_hours = total_duration_sec / 3600.0
android_hours = platform_duration.get("android", 0.0) / 3600.0
web_hours = platform_duration.get("web", 0.0) / 3600.0

distinct_days = len(daily_duration)
avg_daily_hours = total_hours / distinct_days if distinct_days > 0 else 0.0

# Sort apps by duration
sorted_apps = sorted(app_duration.items(), key=lambda x: x[1], reverse=True)
top_apps = []
for app, dur in sorted_apps[:15]:
    top_apps.append({
        "app_or_domain": app,
        "hours": dur / 3600.0,
        "percentage": (dur / total_duration_sec * 100.0) if total_duration_sec > 0 else 0.0,
        "sessions": app_events[app]
    })

# Formulate summary
summary = {
    "total_events": total_events,
    "total_hours": round(total_hours, 2),
    "date_range": {
        "earliest": earliest_time.isoformat() if earliest_time else "N/A",
        "latest": latest_time.isoformat() if latest_time else "N/A",
        "distinct_days_tracked": distinct_days
    },
    "platform_breakdown": {
        "android": {
            "hours": round(android_hours, 2),
            "percentage": round(android_hours / total_hours * 100.0, 2) if total_hours > 0 else 0.0,
            "events": platform_events.get("android", 0)
        },
        "web": {
            "hours": round(web_hours, 2),
            "percentage": round(web_hours / total_hours * 100.0, 2) if total_hours > 0 else 0.0,
            "events": platform_events.get("web", 0)
        }
    },
    "daily_metrics": {
        "average_hours_per_day": round(avg_daily_hours, 2),
        "late_night_hours": round(late_night_duration / 3600.0, 2),
        "late_night_percentage": round((late_night_duration / total_duration_sec * 100.0), 2) if total_duration_sec > 0 else 0.0
    },
    "top_15_apps": top_apps
}

with open(output_summary_path, "w", encoding="utf-8") as sf:
    json.dump(summary, sf, indent=2)

print("\n--- DATA ANALYSIS SUCCESSFUL ---")
print(f"Total Events Tracked: {total_events}")
print(f"Total Time Tracked: {total_hours:.2f} Hours")
print(f"Distinct Active Days: {distinct_days}")
print(f"Average Usage per Active Day: {avg_daily_hours:.2f} Hours")
print(f"Platform Splits: Android={android_hours:.2f}h ({android_hours/total_hours*100.0:.1f}%), Web={web_hours:.2f}h ({web_hours/total_hours*100.0:.1f}%)")
print(f"Late Night Usage: {late_night_duration/3600.0:.2f} Hours ({late_night_duration/total_duration_sec*100.0:.1f}%)")
print("\nTop 5 Apps/Domains:")
for i, item in enumerate(top_apps[:5]):
    print(f" {i+1}. {item['app_or_domain']} -> {item['hours']:.2f} hrs ({item['percentage']:.1f}%) in {item['sessions']} sessions")
