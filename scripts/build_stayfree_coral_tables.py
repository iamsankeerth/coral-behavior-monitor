import sys
import os
# Add scripts directory to path to support in-process imports from any context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_pipeline_engine import DataPipelineEngine

def build_tables():
    """Delegator function forwarding calls to the consolidated DataPipelineEngine."""
    engine = DataPipelineEngine()
    engine._build_stayfree_tables()

def generate_event_id(ts_utc, domain, plat, dur, src):
    """Delegator utility for stable hash generation."""
    engine = DataPipelineEngine()
    return engine.generate_event_id(ts_utc, domain, plat, dur, src)

def get_category_and_sub(domain_or_app):
    """Delegator utility for category mapping."""
    engine = DataPipelineEngine()
    return engine.get_category_and_sub(domain_or_app)

def parse_utc_to_ist(time_str):
    """Delegator utility for timezone conversions."""
    engine = DataPipelineEngine()
    return engine.parse_utc_to_ist(time_str)

if __name__ == '__main__':
    build_tables()
