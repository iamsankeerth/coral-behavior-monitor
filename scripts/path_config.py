import os
import yaml

class PathConfig:
    """
    Centralized path configuration manager for the Coral Behavior-Health Monitor.
    Auto-detects workspace, reads 'config/paths.yaml', and exposes all file/directory paths.
    """
    def __init__(self, workspace=None):
        if workspace is None:
            # Auto-detect workspace as the parent of the 'scripts' directory
            workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.workspace = os.path.abspath(workspace)
        
        # Load paths.yaml
        self.paths_yaml_path = os.path.join(self.workspace, "config", "paths.yaml")
        self.config = {}
        if os.path.exists(self.paths_yaml_path):
            try:
                with open(self.paths_yaml_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Failed to load paths.yaml from {self.paths_yaml_path}: {e}")
        
        # Read parameters from yaml configuration or fall back to defaults
        self.timezone = self.config.get("timezone", "Asia/Kolkata")
        
        # Resolve health connect folder, support env var expansion
        hc_folder = self.config.get("health_connect_export_folder")
        if not hc_folder:
            hc_folder = os.path.join(self.workspace, "data", "raw", "health_connect")
        else:
            hc_folder = os.path.expandvars(hc_folder)
        self.health_connect_export_folder = os.path.abspath(hc_folder)
        
        self.health_connect_latest_file_pattern = self.config.get(
            "health_connect_latest_file_pattern", "Health Connect*.zip"
        )
        
        # Resolve edge profile path, support %USERPROFILE% and environmental vars
        edge_profile = self.config.get("edge_profile_path")
        if not edge_profile:
            edge_profile = os.path.expandvars(r"%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Default")
        else:
            edge_profile = os.path.expandvars(edge_profile)
        self.edge_profile_path = os.path.abspath(edge_profile)
        
        self.stayfree_extension_id = self.config.get(
            "stayfree_extension_id", "elfaihghhjjoknimpccccmkioofjjfkf"
        )
        
        # Derived Paths
        self.raw_csv_path = os.path.join(self.workspace, "stayfree_clean_analytics.csv")
        self.raw_json_path = os.path.join(self.workspace, "stayfree_raw_dump.json")
        self.mapping_path = os.path.join(self.workspace, "config", "category_mapping.yaml")
        
        self.out_events_csv = os.path.join(self.workspace, "data", "coral", "csv", "stayfree_events.csv")
        self.out_events_jsonl = os.path.join(self.workspace, "data", "coral", "jsonl", "stayfree_events.jsonl")
        self.out_daily_csv = os.path.join(self.workspace, "data", "coral", "csv", "stayfree_daily.csv")
        self.out_daily_jsonl = os.path.join(self.workspace, "data", "coral", "jsonl", "stayfree_daily.jsonl")
        
        # Health Connect DB is always inside the health connect export folder
        self.db_path = os.path.join(self.health_connect_export_folder, "health_connect_export.db")
        self.out_health_csv = os.path.join(self.workspace, "data", "coral", "csv", "health_daily.csv")
        self.out_health_jsonl = os.path.join(self.workspace, "data", "coral", "jsonl", "health_daily.jsonl")
        
        self.out_master_csv = os.path.join(self.workspace, "data", "coral", "csv", "behavior_health_daily.csv")
        self.out_master_jsonl = os.path.join(self.workspace, "data", "coral", "jsonl", "behavior_health_daily.jsonl")
        
        self.report_dir = os.path.join(self.workspace, "data", "reports")
        self.log_dir = os.path.join(self.workspace, "data", "logs")
        
        self.stayfree_temp_copy = os.path.join(self.workspace, "stayfree_temp_copy")
        self.stayfree_indexeddb_temp = os.path.join(self.workspace, "stayfree_indexeddb_temp")
        
        # Active extension path resolution (Edge local extension settings & IndexedDB)
        self.active_settings_src = os.path.join(self.edge_profile_path, "Local Extension Settings", self.stayfree_extension_id)
        self.active_indexeddb_src = os.path.join(self.edge_profile_path, "IndexedDB", f"chrome-extension_{self.stayfree_extension_id}_0.indexeddb.leveldb")
