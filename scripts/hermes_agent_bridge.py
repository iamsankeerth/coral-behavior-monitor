import os
import csv
import json
import subprocess
from datetime import datetime

# Path Configurations
workspace = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project"
master_csv = os.path.join(workspace, "data", "coral", "csv", "behavior_health_daily.csv")
pipeline_script = os.path.join(workspace, "scripts", "run_daily_coral_pipeline.ps1")
state_file = os.path.join(workspace, "data", "logs", "hermes_session_state.json")
config_file = os.path.join(workspace, "config", "hermes_config.json")

# Ensure directories exist
os.makedirs(os.path.dirname(state_file), exist_ok=True)

# Default Thresholds (Minutes)
REELS_SHORTS_LIMIT = 30.0
TOTAL_SCREEN_LIMIT = 240.0

# Dynamic Escalation Messages
ESCALATION_MESSAGES = {
    1: {
        "style": "Gentle Awareness",
        "message": "Hey! Friendly check-in. You've crossed your Reels/Shorts limit today. Let's stand up, stretch, and bring focus back to what you're building."
    },
    2: {
        "style": "Mindful Reframing",
        "message": "You're still scrolling. Reels/Shorts are now at {minutes} minutes. Remember: algorithms are engineered to capture your time. You are the creator, not the consumer. What are we building today?"
    },
    3: {
        "style": "Deep Focus Alignment",
        "message": "Reels/Shorts have hit {minutes} minutes. Every minute scrolling is a minute taken directly from your personal coding goals. You have outstanding potential. Let's close the tab and do 15 minutes of deep focus."
    },
    4: {
        "style": "Philosophical Depth",
        "message": "Attention: You have spent {minutes} minutes scrolling today. Time is your only non-renewable resource. Dopamine loops feel good momentarily, but creating something real feels lasting. Let's honor your time."
    },
    5: {
        "style": "The Ultimate Guardian",
        "message": "Reels/Shorts have exceeded {minutes} minutes. This is your guardian alert. The infinite scroll will never run out of videos, but your day will. Close Edge, put down your phone, and take a 10-minute walk. Your future self is waiting for you to build."
    }
}

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Default native Hermes config
    default_config = {
        "whatsapp_target": "whatsapp:iamsan",  # Matches your registered TUI target
        "reels_shorts_limit": REELS_SHORTS_LIMIT,
        "total_screen_limit": TOTAL_SCREEN_LIMIT
    }
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=4)
    return default_config

def run_pipeline():
    print("[1/4] Running daily Coral pipeline to extract freshest Edge & Android logs...")
    try:
        res = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", pipeline_script],
            capture_output=True,
            text=True,
            check=True
        )
        return True, res.stdout
    except Exception as e:
        return False, str(e)

def send_via_hermes(target, text):
    if not target:
        return False, "Delivery target is empty."
        
    try:
        # Run the native hermes send command
        res = subprocess.run(
            ["hermes", "send", "--to", target, text],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return True, "Message delivered successfully via Hermes CLI!"
    except subprocess.CalledProcessError as e:
        return False, f"Hermes CLI error (Exit Code {e.returncode}): {e.stderr.strip() or e.stdout.strip()}"
    except Exception as e:
        return False, f"Failed to invoke Hermes executable: {e}"

def main():
    config = load_config()
    limit = config.get("reels_shorts_limit", REELS_SHORTS_LIMIT)
    target = config.get("whatsapp_target", "whatsapp:iamsan")
    
    # 1. Update data
    success, log_out = run_pipeline()
    if not success:
        print(json.dumps({"error": f"Failed to run pipeline: {log_out}"}))
        return

    # 2. Read latest today IST row from master CSV
    if not os.path.exists(master_csv):
        print(json.dumps({"error": "Master joined CSV behavior_health_daily.csv is missing."}))
        return
        
    with open(master_csv, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        if not reader:
            print(json.dumps({"error": "Master CSV is empty."}))
            return
        today_row = reader[-1] # The latest daily record

    # Extract fields
    date_ist = today_row.get("date_ist", "")
    reels_min = today_row.get("instagram_reels_minutes_if_detected", "0.0")
    shorts_min = today_row.get("youtube_shorts_minutes_if_detected", "0.0")
    
    reels_min = float(reels_min) if reels_min else 0.0
    shorts_min = float(shorts_min) if shorts_min else 0.0
    
    total_reels_shorts = round(reels_min + shorts_min, 2)
    total_screen = round(float(today_row.get("total_screen_minutes", "0.0")), 2)
    
    # 3. Stateful Escalation Checking
    session_state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as sf:
                session_state = json.load(sf)
        except:
            pass

    # Verify if date is the same to persist escalation levels
    last_date = session_state.get("date_ist", "")
    last_reels_shorts = session_state.get("reels_shorts_minutes", 0.0)
    escalation_level = session_state.get("escalation_level", 1)

    limit_exceeded = total_reels_shorts > limit
    whatsapp_sent = False
    whatsapp_status = "Not Exceeded"
    selected_msg = ""
    style = "Normal"

    if limit_exceeded:
        # Check if the user is STILL actively watching (duration has increased since last check)
        if date_ist == last_date:
            if total_reels_shorts > last_reels_shorts:
                # Increment escalation level up to max 5
                escalation_level = min(5, escalation_level + 1)
            # If duration didn't increase, keep current escalation level
        else:
            # New day reset
            escalation_level = 1
            
        # Select Escalation Message
        msg_template = ESCALATION_MESSAGES[escalation_level]
        selected_msg = msg_template["message"].format(minutes=total_reels_shorts)
        style = msg_template["style"]
        
        # Send Push Notification via Hermes CLI Native Gateway
        w_success, w_status = send_via_hermes(target, selected_msg)
        whatsapp_sent = w_success
        whatsapp_status = w_status
        
        # Save fresh state
        session_state = {
            "date_ist": date_ist,
            "reels_shorts_minutes": total_reels_shorts,
            "escalation_level": escalation_level
        }
        with open(state_file, 'w', encoding='utf-8') as sf:
            json.dump(session_state, sf, indent=4)
    else:
        # Reset if below limit
        session_state = {
            "date_ist": date_ist,
            "reels_shorts_minutes": total_reels_shorts,
            "escalation_level": 1
        }
        with open(state_file, 'w', encoding='utf-8') as sf:
            json.dump(session_state, sf, indent=4)

    # 4. Structured JSON output for local Hermes agent execution
    output_payload = {
        "date_ist": date_ist,
        "current_total_screen_minutes": total_screen,
        "current_reels_shorts_minutes": total_reels_shorts,
        "limit_threshold_minutes": limit,
        "limit_exceeded": limit_exceeded,
        "escalation_level": escalation_level,
        "escalation_style": style,
        "pushed_whatsapp_message": selected_msg if limit_exceeded else "N/A",
        "whatsapp_status": whatsapp_status,
        "whatsapp_pushed": whatsapp_sent,
        "suggested_hermes_prompt": f"Write a highly motivational, philosophical message for a developer who is struggling with doomscrolling. Today they spent {total_reels_shorts} minutes on Reels/Shorts (Limit: {limit} mins). Depth level: {escalation_level}/5. Keep it impactful, reframing, and supportive."
    }
    
    print("\n" + "="*80)
    print("[HERMES AGENT INTERFACE PAYLOAD (STDOUT)]")
    print("="*80)
    print(json.dumps(output_payload, indent=4))
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
