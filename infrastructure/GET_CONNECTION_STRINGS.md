# Get Connection Strings from Azure Portal

Since you have the Azure Portal open with the deployed resources, here's how to manually collect the connection strings we need:

## 1. Storage Account (stgcsdevgg4a6y)

1. Click on **stgcsdevgg4a6y**
2. In the left menu, click **Access keys**
3. Under **key1**, click **Show** next to **Connection string**
4. Click **Copy to clipboard**
5. Save as: `AZURE_STORAGE_CONNECTION_STRING`

Also note the storage account name: `stgcsdevgg4a6y`

---

## 2. Application Insights (appi-gcs-dev)

1. Click on **appi-gcs-dev**
2. In the **Overview** or **Properties** section, you'll see:
   - **Instrumentation Key** - Copy this
   - **Connection String** - Copy this
3. Save as:
   - `AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY`
   - `AZURE_APP_INSIGHTS_CONNECTION_STRING`

---

## 3. Container Registry (acrgcsdevgg4a6y)

1. Click on **acrgcsdevgg4a6y**
2. In the left menu, click **Access keys**
3. Toggle **Admin user** to **Enabled**
4. Copy these values:
   - **Login server**: acrgcsdevgg4a6y.azurecr.io
   - **Username**: acrgcsdevgg4a6y
   - **password**: (click show and copy)
5. Save as:
   - `AZURE_CONTAINER_REGISTRY_SERVER=acrgcsdevgg4a6y.azurecr.io`
   - `AZURE_CONTAINER_REGISTRY_USERNAME=acrgcsdevgg4a6y`
   - `AZURE_CONTAINER_REGISTRY_PASSWORD=<the-password>`

---

## 4. Key Vault (kv-gcs-dev-gg4a6y)

1. Click on **kv-gcs-dev-gg4a6y**
2. Note the **Vault URI** from the overview (something like: https://kv-gcs-dev-gg4a6y.vault.azure.net/)
3. Save as:
   - `AZURE_KEY_VAULT_NAME=kv-gcs-dev-gg4a6y`
   - `AZURE_KEY_VAULT_URI=https://kv-gcs-dev-gg4a6y.vault.azure.net/`

---

## 5. Log Analytics (log-gcs-dev)

1. Click on **log-gcs-dev**
2. In the left menu, click **Agents**
3. Copy the **Workspace ID**
4. Save as:
   - `AZURE_LOG_ANALYTICS_WORKSPACE_ID=<workspace-id>`

---

## 6. Azure OpenAI (Existing Resource)

You already have this resource: **OpenAI-bp-NorthCentral**

1. Search for "OpenAI" in the top search bar
2. Click on **OpenAI-bp-NorthCentral**
3. In the left menu, click **Keys and Endpoint**
4. Copy:
   - **Endpoint**: https://OpenAI-bp-NorthCentral.openai.azure.com/
   - **KEY 1**: (click Show and copy)
5. Save as:
   - `AZURE_OPENAI_ENDPOINT=https://OpenAI-bp-NorthCentral.openai.azure.com/`
   - `AZURE_OPENAI_API_KEY=<your-key>`

---

## Create .env.azure File

Once you've collected all the values above, create a file called `.env.azure` in the project root with this content:

```bash
# GCS Azure Infrastructure Connection Strings
# Generated: 2026-01-17
# Resource Group: rg-gcs-dev

# Storage Account
AZURE_STORAGE_ACCOUNT_NAME=stgcsdevgg4a6y
AZURE_STORAGE_CONNECTION_STRING=<paste-from-portal>

# Application Insights
AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY=<paste-from-portal>
AZURE_APP_INSIGHTS_CONNECTION_STRING=<paste-from-portal>

# Container Registry
AZURE_CONTAINER_REGISTRY_NAME=acrgcsdevgg4a6y
AZURE_CONTAINER_REGISTRY_SERVER=acrgcsdevgg4a6y.azurecr.io
AZURE_CONTAINER_REGISTRY_USERNAME=acrgcsdevgg4a6y
AZURE_CONTAINER_REGISTRY_PASSWORD=<paste-from-portal>

# Key Vault
AZURE_KEY_VAULT_NAME=kv-gcs-dev-gg4a6y
AZURE_KEY_VAULT_URI=https://kv-gcs-dev-gg4a6y.vault.azure.net/

# Log Analytics
AZURE_LOG_ANALYTICS_WORKSPACE_ID=<paste-from-portal>

# Container Apps Environment
AZURE_CONTAINER_APPS_ENVIRONMENT=cae-gcs-dev

# Azure OpenAI (Existing Resource)
AZURE_OPENAI_RESOURCE_NAME=OpenAI-bp-NorthCentral
AZURE_OPENAI_ENDPOINT=https://OpenAI-bp-NorthCentral.openai.azure.com/
AZURE_OPENAI_API_KEY=<paste-from-portal>
```

---

## ⚠️ IMPORTANT SECURITY NOTES

1. **DO NOT commit `.env.azure` to git** - it contains secrets
2. Add to `.gitignore` if not already there
3. Store these values in Azure Key Vault for production use
4. Keep a secure backup of this file

---

## What's Next?

After creating the `.env.azure` file:

1. ✅ Phase 1: Infrastructure Setup - **COMPLETE!**
2. ⏭️ Phase 2: Data Migration - Migrate JSON files to Azure Blob Storage
3. ⏭️ Phase 3: API Gateway Development

---

**Need Help?** See [PROJECT_ROADMAP.md](../PROJECT_ROADMAP.md) for the full implementation plan.
