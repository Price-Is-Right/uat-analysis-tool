# Admin Service

Dedicated administrative microservice for UAT Analysis Tool management and monitoring.

## Overview

- **Port:** 8004
- **Framework:** Flask
- **Purpose:** Administrative functions separate from user-facing application

## Features

### Current (v1.0)
- ✅ **Dashboard** - System statistics and overview
- ✅ **Evaluation Viewer** - Interactive viewer with search and navigation
- ✅ **Evaluation List** - Browse and filter all evaluations
- ✅ **Search** - Full-text search across UAT numbers, keywords, and phrases
- ✅ **Filtering** - Filter by status (approved/rejected/all)
- ✅ **Navigation** - Previous/Next buttons to browse evaluations
- ✅ **Export** - Download evaluations as JSON
- ✅ **API Endpoints** - RESTful API for programmatic access

### Planned (Future)
- 🔲 **Authentication** - Login/logout with role-based access
- 🔲 **User Management** - Add/edit/remove users
- 🔲 **System Configuration** - Manage application settings
- 🔲 **Audit Logs** - View system activity logs
- 🔲 **Analytics** - Advanced reporting and insights
- 🔲 **Bulk Operations** - Batch update/delete evaluations

## Quick Start

### Start Admin Service Only
```powershell
.\start_admin_service.ps1
```

### Start All Services
```powershell
.\start_services.ps1 -All
```

### Start Admin + Main App
```powershell
.\start_services.ps1 -MainAppOnly
# In another window:
.\start_services.ps1 -AdminOnly
```

## URLs

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://localhost:8004/ | Admin home with statistics |
| Evaluations List | http://localhost:8004/evaluations | Browse all evaluations |
| Interactive Viewer | http://localhost:8004/evaluations/viewer | Search and view details |
| API Search | http://localhost:8004/api/evaluations/search | Search API endpoint |
| API Export | http://localhost:8004/api/evaluations/export | Export as JSON |

## Usage Examples

### Search for UAT Number
1. Navigate to http://localhost:8004/evaluations/viewer
2. Enter UAT number in search box (e.g., "UAT-12345")
3. Use Previous/Next buttons to navigate results

### Filter by Status
1. Go to http://localhost:8004/evaluations
2. Select status filter: All, Approved, or Rejected
3. Click "Filter" button

### View Evaluation Details
- From list: Click "View" button
- From viewer: Use Previous/Next navigation
- Direct link: http://localhost:8004/evaluations/viewer?id={eval_id}

### Export Data
Visit: http://localhost:8004/api/evaluations/export

Add filters:
```
http://localhost:8004/api/evaluations/export?status=approved
http://localhost:8004/api/evaluations/export?search=UAT-12345
```

## API Endpoints

### Search Evaluations
```http
GET /api/evaluations/search?q={query}&status={status}
```

**Parameters:**
- `q` - Search query (UAT numbers, keywords, phrases)
- `status` - Filter by status: `all`, `approved`, `rejected`

**Response:**
```json
{
  "results": [
    {
      "evaluation_id": "eval_123",
      "timestamp": "2026-01-20T14:30:00",
      "user_approved": true,
      "category": "Teams",
      "uat_numbers": ["UAT-12345", "UAT-67890"],
      "title": "Issue with..."
    }
  ],
  "count": 1
}
```

### Export Evaluations
```http
GET /api/evaluations/export?status={status}&search={query}
```

**Response:**
```json
{
  "export_date": "2026-01-20T14:30:00",
  "count": 100,
  "evaluations": [...]
}
```

## Architecture

```
admin_service.py                    # Main Flask application
├── Routes
│   ├── /                          # Dashboard
│   ├── /evaluations               # List view
│   ├── /evaluations/viewer        # Interactive viewer
│   ├── /evaluations/<id>          # Single evaluation detail
│   └── /api/*                     # API endpoints
├── Templates (templates/admin/)
│   ├── base.html                  # Admin layout
│   ├── dashboard.html             # Statistics dashboard
│   ├── evaluations_list.html      # List view
│   └── evaluation_viewer.html     # Interactive viewer
└── Services
    ├── keyvault_config.py         # Azure Key Vault integration
    └── blob_storage_helper.py     # Blob storage for evaluations
```

## Security

### Current (Development)
- No authentication required
- Open access on localhost:8004

### Future (Production)
- Session-based authentication
- Role-based access control (RBAC)
- Azure AD integration
- API key authentication for API endpoints
- Audit logging of all admin actions

## Data Sources

The admin service reads evaluation data from:
- **Azure Blob Storage**: `gcs-data` container
- **File**: `context_evaluations.json`

Configuration loaded from:
- **Azure Key Vault**: `kv-gcs-dev-gg4a6y`
- **Environment**: `.env.azure` (development fallback)

## Troubleshooting

### Service won't start
```powershell
# Check if port 8004 is in use
netstat -ano | findstr :8004

# Kill process if needed
taskkill /PID <process_id> /F
```

### Can't connect to Key Vault
- Verify Azure CLI is logged in: `az account show`
- Check Key Vault firewall: Your IP must be allowed
- Verify managed identity permissions (production)

### No evaluations shown
- Check blob storage connectivity
- Verify `context_evaluations.json` exists in `gcs-data` container
- Check application logs for errors

## Development

### Add New Route
```python
@app.route('/admin/new-feature')
def new_feature():
    return render_template('new_feature.html')
```

### Add New Template
Create in `templates/admin/`:
```html
{% extends "base.html" %}
{% block title %}New Feature{% endblock %}
{% block content %}
<!-- Your content -->
{% endblock %}
```

### Test Changes
```powershell
# Restart service
Ctrl+C  # Stop current service
.\start_admin_service.ps1
```

## Deployment

### Local Development
```powershell
python admin_service.py
```

### Azure Container Apps (Future)
```bash
# Build container
docker build -t admin-service .

# Push to registry
az acr build --registry acrgcsdevgg4a6y \
  --image admin-service:latest .

# Deploy
az containerapp create \
  --name admin-service \
  --resource-group rg-gcs-dev \
  --image acrgcsdevgg4a6y.azurecr.io/admin-service:latest \
  --target-port 8004 \
  --ingress external \
  --environment-variables AZURE_CLIENT_ID=7846e03e-9279-4057-bdcd-4a2f7f8ebe85
```

## Support

For questions or issues:
1. Check troubleshooting section above
2. Review application logs
3. Check Azure Key Vault and Blob Storage connectivity
4. Contact development team
