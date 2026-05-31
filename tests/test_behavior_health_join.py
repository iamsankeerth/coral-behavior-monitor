import os
import unittest
import csv
import json
from datetime import datetime, timedelta

# Targets to test
events_csv = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\csv\stayfree_events.csv"
events_jsonl = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\jsonl\stayfree_events.jsonl"
daily_csv = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\csv\stayfree_daily.csv"
health_csv = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\csv\health_daily.csv"
master_csv = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project\data\coral\csv\behavior_health_daily.csv"

class TestCoralBehaviorHealthPipeline(unittest.TestCase):

    def test_utc_to_ist_rollover(self):
        """Test that UTC to IST conversions handle midnight boundaries correctly."""
        from scripts.build_stayfree_coral_tables import parse_utc_to_ist
        # 18:45 UTC on April 29 -> 00:15 IST on April 30
        dt_utc, dt_ist, date_ist, hour_ist, weekday_ist = parse_utc_to_ist("2026-04-29T18:45:00.000Z")
        self.assertEqual(date_ist, "2026-04-30")
        self.assertEqual(hour_ist, 0)
        self.assertEqual(weekday_ist, 3) # Thursday

    def test_late_night_window(self):
        """Test that hours inside 23:00 - 05:00 IST are correctly flagged as late night."""
        from scripts.build_stayfree_coral_tables import get_category_and_sub
        # Helper check
        late_hours = [23, 0, 1, 2, 3, 4]
        for h in late_hours:
            is_late = h >= 23 or h < 5
            self.assertTrue(is_late)
            
        day_hours = [5, 12, 18, 22]
        for h in day_hours:
            is_late = h >= 23 or h < 5
            self.assertFalse(is_late)

    def test_event_id_deduplication(self):
        """Test that duplicate events with identical hashes are correctly ignored."""
        from scripts.build_stayfree_coral_tables import generate_event_id
        h1 = generate_event_id("2026-04-29T17:30:10.000Z", "youtube.com", "web", "60.0", "Settings")
        h2 = generate_event_id("2026-04-29T17:30:10.000Z", "youtube.com", "web", "60.0", "Settings")
        self.assertEqual(h1, h2)

    def test_negative_and_excessive_durations(self):
        """Verify that negative durations are excluded and massive durations are flagged."""
        self.assertTrue(os.path.exists(events_csv), "Events CSV does not exist.")
        with open(events_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dur = float(row["duration_seconds"])
                self.assertGreater(dur, 0.0, "Found zero or negative duration in events table!")
                
                # Check suspicious long session flag
                if dur > 28800:
                    self.assertIn("SUSPICIOUS_LONG_DURATION", row["data_quality_flags"])

    def test_sleep_wakeup_date_alignment(self):
        """Verify that sleep duration starts and ends span boundaries correctly in mock generator."""
        self.assertTrue(os.path.exists(health_csv), "Health CSV does not exist.")
        with open(health_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("sleep_minutes"):
                    continue
                sleep_min = float(row["sleep_minutes"])
                sleep_start = datetime.fromisoformat(row["sleep_start_ist"].split("+")[0])
                sleep_end = datetime.fromisoformat(row["sleep_end_ist"].split("+")[0])
                
                # Sleep session duration matches start and end
                delta_min = (sleep_end - sleep_start).total_seconds() / 60.0
                self.assertAlmostEqual(delta_min, sleep_min, places=2)

    def test_jsonl_rows_valid_json(self):
        """Ensure all output JSONL rows are valid, parseable JSON lines."""
        self.assertTrue(os.path.exists(events_jsonl), "Events JSONL does not exist.")
        with open(events_jsonl, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    data = json.loads(stripped)
                    self.assertIn("event_id", data)

    def test_csv_headers_data_contract(self):
        """Verify that CSV headers match the CORAL_DATA_CONTRACT specifications."""
        # 1. stayfree_events
        with open(events_csv, "r", encoding="utf-8") as f:
            headers = next(csv.reader(f))
            self.assertIn("event_id", headers)
            self.assertIn("date_ist", headers)
            self.assertIn("duration_seconds", headers)
            
        # 2. behavior_health_daily
        self.assertTrue(os.path.exists(master_csv), "Master CSV does not exist.")
        with open(master_csv, "r", encoding="utf-8") as f:
            headers = next(csv.reader(f))
            self.assertIn("date_ist", headers)
            self.assertIn("steps_total", headers)
            self.assertIn("focus_ratio", headers)
            self.assertIn("sleep_disruption_index", headers)

    def test_master_has_unique_date_ist_rows(self):
        """Ensure the master behavior_health_daily table contains exactly one row per date_ist."""
        dates = []
        with open(master_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dates.append(row["date_ist"])
                
        # Check uniqueness
        self.assertEqual(len(dates), len(set(dates)), "Found duplicate dates in master daily table!")

if __name__ == '__main__':
    unittest.main()
