# Quick Start Guide - Enhanced Issue Tracker System

Get up and running with the Enhanced Issue Tracker System in under 5 minutes!

## 🚀 Installation (2 minutes)

### Prerequisites Check
```bash
python --version    # Ensure Python 3.8+
pip --version      # Ensure pip is available
```

### Install Dependencies
```bash
cd c:\Projects\Hack
pip install flask requests python-dotenv
```

## ▶️ Start the Application (30 seconds)

### Method 1: Standard Launch
```bash
python app.py
```

### Method 2: Debug Mode
```bash
python app.py --debug
```

### Expected Output
```
* Running on http://127.0.0.1:5001
* Debug mode: on
* Restarting with stat
* Debugger is active!
```

## 🌐 Access the System (15 seconds)

1. **Open your browser**
2. **Navigate to**: http://127.0.0.1:5001
3. **You'll see the Quick ICA Analysis form**

## 🎯 First Issue Submission (2 minutes)

### Quick ICA Form
- Enter a descriptive title (max 125 characters)
- Real-time character counter shows remaining characters
- Example: "Cannot access company email on mobile device"

### Step 2: Detailed Description
- Provide comprehensive issue details
- Include what you're trying to do, expected vs actual results
- Example: "I'm trying to set up my work email on my iPhone but getting 'Cannot Get Mail' error"

### Step 3: Impact Statement
- Describe business/user impact if not resolved
- Example: "Unable to respond to urgent emails while traveling, affecting client relationships"

### Step 4: MSX Information
- **Opportunity ID**: Enter relevant opportunity ID (or "N/A")
- **Milestone ID**: Enter milestone ID (or "N/A")

### Step 5: Review & Submit
- Review all entered information
- Edit any section by clicking "Edit" buttons
- Click "Submit Issue" to proceed

## 🔍 Quality Analysis Process (1 minute)

### Automatic Quality Check
- System analyzes input completeness (0-100%)
- Checks for required keywords and content depth
- Shows progress bar with score

### First Attempt (Score < 80%)
- **Forced Improvement**: Must add more details
- **Specific Guidance**: Shows what information is missing
- **Re-analysis**: Updated score after improvements

### Second Attempt (Any Score)
- **User Choice**: Improve further or proceed
- **Warning Dialog**: Shows if proceeding with low quality
- **Confirmation**: Must confirm to continue with warnings

## 🔎 Enhanced Matching Results (30 seconds)

### Search Process
- **AI-Powered Query Generation**: Azure OpenAI creates intelligent 3-5 word search queries
- **Microsoft Learn Documentation**: Smart search with optimized queries
- **Retirement Information**: Multi-source checking (local JSON + Microsoft Learn + Azure Updates)
- **Similar Products**: Alternative Azure service suggestions
- **Regional Options**: Availability by region for specified services
- **Real-time Progress**: Animated progress bar through 5 search stages

### Retirement Information Display
- **Collapsible Sections**: Click to expand/collapse retirement details (collapsed by default)
- **Scrollable Lists**: Max 400px height prevents buttons from being pushed off-screen
- **Count Badges**: Shows number of relevant retirements found
- **Smart Filtering**: Word boundary matching ensures only relevant services shown
- **Online Search Fallback**: If local database empty, searches Microsoft Learn automatically

### Result Types
1. **Microsoft Learn Docs**: Official documentation links with relevance scores
2. **Similar Products**: Alternative Azure services with descriptions
3. **Regional Options**: Availability information for different Azure regions  
4. **Capacity Guidance**: Quota and limit information if relevant
5. **Retirement Info**: Service/feature retirement announcements with migration guidance

### Available Actions
- **Cancel**: Return to home (centered button with proper alignment)
- **Do Deep Search**: More comprehensive search (may take longer)
- **Continue and Create UAT**: Proceed to UAT creation after reviewing resources
- **Back to Summary**: Return to context summary page

## 🛠 Common Tasks

### View System Status
- Navigate to: http://127.0.0.1:5001/admin
- Check system health and configuration

### Test Search Function
- Navigate to: http://127.0.0.1:5001/api/search
- Test similarity matching with sample queries

### Clear Session Data
- Close browser completely
- Restart browser and navigate to system
- Session will auto-initialize

## 🔧 Quick Troubleshooting

### Application Won't Start
```bash
# Check if port 5001 is in use
netstat -an | findstr :5001

# Try different port
set FLASK_PORT=5002
python app.py
```

### "Cannot Get Mail" on Quality Analysis
```bash
# Check console for detailed error
# Usually indicates missing Azure DevOps configuration
# System works with local database only
```

### Session Errors
1. Clear browser cache
2. Close all browser windows  
3. Restart browser
4. Navigate to http://127.0.0.1:5001

### Azure DevOps 401 Errors
- Check PAT token validity in `enhanced_matching.py`
- Verify organization URLs are correct
- System continues with local database search

## 📱 Mobile Access

### Responsive Design
- Fully functional on mobile devices
- Touch-friendly interface
- All features available on phones/tablets

### Best Practices
- Use landscape mode for better text input
- Zoom in for better character counter visibility
- Save frequently (auto-save is enabled)

## 🎨 Accessibility Features

### Keyboard Navigation
- Tab through all form fields
- Enter to submit forms
- Escape to cancel operations

### Screen Reader Support
- Proper heading structure
- Form labels and descriptions
- Progress announcements

### High Contrast Mode
- Works with Windows High Contrast
- Custom accessible color schemes
- Proper focus indicators

## 📊 Performance Tips

### Optimal Usage
- **Single Browser Window**: Avoid multiple simultaneous sessions
- **Regular Submission**: Submit issues promptly for best results
- **Clear Sessions**: Close browser when finished

### Speed Optimization
- **Local Database**: Fastest search option
- **Detailed Input**: Better quality scores = faster processing
- **Specific Terms**: Use specific technical terms for better matches

## 🆘 Getting Help

### Built-in Help
- **Tooltips**: Hover over question marks for field help
- **Character Counters**: Real-time feedback on input limits
- **Progress Bars**: Visual feedback during processing

### Error Messages
- **Validation Errors**: Clear messages about what needs fixing
- **System Errors**: Detailed error information in console
- **Network Issues**: Automatic fallback to local database

### Console Logging
```bash
# View detailed logs while running
python app.py
# Watch console for:
# - Quality analysis scores
# - Azure DevOps API responses
# - Session management status
# - Error details and stack traces
```

## 🎯 Next Steps

### After First Success
1. **Explore Admin Panel**: Check system configuration
2. **Test Different Issue Types**: Try various problem descriptions
3. **Review Quality Scores**: Understand what makes high-quality submissions
4. **Check Documentation**: Read full README.md for advanced features

### Advanced Usage
- **Configure Azure DevOps**: Set up enterprise integration
- **Customize Quality Thresholds**: Adjust scoring parameters
- **Add Custom Issues**: Extend local database with organization-specific issues

---

## 📋 Quick Reference

| Task | URL | Time |
|------|-----|------|
| **Start New Issue** | http://127.0.0.1:5001 | 2-3 min |
| **Admin Panel** | http://127.0.0.1:5001/admin | 30 sec |
| **API Testing** | http://127.0.0.1:5001/api/search | 1 min |
| **System Restart** | `Ctrl+C` then `python app.py` | 30 sec |

---

**🎉 You're Ready!** The Enhanced Issue Tracker System is now running and ready for production use.

For detailed documentation, see [README.md](README.md)  
For project status, see [PROJECT_STATUS.md](PROJECT_STATUS.md)  
For restart procedures, see [RESTART_GUIDE.md](RESTART_GUIDE.md)
