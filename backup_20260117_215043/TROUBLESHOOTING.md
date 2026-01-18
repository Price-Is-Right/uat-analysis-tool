# Troubleshooting Guide

## Flask Server Exits Immediately in VS Code Terminals

**Issue:** Flask server starts successfully, authenticates, and then immediately exits with "Flask exited normally" when run from VS Code integrated terminals.

**Symptoms:**
- Flask shows "Running on http://127.0.0.1:5002" 
- Immediately followed by "[DEBUG] Flask exited normally"
- Process exits with code 1
- Same issue occurs with minimal test Flask apps
- Works fine in standalone PowerShell windows

**Root Cause:** VS Code's integrated terminal process management interferes with long-running Flask server processes. This is a known compatibility issue between VS Code terminals and Flask's blocking server process.

**Workaround (Required for Testing):**

### Starting Services for Testing:

**PowerShell Window 1 (Flask API):**
```powershell
cd C:\Projects\Hack
.\start_app.ps1
```

**PowerShell Window 2 (Teams Bot):**
```powershell
cd C:\Projects\Hack-TeamsBot
python bot.py
```

**Important:** Use standalone PowerShell windows (not VS Code terminals) for both services when testing bot workflows.

### What Works:
✅ Standalone PowerShell windows  
✅ Windows Terminal  
✅ CMD windows  
✅ Production deployment (WSGI servers like Gunicorn/Waitress)

### What Doesn't Work:
❌ VS Code integrated terminals  
❌ VS Code Python extension "Run Python File"

## Date Discovered
January 14, 2026

## Related Issues
- Flask runs but immediately exits after showing "Press CTRL+C to quit"
- No actual CTRL+C signal is sent
- app.run() returns immediately instead of blocking
- Issue persists even with `use_reloader=False` and `debug=False`

## Tested Solutions That Didn't Work
- Clearing Python cache (`__pycache__`)
- Reinstalling pandas/sklearn/numpy
- Different Flask configurations
- Using different port numbers
- Setting various Flask debug flags

## Why This Happens
VS Code's terminal multiplexer (which allows multiple terminals in tabs) can interfere with processes that:
1. Block indefinitely (like web servers)
2. Wait for network connections
3. Have long-running event loops

The terminal may send signals or close file descriptors that cause Flask to think it should shut down.

## Future Testing Protocol
1. **Always test bot workflows using standalone PowerShell windows**
2. For quick API tests, VS Code terminals may work
3. For full end-to-end testing, use external terminals
4. Document any similar issues with other long-running services
