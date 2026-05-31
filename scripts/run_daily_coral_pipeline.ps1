# ====================================================================
# CORAL DATA PIPELINE RUNNER (DAILY AUTOMATION)
# ====================================================================
$ErrorActionPreference = "Stop"

# Get the script's directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Execute the consolidated DataPipelineEngine directly in-process
& "$scriptDir\..\.venv\Scripts\python.exe" "$scriptDir\data_pipeline_engine.py"
