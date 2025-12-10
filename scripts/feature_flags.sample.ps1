# Copy to feature_flags.ps1 and customize values, then: . .\feature_flags.ps1

# Core Google auth
$env:GEMINI_API_KEY = "<your_gemini_api_key>"
$env:GOOGLE_API_KEY = "<optional_google_api_key>"
$env:GOOGLE_CLOUD_PROJECT = "<your_gcp_project>"
$env:GOOGLE_APPLICATION_CREDENTIALS = "D:\path\to\service_account.json"

# Flow
$env:FLOW_ENABLED = "true"
$env:FLOW_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/flow"
$env:FLOW_WEBHOOK_SECRET = "<random_hex>"
$env:FLOW_DEFAULT_REGION = "us"

# Scene Describer
$env:SCENE_DESCRIBER_ENABLED = "true"
$env:SCENE_DESCRIBER_MODEL = "gemini-3.0-pro-vision"

# Prompt Coach
$env:PROMPT_COACH_ENABLED = "true"
$env:PROMPT_COACH_MODEL = "gemini-3.0-pro"

# AudioFX
$env:AUDIOFX_ENABLED = "false"  # flip to true when your access is granted
$env:AUDIOFX_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/audiofx"
$env:AUDIOFX_MODEL = "audiofx-1"

# Compliance
$env:SYNTHID_DASHBOARD_ENABLED = "false"
$env:SYNTHID_BIGQUERY_DATASET = "veogen_synthid.analytics"

# Workspace
$env:WORKSPACE_AUTOMATION_ENABLED = "false"
$env:WORKSPACE_AGENT_ID = "<agent_id_if_used>"

Write-Host "Feature flags set for current PowerShell session."

