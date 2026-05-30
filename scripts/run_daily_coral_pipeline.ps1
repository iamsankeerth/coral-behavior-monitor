# ====================================================================
# CORAL DATA PIPELINE RUNNER (DAILY AUTOMATION)
# ====================================================================

$ErrorActionPreference = "Stop"
$workspace = "C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project"
$logFile = "$workspace\data\logs\pipeline_run.log"

# Ensure log directory exists
New-Item -ItemType Directory -Path "$workspace\data\logs" -Force | Out-Null

function Log-Message {
    param([string]$message, [string]$level = "INFO")
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $logLine = "[$ts] [$level] $message"
    
    $color = "Green"
    if ($level -eq "ERROR") { $color = "Red" }
    elseif ($level -eq "WARN") { $color = "Yellow" }
    
    Write-Host $logLine -ForegroundColor $color
    Add-Content -Path $logFile -Value $logLine
}

Log-Message "Starting Coral Behavior-Health Daily Pipeline..."

# --------------------------------------------------------------------
# STEP 1: Refresh StayFree Extraction
# --------------------------------------------------------------------
Log-Message "Step 1: Attempting to copy latest StayFree database..."
try {
    $src = "$env:USERPROFILE\AppData\Local\Microsoft\Edge\User Data\Default\Local Extension Settings\elfaihghhjjoknimpccccmkioofjjfkf"
    $dst = "$workspace\stayfree_temp_copy"
    
    if (Test-Path $src) {
        Log-Message "Copying active database files (excluding locks)..."
        if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
        New-Item -ItemType Directory -Path $dst -Force | Out-Null
        Copy-Item -Path "$src\*" -Destination $dst -Exclude "LOCK" -Force
        Log-Message "StayFree database files successfully duplicated to stayfree_temp_copy."
        
        # Execute extractor
        Log-Message "Executing extract_stayfree.js to refresh CSV..."
        node "$workspace\extract_stayfree.js" | Out-Null
        Log-Message "StayFree CSV refreshed successfully."
        
        # Copy StayFree IndexedDB leveldb files
        $indexeddb_src = "$env:USERPROFILE\AppData\Local\Microsoft\Edge\User Data\Default\IndexedDB\chrome-extension_elfaihghhjjoknimpccccmkioofjjfkf_0.indexeddb.leveldb"
        $indexeddb_dst = "$workspace\stayfree_indexeddb_temp"
        if (Test-Path $indexeddb_src) {
            Log-Message "Copying active IndexedDB database files (excluding locks)..."
            if (Test-Path $indexeddb_dst) { Remove-Item $indexeddb_dst -Recurse -Force }
            New-Item -ItemType Directory -Path $indexeddb_dst -Force | Out-Null
            Copy-Item -Path "$indexeddb_src\*" -Destination $indexeddb_dst -Exclude "LOCK" -Force
            Log-Message "StayFree IndexedDB files successfully duplicated to stayfree_indexeddb_temp."
        } else {
            Log-Message "StayFree IndexedDB directory not found." "WARN"
        }
    } else {
        Log-Message "StayFree local extension directory not found. Proceeding with backup CSV." "WARN"
    }
} catch {
    Log-Message "Failed to copy active StayFree database: $_. Proceeding with backup CSV." "WARN"
}

# --------------------------------------------------------------------
# STEP 2: Build StayFree Coral Tables
# --------------------------------------------------------------------
try {
    Log-Message "Step 2: Transforming and validating StayFree Coral tables..."
    & "$workspace\.venv\Scripts\python.exe" "$workspace\scripts\build_stayfree_coral_tables.py"
    Log-Message "StayFree tables compiled successfully."
} catch {
    Log-Message "Critical failure compiling StayFree tables: $_" "ERROR"
    Exit 1
}

# --------------------------------------------------------------------
# STEP 3: Locate latest Health Connect export
# --------------------------------------------------------------------
Log-Message "Step 3: Checking Health Connect data sources..."
& "$workspace\.venv\Scripts\python.exe" "$workspace\scripts\inspect_health_connect_db.py"

# --------------------------------------------------------------------
# STEP 4: Build Health Connect Daily
# --------------------------------------------------------------------
try {
    Log-Message "Step 4: Compiling Health Connect daily dataset..."
    & "$workspace\.venv\Scripts\python.exe" "$workspace\scripts\build_health_coral_table.py"
    Log-Message "health_daily table generated successfully."
} catch {
    Log-Message "Critical failure generating health_daily: $_" "ERROR"
    Exit 1
}

# --------------------------------------------------------------------
# STEP 5: Build behavior_health_daily master
# --------------------------------------------------------------------
try {
    Log-Message "Step 5: Executing master outer join for behavior_health_daily..."
    & "$workspace\.venv\Scripts\python.exe" "$workspace\scripts\build_behavior_health_coral_table.py"
    Log-Message "Master behavior_health_daily joined successfully!"
} catch {
    Log-Message "Critical failure compiling master daily join: $_" "ERROR"
    Exit 1
}

# --------------------------------------------------------------------
# STEP 6: Execute Coral SQL CLI (Graceful fallback)
# --------------------------------------------------------------------
Log-Message "Step 6: Checking Coral CLI status..."
$coralExists = Get-Command -Name "coral" -ErrorAction SilentlyContinue

if ($coralExists) {
    try {
        Log-Message "Coral CLI found. Verifying source schemas..."
        coral source lint "$workspace\coral_sources\behavior_monitor_local.yaml"
        Log-Message "Coral YAML syntax valid."
    } catch {
        Log-Message "Coral source lint failed: $_" "WARN"
    }
} else {
    Log-Message "Coral CLI is not currently registered on the Windows PATH." "WARN"
    Log-Message "All CSV/JSONL datasets are generated locally. Coral is ready to mount."
}

Log-Message "========================================================"
Log-Message "PIPELINE COMPLETED SUCCESSFULLY!"
Log-Message "========================================================"
