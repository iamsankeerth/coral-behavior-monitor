# 3-Minute YouTube Demo Video Script

Keep your video fast-paced, highly visual, and strictly **under 3 minutes** to meet hackathon guidelines.

---

## ⏱️ Video Timeline & Screen Script

### 🎬 0:00 - 0:20 | Part 1: The Problem (Hook)
* **On Screen**: Show the Streamlit dashboard home page or a quick slide showing scattered app logos (Google Fit, StayFree, Excel).
* **Voiceover**: 
  > *"We track our physical health on our phones and our digital habits on our computers. But this data is scattered across isolated databases. You can't easily query if late-night screen time on your PC is destroying your sleep quality, or which specific gaming apps correlate with sedentary, low-step days. That changes today."*

### 🛠️ 0:20 - 0:45 | Part 2: The Data Sources
* **On Screen**: Open VS Code. Briefly show `stayfree_clean_analytics.csv` (19,366 screen events) and `health_daily.csv` (steps, sleep stages).
* **Voiceover**:
  > *"Introducing the Personal Behavior & Health Monitor, built for the Coral Hackathon. We extract 19,000+ local screen focus sessions from StayFree across Edge and Android, alongside your Health Connect exports. To protect your absolute privacy, all sensitive details remain local and sandbox-isolated."*

### 🎛️ 0:45 - 1:20 | Part 3: The Coral Source Integration
* **On Screen**: Open `coral_sources/behavior_monitor_local.yaml`. Scroll through the configuration highlighting the four tables: `stayfree_events`, `stayfree_daily`, `health_daily`, and the master `behavior_health_daily`.
* **Voiceover**:
  > *"Coral is the central query and reasoning engine of our monitor. By declaring our local CSV schemas in this single Coral Source configuration file, Coral registers the datasets and exposes them instantly as standard ANSI SQL databases. There are no heavy server setups—just clean, unified tables."*

### 💻 1:20 - 2:10 | Part 4: Coral SQL Queries in Action
* **On Screen**: Open a terminal and execute a query, or show the queries tab in the dashboard running:
  1. `SELECT date_ist, sleep_minutes, late_night_minutes FROM ...`
  2. `SELECT date_ist, focus_ratio, focus_minutes FROM ...`
* **Voiceover**:
  > *"Watch Coral in action. We query our master behavioral join table to match late-night screen minutes directly with our sleep duration. Instant co-relations are revealed! Coral allows us to filter our lowest sleep dates and immediately see if they align with YouTube or Reels focus. We can even check our Focus Ratio—our ratio of productive learning vs passive gaming—matching it with physical steps."*

### 📊 2:10 - 2:40 | Part 5: The Streamlit Dashboard
* **On Screen**: Show the Streamlit dashboard in action. Click on the "Key Insights" tab, show the charts plotting Sleep Disruption and Screen Time splits (Mobile representing 71.5%!).
* **Voiceover**:
  > *"To present these Coral-powered insights, we built a beautiful Streamlit dashboard. It showcases top-level metrics, platform screen shares, and daily focus ratios. We've even built a live Coral SQL Sandbox tab directly inside the UI, allowing users to copy and test diagnostic queries locally."*

### 🏁 2:40 - 3:00 | Part 6: Wrap Up & Future
* **On Screen**: Show the GitHub repository README and star icon, then show the closing slide.
* **Voiceover**:
  > *"By using Coral as our query engine, we built a local, privacy-first pipeline that reveals matched behavioral insights. In the future, we will integrate Coral's Google Drive direct source. Star our repo, check out the live demo, and take control of your habits today. Thank you!"*
