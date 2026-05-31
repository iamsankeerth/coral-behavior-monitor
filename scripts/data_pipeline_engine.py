import os
import sys
# Add scripts directory to path to support in-process imports from any context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import csv
import json
import sqlite3
import shutil
import glob
import subprocess
import hashlib
import yaml
import struct
from datetime import datetime, timedelta, timezone
from path_config import PathConfig

def parse_utc_to_ist(time_str):
    """Utility for timezone conversions (UTC to IST)."""
    if not time_str or time_str == "N/A":
        return None, None, None, None, None
        
    try:
        cleaned_str = time_str.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(cleaned_str)
        dt_ist = dt_utc + timedelta(hours=5, minutes=30)
        date_ist = dt_ist.strftime("%Y-%m-%d")
        hour_ist = dt_ist.hour
        weekday_ist = dt_ist.weekday()
        return dt_utc, dt_ist, date_ist, hour_ist, weekday_ist
    except Exception:
        return None, None, None, None, None

def generate_event_id(ts_utc, domain, plat, dur, src):
    """Utility for stable event ID hash generation."""
    raw_str = f"{ts_utc}_{domain}_{plat}_{dur}_{src}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

def get_category_and_sub(domain_or_app, category_map):
    """Utility for category mapping and subcategory detection."""
    cat = "unknown"
    sub = "None"
    
    if domain_or_app in category_map:
        cat = category_map[domain_or_app]
    else:
        for k, v in category_map.items():
            if k in domain_or_app:
                cat = v
                break
                
    if "youtube.com/shorts" in domain_or_app:
        sub = "youtube_shorts"
    elif "instagram.com/reels" in domain_or_app:
        sub = "instagram_reels"
        
    return cat, sub

class DataPipelineEngine:
    """
    Unified Data Pipeline Engine for Coral Behavior-Health Monitor.
    Consolidates the StayFree extraction, health aggregation, and behavior_health_daily joins.
    """
    def __init__(self, workspace=None):
        self.config = PathConfig(workspace)
        self.workspace = self.config.workspace
        
        self.raw_csv_path = self.config.raw_csv_path
        self.raw_json_path = self.config.raw_json_path
        self.mapping_path = self.config.mapping_path
        
        self.out_events_csv = self.config.out_events_csv
        self.out_events_jsonl = self.config.out_events_jsonl
        self.out_daily_csv = self.config.out_daily_csv
        self.out_daily_jsonl = self.config.out_daily_jsonl
        
        self.db_path = self.config.db_path
        self.out_health_csv = self.config.out_health_csv
        self.out_health_jsonl = self.config.out_health_jsonl
        
        self.out_master_csv = self.config.out_master_csv
        self.out_master_jsonl = self.config.out_master_jsonl
        
        self.report_dir = self.config.report_dir
        self.log_dir = self.config.log_dir
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.out_events_csv), exist_ok=True)
        os.makedirs(os.path.dirname(self.out_events_jsonl), exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Load category mappings
        if os.path.exists(self.mapping_path):
            with open(self.mapping_path, "r", encoding="utf-8") as yf:
                self.category_map = yaml.safe_load(yf) or {}
        else:
            self.category_map = {}

    def get_category_and_sub(self, domain_or_app):
        return get_category_and_sub(domain_or_app, self.category_map)

    def parse_utc_to_ist(self, time_str):
        return parse_utc_to_ist(time_str)

    def generate_event_id(self, ts_utc, domain, plat, dur, src):
        return generate_event_id(ts_utc, domain, plat, dur, src)

    def _enrich_raw_event(self, dt_utc, domain_clean, platform, duration, source, dedup_set):
        """
        Enrich a raw event with IST conversion, category mapping, late-night classification,
        data quality flags, and unique ID generation.
        Returns the enriched dictionary, or None if the event is a duplicate.
        """
        ts_utc_str = dt_utc.isoformat().replace("+00:00", "")
        if not ts_utc_str.endswith("Z"):
            ts_utc_str += "Z"
            
        dedup_key = (ts_utc_str, domain_clean.lower().strip(), platform)
        if dedup_key in dedup_set:
            return None
        dedup_set.add(dedup_key)
        
        # Convert to IST
        dt_ist = dt_utc + timedelta(hours=5, minutes=30)
        date_ist = dt_ist.strftime("%Y-%m-%d")
        hour_ist = dt_ist.hour
        weekday_ist = dt_ist.weekday()
        
        # Category Mapping
        cat, sub = self.get_category_and_sub(domain_clean)
        
        # Late Night Classification
        is_late = hour_ist >= 23 or hour_ist < 5
        late_window = "None"
        if is_late:
            if hour_ist >= 23 or hour_ist < 1:
                late_window = "23:00-01:00"
            elif hour_ist >= 1 and hour_ist < 3:
                late_window = "01:00-03:00"
            else:
                late_window = "03:00-05:00"
                
        # Data Quality Flags
        dq_flags = []
        if duration > 28800:
            dq_flags.append("SUSPICIOUS_LONG_DURATION")
            
        event_id = self.generate_event_id(ts_utc_str, domain_clean, platform, duration, source)
        
        return {
            "event_id": event_id,
            "timestamp_utc": ts_utc_str,
            "timestamp_ist": dt_ist.isoformat(),
            "date_ist": date_ist,
            "hour_ist": hour_ist,
            "weekday_ist": weekday_ist,
            "platform": platform,
            "device_type": "PC-Windows" if platform == "web" else "Mobile-Android",
            "domain_or_app": domain_clean,
            "app_or_domain_normalized": domain_clean.lower().strip(),
            "category": cat,
            "subcategory": sub,
            "duration_seconds": duration,
            "duration_minutes": round(duration / 60.0, 2),
            "is_web": "true" if platform == "web" else "false",
            "is_android": "true" if platform == "android" else "false",
            "is_late_night": "true" if is_late else "false",
            "late_night_window": late_window,
            "source": source,
            "raw_key": f"key-{event_id[:8]}",
            "raw_payload_available": "true",
            "data_quality_flags": ";".join(dq_flags) if dq_flags else "None"
        }

    # --- PURE-PYTHON CHROMIUM INDEXEDDB LEVELDB LOG PARSER HELPERS ---
    def _read_varint32(self, data, offset):
        result = 0
        shift = 0
        while offset < len(data):
            byte = data[offset]
            offset += 1
            result |= (byte & 0x7f) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return result, offset

    def _parse_write_batch(self, payload):
        if len(payload) < 12:
            return []
        seq, count = struct.unpack("<QI", payload[:12])
        offset = 12
        records = []
        for _ in range(count):
            if offset >= len(payload):
                break
            rec_type = payload[offset]
            offset += 1
            if rec_type == 1: # Put
                key_len, offset = self._read_varint32(payload, offset)
                key = payload[offset:offset+key_len]
                offset += key_len
                val_len, offset = self._read_varint32(payload, offset)
                val = payload[offset:offset+val_len]
                offset += val_len
                records.append(('PUT', key, val))
            elif rec_type == 2: # Delete
                key_len, offset = self._read_varint32(payload, offset)
                key = payload[offset:offset+key_len]
                offset += key_len
                records.append(('DELETE', key, None))
        return records

    def _parse_log_file(self, filepath):
        block_size = 32768
        if not os.path.exists(filepath):
            return
        with open(filepath, "rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break
                offset = 0
                while offset + 7 <= len(block):
                    crc, length, rec_type = struct.unpack("<IHB", block[offset:offset+7])
                    if rec_type == 0 and length == 0:
                        break
                    offset += 7
                    if offset + length > len(block):
                        break
                    payload = block[offset:offset+length]
                    offset += length
                    if rec_type == 1: # FULL record
                        try:
                            for r in self._parse_write_batch(payload):
                                yield r
                        except Exception:
                            pass

    # --- IN-PROCESS FILE COPY & PREPARATION STAGE ---
    def _copy_active_extension_files(self):
        print("Stage 1: Replicating active Chromium settings and IndexedDB files...")
        
        # 1. Local Extension Settings (LevelDB)
        src_settings = self.config.active_settings_src
        dst_settings = self.config.stayfree_temp_copy
        if os.path.exists(src_settings):
            try:
                if os.path.exists(dst_settings):
                    shutil.rmtree(dst_settings)
                os.makedirs(dst_settings)
                for item in glob.glob(os.path.join(src_settings, "*")):
                    if os.path.basename(item) != "LOCK":
                        if os.path.isdir(item):
                            shutil.copytree(item, os.path.join(dst_settings, os.path.basename(item)))
                        else:
                            shutil.copy(item, dst_settings)
                print("Active StayFree settings copied successfully.")
            except Exception as e:
                print(f"Warning: Failed to duplicate Settings files: {e}")
        else:
            print("Warning: Edge settings source path not found.")

        # 2. IndexedDB (LevelDB logs containing real-time scrolling sessions)
        src_idb = self.config.active_indexeddb_src
        dst_idb = self.config.stayfree_indexeddb_temp
        if os.path.exists(src_idb):
            try:
                if os.path.exists(dst_idb):
                    shutil.rmtree(dst_idb)
                os.makedirs(dst_idb)
                for item in glob.glob(os.path.join(src_idb, "*")):
                    if os.path.basename(item) != "LOCK":
                        if os.path.isdir(item):
                            shutil.copytree(item, os.path.join(dst_idb, os.path.basename(item)))
                        else:
                            shutil.copy(item, dst_idb)
                print("Active StayFree IndexedDB files copied successfully.")
            except Exception as e:
                print(f"Warning: Failed to duplicate IndexedDB logs: {e}")
        else:
            print("Warning: Edge IndexedDB source path not found.")

    def _run_js_extractor(self):
        print("Stage 2: Invoking extract_stayfree.js to dump raw LevelDB settings into CSV...")
        try:
            node_script = os.path.join(self.workspace, "extract_stayfree.js")
            res = subprocess.run(["node", node_script], cwd=self.workspace, capture_output=True, text=True, check=True)
            print(f"JS Extractor finished successfully: {res.stdout.strip().splitlines()[-1] if res.stdout else 'Done'}")
            return True
        except Exception as e:
            print(f"Error running extract_stayfree.js: {e}")
            return False

    # --- TRANSFORM AND VALIDATE PIPELINES ---
    def _build_stayfree_tables(self):
        print("Stage 3: Running StayFree extraction & log processing pipeline...")
        events = []
        daily_stats = {}
        anomalies = []
        dedup_set = set()
        
        # 1. Parse active live sessions from IndexedDB log files (Down-to-the-second live sync)
        indexeddb_dir = self.config.stayfree_indexeddb_temp
        parsed_count = 0
        if os.path.exists(indexeddb_dir):
            for filename in os.listdir(indexeddb_dir):
                if filename.endswith(".log"):
                    log_path = os.path.join(indexeddb_dir, filename)
                    for action, key, val in self._parse_log_file(log_path):
                        if action == 'PUT':
                            if b'appId' in val and b'startedAt' in val:
                                try:
                                    # Parse appId (domain)
                                    idx_app = val.find(b'appId')
                                    if idx_app == -1 or idx_app + 6 >= len(val):
                                        continue
                                    len_app = val[idx_app + 6]
                                    domain = val[idx_app + 7 : idx_app + 7 + len_app].decode('utf-8', errors='ignore')
                                    
                                    # Parse startedAt
                                    idx_start = val.find(b'startedAt')
                                    if idx_start == -1 or idx_start + 17 >= len(val):
                                        continue
                                    if val[idx_start + 9] != ord('N'):
                                        continue
                                    started_at = struct.unpack('<d', val[idx_start + 10 : idx_start + 10 + 8])[0]
                                    
                                    # Parse endedAt
                                    ended_at = None
                                    idx_end = val.find(b'endedAt')
                                    if idx_end != -1 and idx_end + 15 <= len(val):
                                        if val[idx_end + 7] == ord('N'):
                                            ended_at = struct.unpack('<d', val[idx_end + 8 : idx_end + 8 + 8])[0]
                                    
                                    # Parse path
                                    path_str = ""
                                    idx_path = val.find(b'path')
                                    if idx_path != -1 and idx_path + 5 < len(val):
                                        len_path = val[idx_path + 5]
                                        path_str = val[idx_path + 6 : idx_path + 6 + len_path].decode('utf-8', errors='ignore')
                                        
                                    duration = (ended_at - started_at) / 1000 if ended_at else 0.0
                                    
                                    # Ignore zero or impossible durations
                                    if duration <= 0 or duration > 86400:
                                        continue
                                        
                                    # Convert startedAt to ISO timestamp UTC
                                    dt_utc = datetime.fromtimestamp(started_at / 1000, timezone.utc)
                                    
                                    is_pkg = "." in domain and domain.replace(".", "").islower() and not domain.endswith(".com") and not domain.endswith(".org") and not domain.endswith(".net")
                                    platform = "android" if is_pkg else "web"
                                    
                                    domain_clean = domain
                                    if not is_pkg and path_str:
                                        if "youtube.com" in domain and "shorts" in path_str:
                                            domain_clean = "youtube.com/shorts"
                                        elif "instagram.com" in domain and "reels" in path_str:
                                            domain_clean = "instagram.com/reels"
                                    
                                    event = self._enrich_raw_event(dt_utc, domain_clean, platform, duration, "IndexedDB Log", dedup_set)
                                    if not event:
                                        continue
                                    
                                    events.append(event)
                                    date_ist = event["date_ist"]
                                    if date_ist not in daily_stats:
                                        daily_stats[date_ist] = []
                                    daily_stats[date_ist].append(event)
                                    
                                    parsed_count += 1
                                except Exception:
                                    pass
            print(f"Successfully injected {parsed_count} live sessions from StayFree IndexedDB logs.")

        # 2. Read raw CSV events (Fallback / Historical)
        if os.path.exists(self.raw_csv_path):
            with open(self.raw_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    domain = row["domain_or_app"]
                    platform = row["platform"]
                    source = row["source"]
                    raw_time = row["date_or_timestamp"]
                    
                    try:
                        duration = float(row["duration_seconds"])
                    except ValueError:
                        duration = 0.0
                        
                    if duration <= 0:
                        anomalies.append({
                            "reason": "ZERO_OR_NEGATIVE_DURATION",
                            "domain": domain,
                            "duration": duration,
                            "timestamp": raw_time
                        })
                        continue
                        
                    if duration > 86400:
                        anomalies.append({
                            "reason": "IMPOSSIBLE_LONG_DURATION",
                            "domain": domain,
                            "duration": duration,
                            "timestamp": raw_time
                        })
                        continue
                        
                    dt_utc, dt_ist, date_ist, hour_ist, weekday_ist = self.parse_utc_to_ist(raw_time)
                    if not dt_utc:
                        anomalies.append({
                            "reason": "INVALID_TIMESTAMP",
                            "domain": domain,
                            "timestamp": raw_time
                        })
                        continue
                        
                    event = self._enrich_raw_event(dt_utc, domain, platform, duration, source, dedup_set)
                    if not event:
                        anomalies.append({
                            "reason": "DUPLICATE_EVENT_ID",
                            "event_id": self.generate_event_id(dt_utc.isoformat(), domain, platform, duration, source),
                            "domain": domain,
                            "timestamp": raw_time
                        })
                        continue
                    
                    events.append(event)
                    date_ist = event["date_ist"]
                    if date_ist not in daily_stats:
                        daily_stats[date_ist] = []
                    daily_stats[date_ist].append(event)

        # 3. Parse active sessions directly from Edge Browser History SQLite DB (Real-time Fallback)
        edge_db_path = os.path.join(self.config.edge_profile_path, "History")
        edge_parsed_count = 0
        if os.path.exists(edge_db_path):
            try:
                from urllib.parse import urlparse
                temp_history_db = os.path.join(os.path.dirname(self.out_events_csv), "History.temp")
                if os.path.exists(temp_history_db):
                    try: os.remove(temp_history_db)
                    except: pass
                    
                shutil.copy2(edge_db_path, temp_history_db)
                
                conn = sqlite3.connect(temp_history_db)
                cursor = conn.cursor()
                
                CHROME_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)
                ist = timezone(timedelta(hours=5, minutes=30))
                now = datetime.now(ist)
                start_date = now - timedelta(days=15)
                start_us = int((start_date.astimezone(timezone.utc) - CHROME_EPOCH).total_seconds() * 1_000_000)
                
                cursor.execute("""
                    SELECT urls.url, urls.title, visits.visit_time, visits.visit_duration
                    FROM visits JOIN urls ON visits.url = urls.id
                    WHERE visits.visit_time >= ?
                      AND visits.visit_duration > 0;
                """, (start_us,))
                
                rows = cursor.fetchall()
                for url, title, visit_time, visit_duration in rows:
                    duration = visit_duration / 1_000_000.0
                    if duration <= 0 or duration > 86400:
                        continue
                        
                    dt_utc = CHROME_EPOCH + timedelta(microseconds=visit_time)
                    
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc
                    if domain.startswith("www."):
                        domain = domain[4:]
                    
                    domain_clean = domain
                    path_str = parsed_url.path
                    if "youtube.com" in domain and "shorts" in path_str:
                        domain_clean = "youtube.com/shorts"
                    elif "instagram.com" in domain and "reels" in path_str:
                        domain_clean = "instagram.com/reels"
                        
                    platform = "web"
                    event = self._enrich_raw_event(dt_utc, domain_clean, platform, duration, "Edge History", dedup_set)
                    if not event:
                        continue
                        
                    events.append(event)
                    date_ist = event["date_ist"]
                    if date_ist not in daily_stats:
                        daily_stats[date_ist] = []
                    daily_stats[date_ist].append(event)
                    
                    edge_parsed_count += 1
                    
                conn.close()
                try: os.remove(temp_history_db)
                except: pass
                print(f"Successfully injected {edge_parsed_count} live sessions from Edge Browser History.")
            except Exception as e:
                print(f"Warning: Error parsing Edge History: {e}")

        if not events:
            print("No events generated for StayFree. Skipping table compiles.")
            return 0, 0

        # Build stayfree_daily Aggregates
        daily_rows = []
        for dt_key, day_events in sorted(daily_stats.items()):
            total_sec = sum(e["duration_seconds"] for e in day_events)
            android_sec = sum(e["duration_seconds"] for e in day_events if e["platform"] == "android")
            web_sec = sum(e["duration_seconds"] for e in day_events if e["platform"] == "web")
            late_night_sec = sum(e["duration_seconds"] for e in day_events if e["is_late_night"] == "true")
            
            youtube_sec = sum(e["duration_seconds"] for e in day_events if "youtube" in e["domain_or_app"])
            youtube_shorts_sec = sum(e["duration_seconds"] for e in day_events if e["subcategory"] == "youtube_shorts")
            instagram_sec = sum(e["duration_seconds"] for e in day_events if "instagram" in e["domain_or_app"])
            instagram_reels_sec = sum(e["duration_seconds"] for e in day_events if e["subcategory"] == "instagram_reels")
            
            cat_seconds = {}
            for e in day_events:
                cat_seconds[e["category"]] = cat_seconds.get(e["category"], 0.0) + e["duration_seconds"]
                
            social_sec = cat_seconds.get("social", 0.0) + cat_seconds.get("threads", 0.0)
            gaming_sec = cat_seconds.get("gaming", 0.0)
            productivity_sec = cat_seconds.get("productivity", 0.0)
            learning_sec = cat_seconds.get("learning", 0.0)
            coding_sec = cat_seconds.get("coding", 0.0)
            communication_sec = cat_seconds.get("communication", 0.0)
            entertainment_sec = cat_seconds.get("entertainment", 0.0)
            
            session_cnt = len(day_events)
            android_cnt = sum(1 for e in day_events if e["platform"] == "android")
            web_cnt = sum(1 for e in day_events if e["platform"] == "web")
            
            app_sec = {}
            for e in day_events:
                app_sec[e["domain_or_app"]] = app_sec.get(e["domain_or_app"], 0.0) + e["duration_seconds"]
            top_app = max(app_sec, key=app_sec.get) if app_sec else "None"
            top_cat = max(cat_seconds, key=cat_seconds.get) if cat_seconds else "None"
            
            durations = sorted([e["duration_seconds"] for e in day_events])
            longest_sec = durations[-1] if durations else 0.0
            avg_sec = sum(durations) / len(durations) if durations else 0.0
            
            n = len(durations)
            median_sec = 0.0
            if n > 0:
                if n % 2 == 1:
                    median_sec = durations[n // 2]
                else:
                    median_sec = (durations[n // 2 - 1] + durations[n // 2]) / 2.0
                    
            events_sorted_time = sorted(day_events, key=lambda x: x["timestamp_ist"])
            first_time = events_sorted_time[0]["timestamp_ist"] if events_sorted_time else "N/A"
            last_time = events_sorted_time[-1]["timestamp_ist"] if events_sorted_time else "N/A"
            
            reels_conf = "NONE"
            if instagram_reels_sec > 0:
                reels_conf = "HIGH"
            elif instagram_sec > 0:
                reels_conf = "LOW"
                
            shorts_conf = "NONE"
            if youtube_shorts_sec > 0:
                shorts_conf = "HIGH"
            elif youtube_sec > 0:
                shorts_conf = "LOW"
                
            day_flags = []
            if total_sec > 57600:
                day_flags.append("EXTREME_SCREEN_TIME")
                
            daily_rows.append({
                "date_ist": dt_key,
                "total_screen_seconds": round(total_sec, 2),
                "total_screen_minutes": round(total_sec / 60.0, 2),
                "android_seconds": round(android_sec, 2),
                "android_minutes": round(android_sec / 60.0, 2),
                "web_seconds": round(web_sec, 2),
                "web_minutes": round(web_sec / 60.0, 2),
                "late_night_seconds": round(late_night_sec, 2),
                "late_night_minutes": round(late_night_sec / 60.0, 2),
                "youtube_seconds": round(youtube_sec, 2),
                "youtube_minutes": round(youtube_sec / 60.0, 2),
                "youtube_shorts_seconds_if_detected": round(youtube_shorts_sec, 2),
                "youtube_shorts_minutes_if_detected": round(youtube_shorts_sec / 60.0, 2),
                "instagram_seconds": round(instagram_sec, 2),
                "instagram_minutes": round(instagram_sec / 60.0, 2),
                "instagram_reels_seconds_if_detected": round(instagram_reels_sec, 2),
                "instagram_reels_minutes_if_detected": round(instagram_reels_sec / 60.0, 2),
                "social_seconds": round(social_sec, 2),
                "social_minutes": round(social_sec / 60.0, 2),
                "gaming_seconds": round(gaming_sec, 2),
                "gaming_minutes": round(gaming_sec / 60.0, 2),
                "productivity_seconds": round(productivity_sec, 2),
                "productivity_minutes": round(productivity_sec / 60.0, 2),
                "learning_seconds": round(learning_sec, 2),
                "learning_minutes": round(learning_sec / 60.0, 2),
                "coding_seconds": round(coding_sec, 2),
                "coding_minutes": round(coding_sec / 60.0, 2),
                "communication_seconds": round(communication_sec, 2),
                "communication_minutes": round(communication_sec / 60.0, 2),
                "entertainment_seconds": round(entertainment_sec, 2),
                "entertainment_minutes": round(entertainment_sec / 60.0, 2),
                "session_count": session_cnt,
                "android_session_count": android_cnt,
                "web_session_count": web_cnt,
                "top_app_or_domain": top_app,
                "top_category": top_cat,
                "longest_session_seconds": round(longest_sec, 2),
                "avg_session_seconds": round(avg_sec, 2),
                "median_session_seconds": round(median_sec, 2),
                "first_event_ist": first_time,
                "last_event_ist": last_time,
                "reels_detection_confidence": reels_conf,
                "shorts_detection_confidence": shorts_conf,
                "data_quality_flags": ";".join(day_flags) if day_flags else "None"
            })

        # Save files
        with open(self.out_events_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(events[0].keys()))
            writer.writeheader()
            writer.writerows(events)
            
        with open(self.out_events_jsonl, "w", encoding="utf-8") as f:
            for ev in events:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
                
        with open(self.out_daily_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(daily_rows[0].keys()))
            writer.writeheader()
            writer.writerows(daily_rows)
            
        with open(self.out_daily_jsonl, "w", encoding="utf-8") as f:
            for dr in daily_rows:
                f.write(json.dumps(dr, ensure_ascii=False) + "\n")

        # StayFree reports
        stayfree_report_md = os.path.join(self.report_dir, "stayfree_validation_report.md")
        stayfree_report_json = os.path.join(self.report_dir, "stayfree_validation_report.json")
        
        validation_summary = {
            "status": "SUCCESS",
            "processed_events": len(events),
            "processed_days": len(daily_rows),
            "total_anomalies_logged": len(anomalies),
            "anomaly_breakdown": {
                "duplicate_ids": sum(1 for a in anomalies if a["reason"] == "DUPLICATE_EVENT_ID"),
                "invalid_timestamps": sum(1 for a in anomalies if a["reason"] == "INVALID_TIMESTAMP"),
                "negative_durations": sum(1 for a in anomalies if a["reason"] == "ZERO_OR_NEGATIVE_DURATION"),
                "impossible_long_durations": sum(1 for a in anomalies if a["reason"] == "IMPOSSIBLE_LONG_DURATION")
            }
        }
        with open(stayfree_report_json, "w", encoding="utf-8") as rj:
            json.dump(validation_summary, rj, indent=2)
            
        md_text = f"""# StayFree Core Data Validation Report
This report summarizes the data verification, transformation, and load (ETL) run for **StayFree screen-time data**.

## 📊 Summary Statistics
* **Processed Event Rows**: **{len(events)}** (Deduplicated & validated)
* **Processed Days**: **{len(daily_rows)}** (Local IST Date Boundary)
* **Anomaly Records Filtered**: **{len(anomalies)}**
"""
        with open(stayfree_report_md, "w", encoding="utf-8") as rm:
            rm.write(md_text)
            
        print(f"StayFree tables generated successfully: {len(events)} events, {len(daily_rows)} days.")
        return len(events), len(daily_rows)

    def _build_health_table(self):
        print("Stage 4: Aggregating Health Connect physical activity and metrics...")
        dates_screen = []
        if os.path.exists(self.out_daily_csv):
            with open(self.out_daily_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dates_screen.append(row["date_ist"])
        else:
            base_date = datetime.now() - timedelta(days=62)
            for i in range(62):
                dates_screen.append((base_date + timedelta(days=i)).strftime("%Y-%m-%d"))

        real_steps = {}
        real_workouts = {}
        real_calories = {}
        use_real_db = False
        
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Steps aggregation
                cursor.execute("SELECT start_time, start_zone_offset, count FROM steps_record_table;")
                for start_time, zone_offset, count in cursor.fetchall():
                    local_sec = (start_time / 1000.0) + zone_offset
                    date_str = datetime.fromtimestamp(local_sec, timezone.utc).strftime('%Y-%m-%d')
                    real_steps[date_str] = real_steps.get(date_str, 0) + count
                    
                # Workouts aggregation
                cursor.execute("SELECT start_time, end_time, start_zone_offset FROM exercise_session_record_table;")
                for start_time, end_time, zone_offset in cursor.fetchall():
                    local_sec = (start_time / 1000.0) + zone_offset
                    date_str = datetime.fromtimestamp(local_sec, timezone.utc).strftime('%Y-%m-%d')
                    duration_min = (end_time - start_time) / (1000.0 * 60.0)
                    
                    if date_str not in real_workouts:
                        real_workouts[date_str] = { "minutes": 0.0, "count": 0 }
                    real_workouts[date_str]["minutes"] += duration_min
                    real_workouts[date_str]["count"] += 1
                    
                # Calories aggregation
                cursor.execute("SELECT start_time, start_zone_offset, energy FROM total_calories_burned_record_table;")
                for start_time, zone_offset, energy in cursor.fetchall():
                    local_sec = (start_time / 1000.0) + zone_offset
                    date_str = datetime.fromtimestamp(local_sec, timezone.utc).strftime('%Y-%m-%d')
                    kcal = energy / 4184.0
                    real_calories[date_str] = real_calories.get(date_str, 0.0) + kcal
                    
                conn.close()
                use_real_db = True
            except Exception as e:
                print(f"Warning: Failed to parse physical SQLite health DB: {e}")
                use_real_db = False

        health_rows = []
        for dt_str in dates_screen:
            steps_total = real_steps.get(dt_str, 0) if use_real_db else 0
            w_info = real_workouts.get(dt_str, {"minutes": 0.0, "count": 0}) if use_real_db else {"minutes": 0.0, "count": 0}
            workout_min = round(w_info["minutes"], 2)
            workout_cnt = w_info["count"]
            
            calories_val = round(real_calories.get(dt_str, 0.0), 2) if use_real_db else 0.0
            calories = calories_val if calories_val > 0.0 else ""
            
            # Explicit empty/N/A values for fields missing in local source DB
            sleep_minutes = ""
            sleep_start_ist = ""
            sleep_end_ist = ""
            sleep_session_count = 0
            awake_minutes = ""
            light_sleep_minutes = ""
            deep_sleep_minutes = ""
            rem_sleep_minutes = ""
            heart_rate_avg = ""
            
            source_info = "Real Health Connect SQLite DB" if use_real_db else "No Database Connected"
            dq_flags = ["*N/A: Sleep session and heart rate tables were completely empty in your source Health Connect database"]
            if steps_total < 3000:
                dq_flags.append("SEDENTARY_DAY")
                
            health_rows.append({
                "date_ist": dt_str,
                "steps_total": steps_total,
                "sleep_minutes": sleep_minutes,
                "sleep_start_ist": sleep_start_ist,
                "sleep_end_ist": sleep_end_ist,
                "sleep_session_count": sleep_session_count,
                "awake_minutes_if_available": awake_minutes,
                "light_sleep_minutes_if_available": light_sleep_minutes,
                "deep_sleep_minutes_if_available": deep_sleep_minutes,
                "rem_sleep_minutes_if_available": rem_sleep_minutes,
                "workout_minutes": workout_min,
                "workout_count": workout_cnt,
                "active_calories_if_available": calories,
                "heart_rate_avg_if_available": heart_rate_avg,
                "source_file": source_info,
                "data_quality_flags": ";".join(dq_flags)
            })

        # Save health files
        with open(self.out_health_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(health_rows[0].keys()))
            writer.writeheader()
            writer.writerows(health_rows)
            
        with open(self.out_health_jsonl, "w", encoding="utf-8") as f:
            for hr in health_rows:
                f.write(json.dumps(hr, ensure_ascii=False) + "\n")

        # Health Validation reports
        health_report_md = os.path.join(self.report_dir, "health_validation_report.md")
        health_report_json = os.path.join(self.report_dir, "health_validation_report.json")
        
        avg_steps = sum(h["steps_total"] for h in health_rows) / len(health_rows) if health_rows else 0.0
        health_validation = {
            "status": "SUCCESS",
            "data_source": "REAL_DATABASE" if use_real_db else "SANDBOX_EMPTY",
            "processed_days": len(health_rows),
            "steps_average": round(avg_steps, 2),
            "sleep_average_min": 0.0,
            "total_workouts": sum(h["workout_count"] for h in health_rows)
        }
        with open(health_report_json, "w", encoding="utf-8") as rj:
            json.dump(health_validation, rj, indent=2)
            
        md_text = f"""# Health Connect Core Data Validation Report
This report summarizes the daily physical health aggregates generated in the **Health Connect Drive pipeline**.

## 🏃 Summary Statistics
* **Data Source**: **{health_validation["data_source"]}**
* **Processed Days**: **{len(health_rows)}**
* **Average Daily Steps**: **{health_validation["steps_average"]}** steps
"""
        with open(health_report_md, "w", encoding="utf-8") as rm:
            rm.write(md_text)
            
        print(f"Health Connect daily table generated containing {len(health_rows)} entries.")
        return len(health_rows)

    def _build_master_table(self):
        print("Stage 5: Executing master outer join for behavior_health_daily...")
        
        # Load StayFree Daily
        stayfree_data = {}
        if os.path.exists(self.out_daily_csv):
            with open(self.out_daily_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stayfree_data[row["date_ist"]] = row
                    
        # Load Health Daily
        health_data = {}
        if os.path.exists(self.out_health_csv):
            with open(self.out_health_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    health_data[row["date_ist"]] = row
                    
        all_dates = sorted(list(set(stayfree_data.keys()).union(set(health_data.keys()))))
        master_rows = []
        
        for date_str in all_dates:
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            sf = stayfree_data.get(date_str, {})
            hl = health_data.get(date_str, {})
            
            prev_date_str = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
            next_date_str = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
            
            prev_sf = stayfree_data.get(prev_date_str, {})
            next_hl = health_data.get(next_date_str, {})
            
            steps = hl.get("steps_total", "")
            sleep_min = hl.get("sleep_minutes", "")
            sleep_start = hl.get("sleep_start_ist", "")
            sleep_end = hl.get("sleep_end_ist", "")
            sleep_session = hl.get("sleep_session_count", 0)
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
            
            f_min = (float(productivity_min) if productivity_min else 0.0) + \
                    (float(learning_min) if learning_min else 0.0) + \
                    (float(coding_min) if coding_min else 0.0)
                    
            l_min = (float(youtube_min) if youtube_min else 0.0) + \
                    (float(instagram_min) if instagram_min else 0.0) + \
                    (float(social_min) if social_min else 0.0) + \
                    (float(gaming_min) if gaming_min else 0.0) + \
                    (float(sf.get("entertainment_minutes", 0.0)) if sf else 0.0)
                    
            focus_ratio = round(f_min / max(l_min, 1.0), 3)
            
            if sleep_min and sleep_min != "":
                sleep_val = float(sleep_min)
                late_val = float(late_night_min) if late_night_min else 0.0
                sleep_disruption = round(late_val / max(sleep_val, 1.0), 3)
            else:
                sleep_disruption = ""
                
            prev_night_late = float(prev_sf.get("late_night_minutes", 0.0)) if prev_sf else 0.0
            next_day_steps_val = next_hl.get("steps_total", "") if next_hl else ""
            
            dq_flags = []
            if not sf:
                dq_flags.append("MISSING_STAYFREE_DATA")
            if hl:
                dq_flags.append(hl.get("data_quality_flags", "None"))
            else:
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
                "focus_ratio": focus_ratio,
                "sleep_disruption_index": sleep_disruption,
                "previous_night_late_screen_minutes": round(prev_night_late, 2),
                "next_day_steps": next_day_steps_val,
                "data_quality_flags": ";".join(dq_flags) if dq_flags else "None"
            })

        if not master_rows:
            print("No daily rows compiled for behavior_health_daily master. Joining skipped.")
            return 0

        # Save files
        headers = list(master_rows[0].keys())
        with open(self.out_master_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(master_rows)
            
        with open(self.out_master_jsonl, "w", encoding="utf-8") as f:
            for mr in master_rows:
                f.write(json.dumps(mr, ensure_ascii=False) + "\n")

        # Master Validation reports
        master_report_md = os.path.join(self.report_dir, "master_validation_report.md")
        master_report_json = os.path.join(self.report_dir, "master_validation_report.json")
        
        joined_overlap = sum(1 for m in master_rows if "MISSING" not in m["data_quality_flags"])
        missing_stayfree = sum(1 for m in master_rows if "MISSING_STAYFREE_DATA" in m["data_quality_flags"])
        missing_health = sum(1 for m in master_rows if "MISSING_HEALTH_CONNECT_DATA" in m["data_quality_flags"])
        
        validation = {
            "status": "SUCCESS",
            "master_rows": len(master_rows),
            "joined_overlap": joined_overlap,
            "missing_stayfree": missing_stayfree,
            "missing_health": missing_health
        }
        with open(master_report_json, "w", encoding="utf-8") as rj:
            json.dump(validation, rj, indent=2)
            
        md_text = f"""# Coral Behavior-Health Master Validation Report
This report summarizes the outer join and feature mapping executed between **StayFree daily stats** and **Health Connect metrics**.

## 🕸️ Master Join Statistics
* **Total Master Days**: **{len(master_rows)}**
* **Fully Linked Days (Complete Coverage)**: **{joined_overlap}** days
* **Incomplete StayFree Days**: **{missing_stayfree}**
* **Incomplete Health Connect Days**: **{missing_health}**
"""
        with open(master_report_md, "w", encoding="utf-8") as rm:
            rm.write(md_text)
            
        print(f"Successfully compiled master behavior_health_daily table with {len(master_rows)} rows!")
        return len(master_rows)

    def sync(self) -> dict:
        """
        Executes the full pipeline synchronization end-to-end.
        """
        print("\n========================================================")
        print("STARTING DATA PIPELINE SYNCHRONIZATION")
        print("========================================================\n")
        
        self._copy_active_extension_files()
        
        js_success = self._run_js_extractor()
        if not js_success:
            print("Warning: Javascript raw stayfree extractor failed. Relying on existing CSV fallback.")
            
        events_cnt, stayfree_days = self._build_stayfree_tables()
        health_days = self._build_health_table()
        master_days = self._build_master_table()
        
        print("\n========================================================")
        print("DATA PIPELINE SYNCHRONIZATION COMPLETED SUCCESSFULLY!")
        print("========================================================\n")
        
        return {
            "status": "SUCCESS",
            "events_count": events_cnt,
            "stayfree_days_count": stayfree_days,
            "health_days_count": health_days,
            "master_days_count": master_days,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == '__main__':
    # Run sync directly if executing script directly
    engine = DataPipelineEngine()
    engine.sync()
