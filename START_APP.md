# Quick Start Guide

## Starting the Application

### Option 1: Using PowerShell Commands

```powershell
# Set Azure OpenAI environment variables (replace with your actual values)
$env:AZURE_OPENAI_ENDPOINT='YOUR_AZURE_OPENAI_ENDPOINT'
$env:AZURE_OPENAI_API_KEY='YOUR_AZURE_OPENAI_API_KEY'
$env:AZURE_OPENAI_DEPLOYMENT_NAME='YOUR_DEPLOYMENT_NAME'
$env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT='YOUR_EMBEDDING_DEPLOYMENT'

# Start the Flask application
python app.py
```

### Option 2: Using the PowerShell Script

```powershell
.\start_app.ps1
```

### Accessing the Application

Once started, navigate to: **http://127.0.0.1:5002**

The console will display:
```
================================================================================
Issue Tracker System starting...
================================================================================

Navigate to http://127.0.0.1:5002 to access the application

[DEBUG] Starting Flask with app.run()...
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5002
```

## Stopping the Application

Press `CTRL+C` in the terminal where the app is running.

## Environment Variables (Required)

| Variable | Example Value | Purpose |
|----------|---------------|---------|
| `AZURE_OPENAI_ENDPOINT` | `https://YOUR-RESOURCE.openai.azure.com` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | `YOUR_API_KEY_HERE` | API authentication key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-4o-standard` | GPT-4o deployment for classification |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | `text-embedding-3-large` | Embedding model for similarity search |

## Making Environment Variables Persistent

### Option A: Create .env file (Recommended)

Create a `.env` file in the project root:

```bash
AZURE_OPENAI_ENDPOINT=YOUR_AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_API_KEY
AZURE_OPENAI_DEPLOYMENT_NAME=YOUR_DEPLOYMENT_NAME
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=YOUR_EMBEDDING_DEPLOYMENT
```

Then install python-dotenv: `pip install python-dotenv`

### Option B: System Environment Variables

Set permanently in Windows:
```powershell
[System.Environment]::SetEnvironmentVariable('AZURE_OPENAI_ENDPOINT', 'YOUR_ENDPOINT_HERE', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_OPENAI_API_KEY', 'YOUR_API_KEY_HERE', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_OPENAI_DEPLOYMENT_NAME', 'YOUR_DEPLOYMENT_NAME', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'YOUR_EMBEDDING_DEPLOYMENT', 'User')
```

**Note:** Restart your terminal after setting system variables.

### Option C: PowerShell Profile

Add to your PowerShell profile (`$PROFILE`):
```powershell
$env:AZURE_OPENAI_ENDPOINT='YOUR_ENDPOINT_HERE'
$env:AZURE_OPENAI_API_KEY='YOUR_API_KEY_HERE'
$env:AZURE_OPENAI_DEPLOYMENT_NAME='YOUR_DEPLOYMENT_NAME'
$env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT='YOUR_EMBEDDING_DEPLOYMENT'
```

## Troubleshooting

### "AI services are not configured" error
- Check that all 4 environment variables are set
- Restart the application after setting variables
- Verify the endpoint and API key are correct

### Port 5002 already in use
```powershell
# Kill any existing Python processes
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
```

### Python syntax errors on startup
- Ensure you're using Python 3.10 or higher
- Check that all required packages are installed: `pip install -r requirements.txt`

### Cache issues
```powershell
# Clear AI cache
Remove-Item -Recurse -Force cache/ai_cache/*
```

## Verification

Once the app starts, you should see in the logs:
```
[HybridAnalyzer] AI services initialized successfully
[HybridAnalyzer] Mode: AI-powered with pattern features
```

Submit a test issue and check for:
- ✅ Green "AI-Powered Analysis Complete!" alert
- ✅ 95%+ confidence score
- ✅ "Source: llm" in the analysis
- ✅ Detailed reasoning text displayed

## Need Help?

See [PROJECT_STATUS_2026-01-02.md](PROJECT_STATUS_2026-01-02.md) for full system documentation and architecture details.
