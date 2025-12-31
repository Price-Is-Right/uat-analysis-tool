# Authentication Setup

## Development Environment (Current)

The application currently uses **Azure CLI authentication** for Azure DevOps integration.

### Setup Steps:

1. **Install Azure CLI** (if not already installed):
   ```bash
   # Windows
   winget install -e --id Microsoft.AzureCLI
   
   # Or download from: https://aka.ms/installazurecliwindows
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```
   
3. **Verify Authentication**:
   ```bash
   az account show
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

The application will automatically use your Azure CLI credentials for:
- Creating UATs in Azure DevOps
- Searching existing UATs and features
- Accessing Azure DevOps REST APIs

## Production Deployment ⚠️

**IMPORTANT:** Before deploying to production, switch to **Service Principal authentication**.

### Why Service Principal?

- ✅ No dependency on `az login`
- ✅ Automated authentication without user interaction
- ✅ Better security with scoped permissions
- ✅ Proper for CI/CD pipelines and production servers
- ✅ Audit trail and compliance

### Production Setup Steps:

1. **Create Azure AD App Registration**:
   ```bash
   az ad app create --display-name "UAT-Analysis-Tool-Prod"
   ```

2. **Create Service Principal**:
   ```bash
   az ad sp create --id <app-id>
   ```

3. **Grant Azure DevOps Permissions**:
   - Go to Azure DevOps Organization Settings
   - Add Service Principal with appropriate permissions:
     - Work Items: Read & Write
     - Project: Read
     - Build: Read (if needed)

4. **Create Client Secret**:
   ```bash
   az ad app credential reset --id <app-id>
   ```
   Save the client secret securely!

5. **Update Code**:
   
   In `ado_integration.py` and `enhanced_matching.py`, update the credential method:
   
   ```python
   from azure.identity import ClientSecretCredential
   
   @staticmethod
   def get_credential():
       tenant_id = os.environ.get('AZURE_TENANT_ID')
       client_id = os.environ.get('AZURE_CLIENT_ID')
       client_secret = os.environ.get('AZURE_CLIENT_SECRET')
       
       return ClientSecretCredential(
           tenant_id=tenant_id,
           client_id=client_id,
           client_secret=client_secret
       )
   ```

6. **Set Environment Variables**:
   ```bash
   # Production environment
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_CLIENT_SECRET="your-client-secret"
   ```

### Azure App Service / Container Apps

If deploying to Azure, use **Managed Identity** instead of Service Principal:

1. Enable Managed Identity on your Azure resource
2. Grant Azure DevOps permissions to the Managed Identity
3. Update code to use `ManagedIdentityCredential`

## Troubleshooting

### "Azure CLI credential failed"

```bash
# Re-login to Azure CLI
az login

# Check your account
az account show

# List available subscriptions
az account list
```

### "Token refresh failed"

The app automatically refreshes tokens, but if issues persist:
- Log out and back in: `az logout && az login`
- Check Azure DevOps permissions for your account

### Production Issues

- Verify Service Principal has correct permissions in Azure DevOps
- Check environment variables are set correctly
- Validate tenant_id, client_id, and client_secret values
- Review Azure AD app registration settings

## Security Best Practices

✅ **Never commit credentials** to source control
✅ **Use Azure Key Vault** for production secrets
✅ **Rotate client secrets** regularly (every 90 days)
✅ **Use Managed Identity** when running on Azure
✅ **Apply least privilege** - only grant required permissions
✅ **Monitor access logs** in Azure AD and Azure DevOps
