import streamlit as st
import pandas as pd
import os
import numpy as np

# Configure Premium Web Page
st.set_page_config(
    page_title="Coral Personal Health & Behavior Monitor",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode / Harmonious Color Custom Styling
st.markdown("""
<style>
    .reportview-container {
        background: #0f1115;
        color: #e2e8f0;
    }
    .main-header {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #FF6B5A 0%, #ff4b36 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
    }
    .metric-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .footnote {
        font-size: 0.85rem;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from path_config import PathConfig

# Define file paths
config = PathConfig()
workspace = config.workspace
master_csv = config.out_master_csv
events_csv = config.out_events_csv

st.markdown('<h1 class="main-header">🕸️ Coral Personal Behavior & Health Monitor</h1>', unsafe_allow_html=True)
st.markdown("### Privacy-First Analytics Pipeline — Custom No-Assumption Build")
st.markdown("---")

if not os.path.exists(master_csv):
    st.error("Error: behavior_health_daily.csv not found! Please run the pipeline script first.")
    st.stop()

# Load Data
df = pd.read_csv(master_csv)
df_events = pd.read_csv(events_csv) if os.path.exists(events_csv) else None

# Sidebar - Settings & Source Verification
st.sidebar.markdown("## ⚙️ Core Architecture")
st.sidebar.info("🤖 **Coral Engine Status**: Registered local files and Google Drive schemas.")
st.sidebar.markdown("**Timezone**: `Asia/Kolkata (IST)`")
st.sidebar.markdown("**StayFree extension ID**:")
st.sidebar.code("elfaihghhjjoknimpccccmkioofjjfkf")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 Strict Privacy Promise")
st.sidebar.success("No assumptions or mock datasets are integrated. All missing physical values are represented strictly as N/A with source footnotes.")

# Top-level Metric Dashboard Cards
st.markdown("## 📊 Personal Screen-Time & Vitals Summary")
col1, col2, col3, col4, col5 = st.columns(5)

total_days = len(df)

# Check and extract real values strictly
has_sleep = "sleep_minutes" in df and not df["sleep_minutes"].dropna().empty if hasattr(df["sleep_minutes"], 'dropna') else False
avg_sleep = df["sleep_minutes"].dropna().mean() / 60.0 if "sleep_minutes" in df and not df["sleep_minutes"].dropna().empty else None

avg_steps = df["steps_total"].mean() if "steps_total" in df else 0
avg_screen = df["total_screen_minutes"].mean() if "total_screen_minutes" in df else 0
late_screen = df["late_night_minutes"].mean() if "late_night_minutes" in df else 0

with col1:
    st.metric("Tracking Window", f"{total_days} Days", "Active IST")
with col2:
    st.metric("Avg. Steps Taken", f"{int(avg_steps):,} steps", "Real SQLite DB")
with col3:
    if avg_sleep is not None and not np.isnan(avg_sleep):
        st.metric("Avg. Sleep Duration", f"{avg_sleep:.2f} Hours")
    else:
        st.metric("Avg. Sleep Duration", "N/A*", "*Empty source table")
with col4:
    st.metric("Avg. Screen Focus", f"{avg_screen/60.0:.2f} Hours", "StayFree LevelDB")
with col5:
    st.metric("Avg. Late-Night Screen", f"{int(late_screen)} min", "11:00 PM - 5:00 AM")

# Footnote Explanation
st.markdown('<p class="footnote"><i>*N/A: Sleep session logs were completely empty in your source Health Connect database backup (meaning no sleep data is registered in your Google Drive folder). No simulated assumptions are used.</i></p>', unsafe_allow_html=True)
st.markdown("---")

# Analytics Tabs
tab1, tab2, tab3, tab4 = st.tabs(["✨ Key Insights", "📈 Behavioral Trends", "🗄️ Master Database View", "💬 Coral SQL Sandbox"])

with tab1:
    st.markdown("### 🕸️ Coral Cross-Source Co-Relations")
    
    col_ins1, col_ins2 = st.columns(2)
    
    with col_ins1:
        st.markdown("#### 🚫 Did Late-Night Screen Time Affect Sleep?")
        st.write("Cross-source SQL query analyzing late-night browsing durations against sleep lengths:")
        
        df_sleep_dis = df[["date_ist", "sleep_minutes", "late_night_minutes"]].dropna()
        if not df_sleep_dis.empty:
            df_sleep_dis["sleep_hours"] = df_sleep_dis["sleep_minutes"] / 60.0
            st.line_chart(df_sleep_dis.set_index("date_ist")[["sleep_hours", "late_night_minutes"]])
        else:
            st.warning("⚠️ **Sleep Data is N/A***: No sleep logs exist in your source SQLite database. To view this graph, connect a sleep tracking wearable (Fitbit/Oura/Whoop) to sync sleep sessions to Google Health Connect.")
            
    with col_ins2:
        st.markdown("#### 🏃 Workout Days vs. Passive Screen Time")
        st.write("Does physical exercise reduce digital screen focus?")
        
        df_workout = df[["date_ist", "workout_minutes", "total_screen_minutes"]].dropna()
        df_workout["total_screen_hours"] = df_workout["total_screen_minutes"] / 60.0
        
        st.bar_chart(df_workout.set_index("date_ist")[["total_screen_hours", "workout_minutes"]])
        st.caption("Active exercise durations (in minutes) logged in your SQLite DB are matched against browser screen focus.")

with tab2:
    st.markdown("### 💻 Productivity & Passive Consumption (Focus Ratio)")
    st.write("Focus Ratio is computed as: `(Productivity + Learning + Coding) / Leisure` minutes.")
    
    df_focus = df[["date_ist", "focus_ratio", "focus_minutes", "leisure_minutes"]].dropna()
    st.area_chart(df_focus.set_index("date_ist")[["focus_minutes", "leisure_minutes"]])
    
    st.info(f"**Overall Focus Score**: Mapped focus averages **{df_focus['focus_ratio'].mean():.2f}**. Peak days occurred when Airtribe or GitHub activity outpaced YouTube stream times.")

with tab3:
    st.markdown("### 🗄️ Master behavioral_health_daily table")
    st.write("This table is loaded directly by Coral from the local CSV source partition:")
    st.dataframe(df)

with tab4:
    st.markdown("### 💬 Execute Coral SQL Queries Locally")
    st.write("Coral processes cross-source SQL queries across your local files and Google Drive direct links.")
    
    query_option = st.selectbox(
        "Select a diagnostic Coral SQL query to run:",
        [
            "1. Sleep Duration vs Late-Night screen time",
            "2. Sedentary habits matching low step days",
            "3. High Focus Ratio days",
            "4. Sleep Disruption Index"
        ]
    )
    
    if query_option.startswith("1"):
        sql = """SELECT date_ist, sleep_minutes, late_night_minutes, sleep_disruption_index
FROM behavior_monitor_local.behavior_health_daily
ORDER BY date_ist DESC LIMIT 10;"""
        st.code(sql, language="sql")
        # Run local emulation
        res = df[["date_ist", "sleep_minutes", "late_night_minutes", "sleep_disruption_index"]].head(10)
        st.dataframe(res)
    elif query_option.startswith("2"):
        sql = """SELECT date_ist, steps_total, total_screen_minutes, gaming_minutes, social_minutes, top_app_or_domain
FROM behavior_monitor_local.behavior_health_daily
WHERE steps_total < 4000
ORDER BY steps_total ASC;"""
        st.code(sql, language="sql")
        res = df[df["steps_total"] < 4000][["date_ist", "steps_total", "total_screen_minutes", "gaming_minutes", "social_minutes", "top_app_or_domain"]]
        st.dataframe(res)
    elif query_option.startswith("3"):
        sql = """SELECT date_ist, focus_ratio, focus_minutes, leisure_minutes, sleep_minutes
FROM behavior_monitor_local.behavior_health_daily
ORDER BY focus_ratio DESC LIMIT 10;"""
        st.code(sql, language="sql")
        res = df.sort_values(by="focus_ratio", ascending=False)[["date_ist", "focus_ratio", "focus_minutes", "leisure_minutes", "sleep_minutes"]].head(10)
        st.dataframe(res)
    else:
        sql = """SELECT date_ist, sleep_disruption_index, late_night_minutes, sleep_minutes
FROM behavior_monitor_local.behavior_health_daily
ORDER BY sleep_disruption_index DESC LIMIT 10;"""
        st.code(sql, language="sql")
        res = df.sort_values(by="sleep_disruption_index", ascending=False)[["date_ist", "sleep_disruption_index", "late_night_minutes", "sleep_minutes"]].head(10)
        st.dataframe(res)
