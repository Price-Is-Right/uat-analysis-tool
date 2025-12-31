#!/usr/bin/env python3
"""
Azure DevOps Integration Module

This module provides comprehensive integration with Azure DevOps REST APIs for work item
management, specifically designed for the Enhanced Issue Tracker System.

⚠️ PRODUCTION DEPLOYMENT NOTE:
   Currently using Azure CLI authentication for development.
   Before production deployment, switch to Service Principal authentication:
   - Create Azure AD App Registration
   - Grant appropriate Azure DevOps permissions
   - Use client_id/client_secret instead of CLI credentials
   - Update AzureDevOpsConfig to use Service Principal

Key Features:
- Work item creation with custom fields and formatting
- Authentication using Azure CLI credentials (dev) / Service Principal (prod)
- Error handling and validation for API operations
- Support for custom work item types (Action items)
- Project and organization management

Classes:
    AzureDevOpsConfig: Configuration container for API settings and credentials
    AzureDevOpsClient: Main client for Azure DevOps REST API operations

Author: Enhanced Issue Tracker System
Version: 2.1
Last Updated: December 2025
"""

import requests
import json
import os
from typing import Dict, List, Optional
from urllib.parse import quote
from azure.identity import AzureCliCredential, DefaultAzureCredential


class AzureDevOpsConfig:
    """
    Configuration container for Azure DevOps integration settings.
    
    Centralizes all configuration parameters for Azure DevOps API access,
    including authentication, project details, and API versioning.
    
    Attributes:
        ORGANIZATION (str): Azure DevOps organization name
        PROJECT (str): Target project name for work item creation
        BASE_URL (str): Complete base URL for API endpoints
        API_VERSION (str): Azure DevOps REST API version
        WORK_ITEM_TYPE (str): Default work item type for new items
        PAT (str): Personal Access Token for authentication
    """
    ORGANIZATION = "unifiedactiontrackertest"
    PROJECT = "Unified Action Tracker Test"
    BASE_URL = f"https://dev.azure.com/{ORGANIZATION}"
    API_VERSION = "7.0"
    WORK_ITEM_TYPE = "Action"  # Custom work item type
    
    # Azure DevOps scope for authentication
    ADO_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"  # Azure DevOps scope
    
    @staticmethod
    def get_credential():
        """
        Get Azure credential for authentication.
        
        Development: Uses Azure CLI credential (requires 'az login')
        Production: TODO - Switch to Service Principal with client_id/client_secret
        
        Returns:
            Azure credential object
        """
        try:
            # Try Azure CLI credential first (development)
            credential = AzureCliCredential()
            # Test the credential
            credential.get_token(AzureDevOpsConfig.ADO_SCOPE)
            return credential
        except Exception as e:
            # Fallback to default credential chain (includes managed identity for production)
            print(f"⚠️  Azure CLI credential failed: {e}")
            print("📝 Make sure you're logged in: az login")
            return DefaultAzureCredential()


class AzureDevOpsClient:
    """
    Client for Azure DevOps REST API operations.
    
    Uses Azure CLI authentication for development. For production deployment,
    update to use Service Principal authentication.
    
    Provides a comprehensive interface for interacting with Azure DevOps work items,
    including creation, testing connectivity, and error handling. Designed specifically
    for the Enhanced Issue Tracker System's workflow requirements.
    
    Attributes:
        config (AzureDevOpsConfig): Configuration object with API settings
        headers (Dict[str, str]): HTTP headers for API authentication
    """
    
    def __init__(self):
        """
        Initialize the Azure DevOps client with configuration and authentication.
        
        Sets up the client with proper authentication headers and configuration
        from the AzureDevOpsConfig class.
        """
        self.config = AzureDevOpsConfig()
        self.credential = self.config.get_credential()
        self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Generate authentication headers for Azure DevOps API calls.
        
        Uses Azure credential (CLI or Service Principal) to obtain an access token
        for Azure DevOps REST API authentication.
        
        Returns:
            Dict[str, str]: HTTP headers including Authorization, Content-Type, and Accept
        """
        try:
            # Get access token from credential
            token = self.credential.get_token(self.config.ADO_SCOPE)
            
            return {
                'Content-Type': 'application/json-patch+json',
                'Authorization': f'Bearer {token.token}',
                'Accept': 'application/json'
            }
        except Exception as e:
            print(f"❌ Failed to get Azure DevOps token: {e}")
            print("📝 Run 'az login' to authenticate with Azure CLI")
            raise
    
    def test_connection(self) -> Dict:
        """
        Test the connection to Azure DevOps and validate authentication.
        
        Performs a test API call to verify that the client can successfully
        connect to Azure DevOps using the configured credentials and organization.
        
        Returns:
            Dict: Test results including:
                - success: Boolean indicating if connection was successful
                - status_code: HTTP status code from the test request
                - message: Descriptive message about the test result
                - organization: Organization name if successful
                - project: Project name if successful
        """
        try:
            # Test with projects endpoint
            url = f"{self.config.BASE_URL}/_apis/projects?api-version={self.config.API_VERSION}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                projects_data = response.json()
                return {
                    'success': True,
                    'message': f"Successfully connected to ADO. Found {len(projects_data.get('value', []))} projects",
                    'projects': projects_data.get('value', [])
                }
            else:
                return {
                    'success': False,
                    'error': f"Connection failed: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Connection error: {str(e)}"
            }
    
    def create_work_item(self, title: str, description: str = "", **kwargs) -> Dict:
        """Create a work item in Azure DevOps
        
        Args:
            title: Work item title (required)
            description: Work item description
            **kwargs: Additional fields like area_path, iteration_path, etc.
        
        Returns:
            Dict with success status and work item details or error
        """
        try:
            # Build the JSON patch operations for work item creation
            operations = []
            
            # Title (required field)
            operations.append({
                "op": "add",
                "path": "/fields/System.Title",
                "value": title
            })
            
            # Description (if provided)
            if description:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": description
                })
            
            # Additional fields from kwargs
            field_mappings = {
                'area_path': 'System.AreaPath',
                'iteration_path': 'System.IterationPath',
                'assigned_to': 'System.AssignedTo',
                'customer_scenario': 'Microsoft.VSTS.Common.AcceptanceCriteria',
                'priority': 'Microsoft.VSTS.Common.Priority',
                'tags': 'System.Tags'
            }
            
            for key, value in kwargs.items():
                if key in field_mappings and value:
                    operations.append({
                        "op": "add",
                        "path": f"/fields/{field_mappings[key]}",
                        "value": value
                    })
            
            # Add source tag to identify work items created by this app
            operations.append({
                "op": "add",
                "path": "/fields/System.Tags",
                "value": "IssueTracker;AutoCreated"
            })
            
            # API endpoint for creating work items
            url = f"{self.config.BASE_URL}/{quote(self.config.PROJECT)}/_apis/wit/workitems/${self.config.WORK_ITEM_TYPE}?api-version={self.config.API_VERSION}"
            
            # Make the API call
            response = requests.post(url, json=operations, headers=self.headers)
            
            if response.status_code == 200:
                work_item = response.json()
                return {
                    'success': True,
                    'work_item_id': work_item['id'],
                    'url': work_item['_links']['html']['href'],
                    'title': work_item['fields']['System.Title'],
                    'state': work_item['fields']['System.State'],
                    'work_item': work_item
                }
            else:
                return {
                    'success': False,
                    'error': f"ADO API Error: {response.status_code} - {response.text}",
                    'url': url
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}"
            }
    
    def create_work_item_from_issue(self, issue_data: Dict) -> Dict:
        """Create a work item from issue tracker data with custom fields
        
        Args:
            issue_data: Dictionary containing issue information with keys:
                - title: Issue title
                - description: Issue description  
                - impact: Customer impact/scenario
                - opportunity_id: Opportunity ID for tracking
                - milestone_id: Milestone ID for tracking
                - area_path: Area path (optional)
                - iteration_path: Iteration path (optional)
                - priority: Priority level (optional)
        
        Returns:
            Dict with success status and work item details or error
        """
        try:
            # Extract data from issue
            title = issue_data.get('title', 'Untitled Issue')
            description = issue_data.get('description', '')
            impact = issue_data.get('impact', '')
            opportunity_id = issue_data.get('opportunity_id', '')
            milestone_id = issue_data.get('milestone_id', '')
            
            # Build a comprehensive description including impact
            full_description = description
            if impact:
                full_description += f"\n\n**Customer Impact:**\n{impact}"
            
            # Build the JSON patch operations for work item creation with custom fields
            operations = []
            
            # Standard fields
            operations.append({
                "op": "add",
                "path": "/fields/System.Title",
                "value": title
            })
            
            operations.append({
                "op": "add",
                "path": "/fields/System.Description",
                "value": full_description
            })
            
            # Assigned To field - set to "ACR Accelerate Blockers Help"
            operations.append({
                "op": "add",
                "path": "/fields/System.AssignedTo",
                "value": "ACR Accelerate Blockers Help"
            })
            
            # Custom field: CustomerScenarioandDesiredOutcome (set to Impact statement)
            if impact:
                operations.append({
                    "op": "add",
                    "path": "/fields/custom.CustomerScenarioandDesiredOutcome",
                    "value": impact
                })
            
            # Custom field: AssigntoCorp (set to True)
            operations.append({
                "op": "add",
                "path": "/fields/custom.AssigntoCorp",
                "value": True
            })
            
            # Custom field: Opportunity_ID (set to submitted Opportunity Number)
            if opportunity_id:
                operations.append({
                    "op": "add",
                    "path": "/fields/custom.Opportunity_ID",
                    "value": opportunity_id
                })
            
            # Custom field: MilestoneID (set to submitted Milestone ID)
            if milestone_id:
                operations.append({
                    "op": "add",
                    "path": "/fields/custom.MilestoneID",
                    "value": milestone_id
                })
            
            # Custom field: StatusUpdate (set to 'WizardAuto')
            operations.append({
                "op": "add",
                "path": "/fields/custom.StatusUpdate",
                "value": "WizardAuto"
            })
            
            # Add source tag to identify work items created by this app
            operations.append({
                "op": "add",
                "path": "/fields/System.Tags",
                "value": "IssueTracker;AutoCreated;WizardGenerated"
            })
            
            # Add optional fields if provided
            if issue_data.get('area_path'):
                operations.append({
                    "op": "add",
                    "path": "/fields/System.AreaPath",
                    "value": issue_data['area_path']
                })
            
            if issue_data.get('iteration_path'):
                operations.append({
                    "op": "add",
                    "path": "/fields/System.IterationPath",
                    "value": issue_data['iteration_path']
                })
            
            if issue_data.get('priority'):
                operations.append({
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Priority",
                    "value": issue_data['priority']
                })
            
            # API endpoint for creating work items
            url = f"{self.config.BASE_URL}/{quote(self.config.PROJECT)}/_apis/wit/workitems/${self.config.WORK_ITEM_TYPE}?api-version={self.config.API_VERSION}"
            
            # Make the API call
            response = requests.post(url, json=operations, headers=self.headers)
            
            if response.status_code == 200:
                work_item = response.json()
                return {
                    'success': True,
                    'work_item_id': work_item['id'],
                    'url': work_item['_links']['html']['href'],
                    'title': work_item['fields']['System.Title'],
                    'state': work_item['fields']['System.State'],
                    'assigned_to': work_item['fields'].get('System.AssignedTo', {}).get('displayName', 'ACR Accelerate Blockers Help'),
                    'opportunity_id': opportunity_id,
                    'milestone_id': milestone_id,
                    'work_item': work_item,
                    'source': 'IssueTracker',
                    'original_issue': issue_data
                }
            else:
                return {
                    'success': False,
                    'error': f"ADO API Error: {response.status_code} - {response.text}",
                    'url': url
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create work item from issue data: {str(e)}"
            }
    
    def get_work_item_fields(self) -> Dict:
        try:
            url = f"{self.config.BASE_URL}/{quote(self.config.PROJECT)}/_apis/wit/workitemtypes/{self.config.WORK_ITEM_TYPE}?api-version={self.config.API_VERSION}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                work_item_type = response.json()
                return {
                    'success': True,
                    'fields': work_item_type.get('fields', []),
                    'work_item_type': work_item_type
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to get work item type: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}"
            }


def test_ado_integration():
    """Test function to verify ADO integration works"""
    print("Testing Azure DevOps Integration...")
    
    # Initialize client
    ado_client = AzureDevOpsClient()
    
    # Test connection
    print("\n1. Testing connection...")
    connection_result = ado_client.test_connection()
    if connection_result['success']:
        print(f"✓ {connection_result['message']}")
    else:
        print(f"✗ {connection_result['error']}")
        return
    
    # Test work item creation
    print("\n2. Testing work item creation...")
    test_work_item = ado_client.create_work_item(
        title="Test Work Item from Issue Tracker",
        description="This is a test work item created by the Issue Tracker application to verify ADO integration.",
        customer_scenario="Testing the integration between Issue Tracker and Azure DevOps"
    )
    
    if test_work_item['success']:
        print(f"✓ Work item created successfully!")
        print(f"  - ID: {test_work_item['work_item_id']}")
        print(f"  - Title: {test_work_item['title']}")
        print(f"  - State: {test_work_item['state']}")
        print(f"  - URL: {test_work_item['url']}")
    else:
        print(f"✗ Failed to create work item: {test_work_item['error']}")
    
    # Test getting work item fields
    print("\n3. Testing work item field retrieval...")
    fields_result = ado_client.get_work_item_fields()
    if fields_result['success']:
        print(f"✓ Retrieved work item type information")
        print(f"  - Available fields: {len(fields_result['fields'])}")
    else:
        print(f"✗ Failed to get work item fields: {fields_result['error']}")


if __name__ == "__main__":
    test_ado_integration()
