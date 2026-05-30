# Coral Agent Context: Personal Behavior & Health Monitor

This context document guides AI agents (and Coral reasoning models) on how to interpret, parse, and reason over the **Behavior & Health Monitor** database.

---

## 📅 1. Timezone and Date Boundaries
* **Timezone**: All dates and timestamps are calculated in **Asia/Kolkata (IST)** / UTC + 5:30.
* **Join Key**: The primary linkage key between all daily datasets is **`date_ist`** (format: `YYYY-MM-DD`). 
* **UTC to IST Shift**: Screen sessions starting late-night UTC often roll over to the *next day* in local IST. The pipeline handles this explicitly during aggregation to prevent distorting daily focus totals.

---

## 🛏️ 2. Sleep Alignment Rule
* **Wake-Up Date Assignment**: In alignment with standard clinical sleep analytics, sleep sessions are assigned to the **wake-up date** (end of sleep session) rather than the sleep start date. 
  * *Example*: If you fall asleep at 11:30 PM on May 29 and wake up at 7:30 AM on May 30, the sleep duration (480 minutes) is credited to **May 30**. 
  * This matches previous-night behaviors directly with current-day recovery metrics.

---

## 🎯 3. Focus and Leisure Metrics Definitions
* **`focus_minutes`**: Sum of screen focus spent in productive, task-oriented categories:
  * **Productivity** (e.g. `chatgpt.com`, `com.openai.chatgpt`)
  * **Learning** (e.g. `airtribe.live`, `wemakedevs.org`)
  * **Coding** (e.g. `github.com`, `withcoral.com`, `stackoverflow.com`)
* **`leisure_minutes`**: Sum of screen focus spent in entertainment, gaming, or passive consumption:
  * **YouTube** (`youtube.com` + `com.google.android.youtube`)
  * **Instagram** (`com.instagram.android`)
  * **Social Media / Chat** (`com.twitter.android`, `com.snapchat.android`, `threads`)
  * **Gaming** (`com.supercell.clashofclans`, `com.supercell.clashroyale`, `com.pubg.imobile`, `vlr.gg`)
  * **Entertainment** (`in.startv.hotstar`, `netflix.com`, `spotify.com`)
* **`focus_ratio`**: Calculated as `focus_minutes / max(leisure_minutes, 1.0)`. 
  * A ratio **> 1.0** indicates more active professional/learning focus than passive consumption.
* **`sleep_disruption_index`**: Calculated as `late_night_minutes / max(sleep_minutes, 1.0)`.
  * Quantifies the concentration of sleep-sensitive digital focus relative to total sleep recovery.

---

## 📹 4. Reels and Shorts Detection Metrics
* **Instagram Reels / YouTube Shorts**: StayFree does not natively split out Reels or Shorts inside synced Android packages because Android package names are monolithic (`com.instagram.android` and `com.google.android.youtube`). 
* **Confidence Scores**:
  * **`HIGH`**: Specific sub-URLs matching `/shorts` or `/reels` were detected in browser logs.
  * **`LOW`**: Standard Instagram/YouTube focus was recorded, but individual content paths were unclassified.
  * **`NONE`**: Zero interactions with YouTube or Instagram occurred on this date.
  * *Important*: Avoid assuming all Instagram usage is Reels, or all YouTube usage is Shorts.

---

## ⚠️ 5. Analytical and Clinical Safety Guidelines
* **Correlation is NOT Causation**: This database reveals statistical correlations and behavioral matches, not medical causation. All queries, reports, and dashboards must use descriptive, non-causative language (e.g., "associated with", "matched trends", "correlated patterns", "linked on dates").
* **Data Completeness**: If you travel across timezones or clear browser storage, some dates may contain missing tracking events. These are flagged with `MISSING_STAYFREE_DATA` or `MISSING_HEALTH_CONNECT_DATA` inside `data_quality_flags` instead of throwing execution errors.
