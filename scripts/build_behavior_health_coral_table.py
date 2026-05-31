import sys
import os
# Add scripts directory to path to support in-process imports from any context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_pipeline_engine import DataPipelineEngine

def build_master_table():
    """Delegator function forwarding calls to the consolidated DataPipelineEngine."""
    engine = DataPipelineEngine()
    engine._build_master_table()

if __name__ == '__main__':
    build_master_table()
