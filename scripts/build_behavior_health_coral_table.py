import os
import csv
import json
from datetime import datetime, timedelta

# Define source paths
stayfree_daily_csv = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\csv\stayfree_daily.csv"
health_daily_csv = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\csv\health_daily.csv"

# Target paths
out_master_csv = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\csv\behavior_health_daily.csv"
out_master_jsonl = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\jsonl\behavior_health_daily.jsonl"

report_md_path = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\reports\master_validation_report.md"
report_json_path = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\reports\master_validation_report.json"

os.makedirs(os.path.dirname(out_master_csv), exist_ok=True)
os.makedirs(os.path.dirname(out_master_jsonl), exist_ok=True)
os.makedirs(os.path.dirname(report_md_path), exist_ok=True)

def build_master_table():
    print("Building behavior_health_daily Coral Master Table...")
    
    # 1. Load StayFree Daily
    stayfree_data = {}
    if os.path.exists(stayfree_daily_csv):
        with open(stayfree_daily_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stayfree_data[row["date_ist"]] = row
                
    # 2. Load Health Daily
    health_data = {}
    if os.path.exists(health_daily_csv):
        with open(health_daily_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                health_data[row["date_ist"]] = row
                
    # Get all unique dates sorted
    all_dates = sorted(list(set(stayfree_data.keys()).union(set(health_data.keys()))))
    
    master_rows = []
    
    for i, date_str in enumerate(all_dates):
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Get matching records
        sf = stayfree_data.get(date_str, {})
        hl = health_data.get(date_str, {})
        
        # Check shifting variables (previous night screen time, next day steps)
        prev_date_str = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
        next_date_str = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
        
        prev_sf = stayfree_data.get(prev_date_str, {})
        next_hl = health_data.get(next_date_str, {})
        
        # Extract direct metrics
        steps = hl.get("steps_total", "")
        sleep_min = hl.get("sleep_minutes", "")
        sleep_start = hl.get("sleep_start_ist", "N/A")
        sleep_end = hl.get("sleep_end_ist", "N/A")
        sleep_session = hl.get("sleep_session_count", "")
        deep_sleep = hl.get("deep_sleep_minutes_if_available", "")
        rem_sleep = hl.get("rem_sleep_minutes_if_available", "")
        workout_min = hl.get("workout_minutes", "")
        workout_cnt = hl.get("workout_count", "")
        
        screen_min = sf.get("total_screen_minutes", "")
        android_min = sf.get("android_minutes", "")
        web_min = sf.get("web_minutes", "")
        late_night_min = sf.get("late_night_minutes", "")
        youtube_min = sf.get("youtube_minutes", "")
        youtube_shorts = sf.get("youtube_shorts_minutes_if_detected", "")
        instagram_min = sf.get("instagram_minutes", "")
        instagram_reels = sf.get("instagram_reels_minutes_if_detected", "")
        social_min = sf.get("social_minutes", "")
        gaming_min = sf.get("gaming_minutes", "")
        productivity_min = sf.get("productivity_minutes", "")
        learning_min = sf.get("learning_minutes", "")
        coding_min = sf.get("coding_minutes", "")
        session_cnt = sf.get("session_count", "")
        top_app = sf.get("top_app_or_domain", "None")
        top_cat = sf.get("top_category", "None")
        
        # Derived calculations
        # Set values to floats for safe math, default to 0.0 if empty
        f_min = (float(productivity_min) if productivity_min else 0.0) + \
                (float(learning_min) if learning_min else 0.0) + \
                (float(coding_min) if coding_min else 0.0)
                
        l_min = (float(youtube_min) if youtube_min else 0.0) + \
                (float(instagram_min) if instagram_min else 0.0) + \
                (float(social_min) if social_min else 0.0) + \
                (float(gaming_min) if gaming_min else 0.0) + \
                (float(sf.get("entertainment_minutes", 0.0)) if sf else 0.0)
                
        focus_ratio = f_min / max(l_min, 1.0)
        
        sleep_val = float(sleep_min) if sleep_min else 0.0
        late_val = float(late_night_min) if late_night_min else 0.0
        sleep_disruption = late_val / max(sleep_val, 1.0)
        
        prev_night_late = float(prev_sf.get("late_night_minutes", 0.0)) if prev_sf else 0.0
        
        next_day_steps_val = next_hl.get("steps_total", "")
        
        # Data Quality Flags
        dq_flags = []
        if not sf:
            dq_flags.append("MISSING_STAYFREE_DATA")
        if not hl:
            dq_flags.append("MISSING_HEALTH_CONNECT_DATA")
            
        master_rows.append({
            "date_ist": date_str,
            "steps_total": steps,
            "sleep_minutes": sleep_min,
            "sleep_start_ist": sleep_start,
            "sleep_end_ist": sleep_end,
            "sleep_session_count": sleep_session,
            "deep_sleep_minutes_if_available": deep_sleep,
            "rem_sleep_minutes_if_available": rem_sleep,
            "workout_minutes": workout_min,
            "workout_count": workout_cnt,
            "total_screen_minutes": screen_min,
            "android_minutes": android_min,
            "web_minutes": web_min,
            "late_night_minutes": late_night_min,
            "youtube_minutes": youtube_min,
            "youtube_shorts_minutes_if_detected": youtube_shorts,
            "instagram_minutes": instagram_min,
            "instagram_reels_minutes_if_detected": instagram_reels,
            "social_minutes": social_min,
            "gaming_minutes": gaming_min,
            "productivity_minutes": productivity_min,
            "learning_minutes": learning_min,
            "coding_minutes": coding_min,
            "session_count": session_cnt,
            "top_app_or_domain": top_app,
            "top_category": top_cat,
            "focus_minutes": round(f_min, 2),
            "leisure_minutes": round(l_min, 2),
            "focus_ratio": round(focus_ratio, 3),
            "sleep_disruption_index": round(sleep_disruption, 3),
            "previous_night_late_screen_minutes": round(prev_night_late, 2),
            "next_day_steps": next_day_steps_val,
            "data_quality_flags": ";".join(dq_flags) if dq_flags else "None"
        })

    # Write CSV & JSONL
    headers = list(master_rows[0].keys())
    with open(out_master_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(master_rows)
        
    with open(out_master_jsonl, "w", encoding="utf-8") as f:
        for mr in master_rows:
            f.write(json.dumps(mr, ensure_ascii=False) + "\n")

    # validation report
    validation = {
        "status": "SUCCESS",
        "master_rows": len(master_rows),
        "joined_overlap": sum(1 for m in master_rows if "MISSING" not in m["data_quality_flags"]),
        "missing_stayfree": sum(1 for m in master_rows if "MISSING_STAYFREE_DATA" in m["data_quality_flags"]),
        "missing_health": sum(1 for m in master_rows if "MISSING_HEALTH_CONNECT_DATA" in m["data_quality_flags"])
    }
    
    with open(report_json_path, "w", encoding="utf-8") as rj:
        json.dump(validation, rj, indent=2)
        
    # Write MD Report
    report_md = f"""# Coral Behavior-Health Master Validation Report

This report summarizes the outer join and feature mapping executed between **StayFree daily stats** and **Health Connect metrics**.

## 🕸️ Master Join Statistics
* **Total Master Days**: **{len(master_rows)}**
* **Fully Linked Days (Complete Coverage)**: **{validation["joined_overlap"]}** days
* **Incomplete StayFree Days**: **{validation["missing_stayfree"]}**
* **Incomplete Health Connect Days**: **{validation["missing_health"]}**

## 🛡️ Non-Causative Correlation & Integrity Rules
* **No Medical Causation Claimed**: All analyses use correlative, descriptive, and matched language.
* **Derived Index Mapping**: Mapped `focus_ratio` (Focus/Leisure), `sleep_disruption_index` (Late-night/Sleep duration), and shifted next-day steps and previous-night screen time.
"""
    with open(report_md_path, "w", encoding="utf-8") as rm:
        rm.write(report_md)
        
    print(f"Successfully compiled master behavior_health_daily table with {len(master_rows)} rows!")

if __name__ == '__main__':
    build_master_table()
