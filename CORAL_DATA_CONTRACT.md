# Coral Data Contract

This data contract defines the schema, types, properties, and constraints for the tables exposed to Coral in the **Personal Behavior & Health Monitor powered by Coral** project.

---

## 📋 Table 1: `stayfree_events`

* **Purpose**: Event-level digital screen-time/session tracking.
* **Granularity**: One row per distinct active focus session or imported mobile event.
* **Storage Location**: `data/coral/csv/stayfree_events.csv` & `data/coral/jsonl/stayfree_events.jsonl`

### Schema Definition

| Column | Type | Nullable | Description / Rules |
| :--- | :--- | :---: | :--- |
| `event_id` | String | No | Primary Key. Stable hash of `timestamp_utc`, `domain_or_app`, `platform`, `duration_seconds`, and `source`. |
| `timestamp_utc` | String | No | ISO-8601 UTC timestamp of session start. |
| `timestamp_ist` | String | No | ISO-8601 Asia/Kolkata (IST) timestamp of session start. |
| `date_ist` | String | No | Date string `YYYY-MM-DD` in IST. Used for joins. |
| `hour_ist` | Integer | No | Hour of day (0-23) in IST. |
| `weekday_ist` | Integer | No | Day of week (0=Monday, 6=Sunday) in IST. |
| `platform` | String | No | Operating platform: `web` or `android`. |
| `device_type` | String | No | Device category: `PC-Windows` or `Mobile-Android`. |
| `domain_or_app` | String | No | The untransformed tracking identifier (e.g. `youtube.com` or `com.google.android.youtube`). |
| `app_or_domain_normalized` | String | No | Lowercase, trimmed, scrubbed domain or package. |
| `category` | String | No | Mapped high-level category (e.g. `gaming`, `productivity`, `social`, `entertainment`, etc.). |
| `subcategory` | String | Yes | Sub-classification (e.g. `youtube_shorts`, `instagram_reels`, etc.). |
| `duration_seconds` | Double | No | Active usage length in seconds. |
| `duration_minutes` | Double | No | Active usage length in minutes. |
| `is_web` | Boolean | No | True if `platform == 'web'`. |
| `is_android` | Boolean | No | True if `platform == 'android'`. |
| `is_late_night` | Boolean | No | True if `hour_ist` is between **23** (11 PM) and **5** (5 AM) inclusive. |
| `late_night_window` | String | Yes | Categorization of sleep boundary: `23:00-01:00`, `01:00-03:00`, `03:00-05:00`, or `None`. |
| `source` | String | No | Provenance marker indicating DB source key/table. |
| `raw_key` | String | No | Key in the original LevelDB database. |
| `raw_payload_available` | Boolean | No | True if raw un-serialized data is stored in raw JSON backups. |
| `data_quality_flags` | String | Yes | Semicolon-delimited validation warnings (e.g., `SUSPICIOUS_LONG_DURATION` if > 8 hrs). |

---

## 📊 Table 2: `stayfree_daily`

* **Purpose**: Consolidated daily digital behavior aggregates.
* **Granularity**: One row per distinct local date (`date_ist`).
* **Storage Location**: `data/coral/csv/stayfree_daily.csv` & `data/coral/jsonl/stayfree_daily.jsonl`

### Schema Definition

| Column | Type | Nullable | Description / Rules |
| :--- | :--- | :---: | :--- |
| `date_ist` | String | No | Primary Key. Format: `YYYY-MM-DD`. |
| `total_screen_seconds` | Double | No | Cumulative screen time. |
| `total_screen_minutes` | Double | No | Cumulative screen time in minutes. |
| `android_seconds` | Double | No | Total Android usage. |
| `android_minutes` | Double | No | Total Android usage in minutes. |
| `web_seconds` | Double | No | Total Desktop Edge usage. |
| `web_minutes` | Double | No | Total Desktop Edge usage in minutes. |
| `late_night_seconds` | Double | No | Screen time between 11 PM and 5 AM. |
| `late_night_minutes` | Double | No | Screen time in minutes between 11 PM and 5 AM. |
| `youtube_seconds` | Double | No | Total YouTube duration (web + android). |
| `youtube_minutes` | Double | No | Total YouTube duration in minutes. |
| `youtube_shorts_seconds_if_detected` | Double | Yes | Estimated YouTube Shorts duration. |
| `youtube_shorts_minutes_if_detected` | Double | Yes | Estimated YouTube Shorts duration in minutes. |
| `instagram_seconds` | Double | No | Total Instagram duration. |
| `instagram_minutes` | Double | No | Total Instagram duration in minutes. |
| `instagram_reels_seconds_if_detected` | Double | Yes | Estimated Instagram Reels duration. |
| `instagram_reels_minutes_if_detected` | Double | Yes | Estimated Instagram Reels duration in minutes. |
| `social_seconds` | Double | No | Duration spent in social media category. |
| `social_minutes` | Double | No | Duration in minutes spent in social media. |
| `gaming_seconds` | Double | No | Duration spent in gaming category. |
| `gaming_minutes` | Double | No | Duration in minutes spent in gaming. |
| `productivity_seconds` | Double | No | Duration spent in productivity category. |
| `productivity_minutes` | Double | No | Duration in minutes spent in productivity. |
| `learning_seconds` | Double | No | Duration spent in learning category. |
| `learning_minutes` | Double | No | Duration in minutes spent in learning. |
| `coding_seconds` | Double | No | Duration spent in coding category. |
| `coding_minutes` | Double | No | Duration in minutes spent in coding. |
| `communication_seconds` | Double | No | Duration spent in communication category. |
| `communication_minutes` | Double | No | Duration in minutes spent in communication. |
| `entertainment_seconds` | Double | No | Duration spent in entertainment category. |
| `entertainment_minutes` | Double | No | Duration in minutes spent in entertainment. |
| `session_count` | Integer | No | Count of active sessions. |
| `android_session_count` | Integer | No | Count of Android sessions. |
| `web_session_count` | Integer | No | Count of desktop browser sessions. |
| `top_app_or_domain` | String | No | Most heavily used domain/app on this date. |
| `top_category` | String | No | Most heavily used category on this date. |
| `longest_session_seconds` | Double | No | Duration of the longest single session. |
| `avg_session_seconds` | Double | No | Average session length on this date. |
| `median_session_seconds` | Double | No | Median session length on this date. |
| `first_event_ist` | String | Yes | ISO-8601 time of first recorded event. |
| `last_event_ist` | String | Yes | ISO-8601 time of last recorded event. |
| `reels_detection_confidence` | String | No | Confidence level: `HIGH`, `LOW`, or `NONE`. |
| `shorts_detection_confidence` | String | No | Confidence level: `HIGH`, `LOW`, or `NONE`. |
| `data_quality_flags` | String | Yes | Quality codes. |

---

## 🏃 Table 3: `health_daily`

* **Purpose**: Daily Health Connect aggregations.
* **Granularity**: One row per distinct local date (`date_ist`).
* **Storage Location**: `data/coral/csv/health_daily.csv` & `data/coral/jsonl/health_daily.jsonl`

### Schema Definition

| Column | Type | Nullable | Description / Rules |
| :--- | :--- | :---: | :--- |
| `date_ist` | String | No | Primary Key. Format: `YYYY-MM-DD`. |
| `steps_total` | Integer | Yes | Total steps taken during the day. |
| `sleep_minutes` | Double | Yes | Total minutes of sleep recorded. Default: mapped to wake-up date. |
| `sleep_start_ist` | String | Yes | ISO-8601 timestamp of sleep session start. |
| `sleep_end_ist` | String | Yes | ISO-8601 timestamp of sleep session end. |
| `sleep_session_count` | Integer | Yes | Total distinct sleep sessions recorded. |
| `awake_minutes_if_available` | Double | Yes | Restless/awake sleep stages in minutes. |
| `light_sleep_minutes_if_available` | Double | Yes | Light sleep stages in minutes. |
| `deep_sleep_minutes_if_available` | Double | Yes | Deep sleep stages in minutes. |
| `rem_sleep_minutes_if_available` | Double | Yes | REM sleep stages in minutes. |
| `workout_minutes` | Double | Yes | Active exercise duration in minutes. |
| `workout_count` | Integer | Yes | Number of distinct workout logs. |
| `active_calories_if_available` | Double | Yes | Active energy expenditure in kilocalories. |
| `heart_rate_avg_if_available` | Double | Yes | Mean beats per minute recorded. |
| `source_file` | String | No | SQLite file or CSV source of data. |
| `data_quality_flags` | String | Yes | Quality alerts. |

---

## 🕸️ Table 4: `behavior_health_daily`

* **Purpose**: Combined master Coral reasoning table representing the cross-source join of digital activity and physical health metrics.
* **Granularity**: One row per local date (`date_ist`).
* **Storage Location**: `data/coral/csv/behavior_health_daily.csv` & `data/coral/jsonl/behavior_health_daily.jsonl`

### Schema Definition

| Column | Type | Nullable | Description / Rules |
| :--- | :--- | :---: | :--- |
| `date_ist` | String | No | Primary Key. Format: `YYYY-MM-DD`. |
| `steps_total` | Integer | Yes | Steps from `health_daily`. |
| `sleep_minutes` | Double | Yes | Total sleep from `health_daily`. |
| `sleep_start_ist` | String | Yes | Sleep start time. |
| `sleep_end_ist` | String | Yes | Sleep end time. |
| `sleep_session_count` | Integer | Yes | Total sleep sessions. |
| `deep_sleep_minutes_if_available` | Double | Yes | Deep sleep minutes. |
| `rem_sleep_minutes_if_available` | Double | Yes | REM sleep minutes. |
| `workout_minutes` | Double | Yes | Active workout minutes. |
| `workout_count` | Integer | Yes | Total workout count. |
| `total_screen_minutes` | Double | Yes | Screen minutes from `stayfree_daily`. |
| `android_minutes` | Double | Yes | Android minutes. |
| `web_minutes` | Double | Yes | Web browser minutes. |
| `late_night_minutes` | Double | Yes | Late-night screen minutes. |
| `youtube_minutes` | Double | Yes | YouTube minutes. |
| `youtube_shorts_minutes_if_detected` | Double | Yes | YouTube Shorts minutes. |
| `instagram_minutes` | Double | Yes | Instagram minutes. |
| `instagram_reels_minutes_if_detected` | Double | Yes | Instagram Reels minutes. |
| `social_minutes` | Double | Yes | Social media minutes. |
| `gaming_minutes` | Double | Yes | Gaming minutes. |
| `productivity_minutes` | Double | Yes | Productivity minutes. |
| `learning_minutes` | Double | Yes | Learning minutes. |
| `coding_minutes` | Double | Yes | Coding minutes. |
| `session_count` | Integer | Yes | Total session count. |
| `top_app_or_domain` | String | Yes | Top app/domain used. |
| `top_category` | String | Yes | Top category. |
| `focus_minutes` | Double | Yes | Mapped as: `productivity_minutes + learning_minutes + coding_minutes`. |
| `leisure_minutes` | Double | Yes | Mapped as: `youtube_minutes + instagram_minutes + social_minutes + gaming_minutes + entertainment_minutes`. |
| `focus_ratio` | Double | Yes | Calculated: `focus_minutes / max(leisure_minutes, 1)`. |
| `sleep_disruption_index` | Double | Yes | Calculated: `late_night_minutes / max(sleep_minutes, 1)`. |
| `previous_night_late_screen_minutes` | Double | Yes | `late_night_minutes` from the previous date (`date_ist - 1 day`). |
| `next_day_steps` | Integer | Yes | `steps_total` from the next date (`date_ist + 1 day`). |
| `data_quality_flags` | String | Yes | Quality alerts. e.g. `MISSING_HEALTH_CONNECT_DATA` or `MISSING_STAYFREE_DATA`. |

---

## 💬 Coral Example Queries & Questions

The Master Joined Table enables powerful, non-causative correlative analysis:

### 1. Does late-night screen time correlate with lower sleep duration?
```sql
SELECT 
    date_ist, 
    sleep_minutes, 
    late_night_minutes, 
    sleep_disruption_index
FROM behavior_monitor_local.behavior_health_daily
WHERE sleep_minutes IS NOT NULL 
  AND late_night_minutes > 15
ORDER BY late_night_minutes DESC;
```

### 2. Which digital habits are associated with low-step days?
```sql
SELECT 
    date_ist, 
    steps_total, 
    total_screen_minutes, 
    gaming_minutes, 
    social_minutes,
    top_app_or_domain
FROM behavior_monitor_local.behavior_health_daily
WHERE steps_total < 4000
ORDER BY steps_total ASC;
```

### 3. Do workout days correlate with reduced screen time or higher focus?
```sql
SELECT 
    AVG(total_screen_minutes) AS avg_screen_workout_days,
    AVG(focus_ratio) AS avg_focus_ratio_workout_days
FROM behavior_monitor_local.behavior_health_daily
WHERE workout_minutes > 0;
```
