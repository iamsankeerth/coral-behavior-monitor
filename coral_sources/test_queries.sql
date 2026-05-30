-- ====================================================================
-- CORAL PERSONAL MONITOR DIAGNOSTIC & BEHAVIORAL SQL QUERIES
-- ====================================================================

-- 1. Basic Master Table Connection Verification
-- Validates the successful schema compilation and outer join.
SELECT 
    date_ist, 
    steps_total, 
    sleep_minutes, 
    total_screen_minutes, 
    data_quality_flags
FROM behavior_monitor_local.behavior_health_daily 
ORDER BY date_ist DESC 
LIMIT 5;


-- 2. Sleep Duration vs. Late-Night Digital Screen Activity
-- Explores matched trends between late-night focus and subsequent sleep lengths over a 2-week window.
SELECT 
    date_ist, 
    sleep_minutes, 
    late_night_minutes,
    sleep_disruption_index
FROM behavior_monitor_local.behavior_health_daily
ORDER BY date_ist DESC
LIMIT 14;


-- 3. Top 10 Worst Sleep Durations and Digital Activity
-- Identifies if the shortest sleep durations are matched with heavy YouTube or Instagram focus.
SELECT 
    date_ist, 
    sleep_minutes, 
    late_night_minutes, 
    youtube_minutes, 
    instagram_minutes, 
    top_app_or_domain
FROM behavior_monitor_local.behavior_health_daily
WHERE sleep_minutes IS NOT NULL
ORDER BY sleep_minutes ASC
LIMIT 10;


-- 4. High Instagram / Reels Engagement Days
-- Isolates dates with heaviest social media focus and matches them against active steps and sleep.
SELECT 
    date_ist, 
    instagram_minutes, 
    instagram_reels_minutes_if_detected, 
    sleep_minutes, 
    steps_total
FROM behavior_monitor_local.behavior_health_daily
ORDER BY instagram_minutes DESC
LIMIT 10;


-- 5. Workout Engagement vs. Active Screen Time
-- Analyses whether planned exercise days correspond with decreases in passive digital usage.
SELECT 
    date_ist, 
    workout_minutes, 
    total_screen_minutes, 
    focus_ratio
FROM behavior_monitor_local.behavior_health_daily
WHERE workout_minutes > 0
ORDER BY date_ist DESC;


-- 6. High Focus Ratio Profiles
-- Highlights your most productive days (Focus Ratio = Productive Focus / Passive Leisure).
SELECT 
    date_ist, 
    focus_ratio, 
    focus_minutes, 
    leisure_minutes, 
    sleep_minutes, 
    steps_total
FROM behavior_monitor_local.behavior_health_daily
ORDER BY focus_ratio DESC
LIMIT 10;


-- 7. Late-Night Sleep Disruption Index
-- Ranks dates by the highest concentration of late-night screen time relative to sleep duration.
SELECT 
    date_ist, 
    sleep_disruption_index, 
    late_night_minutes, 
    sleep_minutes
FROM behavior_monitor_local.behavior_health_daily
WHERE sleep_minutes IS NOT NULL
ORDER BY sleep_disruption_index DESC
LIMIT 10;
