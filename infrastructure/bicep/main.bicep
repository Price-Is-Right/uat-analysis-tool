// GCS Infrastructure - Main Deployment
// Creates all Azure resources for GCS development environment

targetScope = 'subscription'

@description('Location for all resources')
param location string = 'northcentralus'

@description('Environment name')
param environment string = 'dev'

@description('Project name')
param projectName string = 'gcs'

@description('Owner email')
param owner string = 'bprice@microsoft.com'

// Resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-${projectName}-${environment}'
  location: location
  tags: {
    Environment: environment
    Project: projectName
    Owner: owner
    Purpose: 'AI-Powered UAT Management System'
  }
}

// Deploy storage, monitoring, and container infrastructure
module infrastructure 'resources.bicep' = {
  scope: rg
  name: 'gcs-infrastructure-deployment'
  params: {
    location: location
    environment: environment
    projectName: projectName
    owner: owner
  }
}

// Outputs
output resourceGroupName string = rg.name
output storageAccountName string = infrastructure.outputs.storageAccountName
output appInsightsName string = infrastructure.outputs.appInsightsName
output logAnalyticsName string = infrastructure.outputs.logAnalyticsName
output containerRegistryName string = infrastructure.outputs.containerRegistryName
output keyVaultName string = infrastructure.outputs.keyVaultName
