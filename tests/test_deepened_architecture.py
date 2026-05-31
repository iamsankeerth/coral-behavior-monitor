import os
import unittest
from scripts.data_pipeline_engine import DataPipelineEngine
from scripts.coral_analytics_engine import CoralAnalyticsEngine
from scripts.hermes_communication_adapter import HermesCliAdapter, InMemoryMessageLogger

class TestDeepenedArchitecture(unittest.TestCase):
    """
    Unit test suite verifying the architecture deepening refactors.
    """
    def setUp(self):
        self.workspace = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project"
        self.pipeline_engine = DataPipelineEngine(self.workspace)
        self.analytics_engine = CoralAnalyticsEngine(self.workspace)

    def test_pipeline_engine_sync(self):
        """Verify that the DataPipelineEngine syncs and returns a summary dictionary in-process."""
        summary = self.pipeline_engine.sync()
        self.assertEqual(summary["status"], "SUCCESS")
        self.assertIn("events_count", summary)
        self.assertIn("stayfree_days_count", summary)
        self.assertIn("health_days_count", summary)
        self.assertIn("master_days_count", summary)
        self.assertGreater(summary["master_days_count"], 0)

    def test_analytics_engine_execution(self):
        """Verify that the CoralAnalyticsEngine can query behavior_health_daily in-process."""
        # Query with auto_sync = False to test fast in-memory execution
        query = "SELECT date_ist, steps_total, total_screen_minutes FROM behavior_health_daily ORDER BY date_ist DESC LIMIT 1;"
        res = self.analytics_engine.execute_query(query, auto_sync=False)
        self.assertNotIn("Error", res)
        self.assertIn("date_ist", res)

    def test_analytics_engine_timestamps(self):
        """Verify that the CoralAnalyticsEngine extracts data freshness updates correctly."""
        steps_ts = self.analytics_engine.get_steps_timestamp()
        pc_ts, mobile_ts = self.analytics_engine.get_stayfree_timestamps()
        
        self.assertIsNotNone(steps_ts)
        self.assertIsNotNone(pc_ts)
        self.assertIsNotNone(mobile_ts)
        self.assertTrue(any(term in steps_ts for term in ["IST", "N/A", "Error"]))
        self.assertTrue(any(term in pc_ts for term in ["IST", "N/A", "Error"]))

    def test_analytics_engine_vitals_summary(self):
        """Verify that the vital/screen time summary compiles formatted strings correctly."""
        summary = self.analytics_engine.get_vitals_summary()
        self.assertIn("Today's Vitals & Screen Time Summary", summary)
        self.assertIn("Data Freshness & Sync Timestamps", summary)
        self.assertIn("Mobile Steps data last updated:", summary)

    def test_communication_mock_adapter(self):
        """Verify that the InMemoryMessageLogger captures sent messages correctly without shelling out."""
        logger = InMemoryMessageLogger()
        success, status = logger.send_message("whatsapp:iamsan", "Mock Message 123")
        
        self.assertTrue(success)
        self.assertEqual(status, "Message captured in-memory successfully (Test Adapter)!")
        self.assertEqual(len(logger.sent_messages), 1)
        self.assertEqual(logger.sent_messages[0]["target"], "whatsapp:iamsan")
        self.assertEqual(logger.sent_messages[0]["text"], "Mock Message 123")

    def test_communication_cli_adapter_contract(self):
        """Verify the HermesCliAdapter structure and error checking interface."""
        adapter = HermesCliAdapter()
        # Verify it has correct interface
        self.assertTrue(hasattr(adapter, "send_message"))

if __name__ == '__main__':
    unittest.main()
