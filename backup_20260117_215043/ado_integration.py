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
from typing import Dict, List, Optional, Any
from urllib.parse import quote
from azure.identity import AzureCliCredential, DefaultAzureCredential, InteractiveBrowserCredential


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
    
    # Cached credential to reuse across operations
    _cached_credential = None
    
    @staticmethod
    def get_credential():
        """
        Get Azure credential for authentication.
        
        Uses InteractiveBrowserCredential for proper permissions, with caching
        so authentication only happens once. Attempts to reuse credential from
        EnhancedMatchingConfig if already authenticated.
        
        Returns:
            Azure credential object
        """
        from azure.identity import AzureCliCredential, DefaultAzureCredential, InteractiveBrowserCredential
        
        # Try to reuse credential from EnhancedMatchingConfig (if already authenticated)
        try:
            from enhanced_matching import EnhancedMatchingConfig
            if EnhancedMatchingConfig._uat_credential is not None:
                print("🔐 Reusing cached credential from UAT search...")
                # Test it still works
                EnhancedMatchingConfig._uat_credential.get_token(AzureDevOpsConfig.ADO_SCOPE)
                print("✅ Authentication successful (cached)")
                AzureDevOpsConfig._cached_credential = EnhancedMatchingConfig._uat_credential
                return EnhancedMatchingConfig._uat_credential
        except Exception as reuse_error:
            print(f"⚠️  Could not reuse cached credential: {reuse_error}")
            pass  # Fall through to create new credential
        
        # Return our own cached credential if available
        if AzureDevOpsConfig._cached_credential is not None:
            return AzureDevOpsConfig._cached_credential
        
        try:
            # Use Interactive Browser first for proper permissions
            print("🔐 Using Interactive Browser credential (one-time login)...")
            credential = InteractiveBrowserCredential()
            token = credential.get_token(AzureDevOpsConfig.ADO_SCOPE)
            print("✅ Authentication successful (cached for session)")
            AzureDevOpsConfig._cached_credential = credential
            
            # CRITICAL: Also cache in EnhancedMatchingConfig so search doesn't prompt again
            from enhanced_matching import EnhancedMatchingConfig
            EnhancedMatchingConfig._uat_credential = credential
            EnhancedMatchingConfig._uat_token = token.token
            print("✅ Credential shared with search services")
            
            return credential
        except Exception as e:
            # Fallback to Azure CLI credential
            print(f"⚠️  Interactive Browser credential failed: {e}")
            
            # DO NOT fallback to Azure CLI - it doesn't work for work item creation
            # Azure CLI tokens cause "identity not materialized" errors
            print("❌ Interactive Browser authentication is REQUIRED for work item creation")
            print("💡 Please complete the browser login when prompted")
            raise Exception("Interactive Browser authentication required. Please log in through the browser.")
    
    @staticmethod
    def get_tft_credential():
        """
        Get Azure credential for Technical Feedback organization access.
        
        Uses InteractiveBrowserCredential for cross-org access which requires
        browser-based authentication to materialize identity.
        
        Returns:
            Azure credential object configured for browser authentication
        """
        # Use tenant ID for Microsoft
        tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
        return InteractiveBrowserCredential(tenant_id=tenant_id)


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
            # Always get fresh token from credential
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
            
            # State field - set to 'In Progress'
            operations.append({
                "op": "add",
                "path": "/fields/System.State",
                "value": "In Progress"
            })
            
            # Assigned To field - set to "ACR Accelerate Blockers Help"
            operations.append({
                "op": "add",
                "path": "/fields/System.AssignedTo",
                "value": "ACR Accelerate Blockers Help"
            })
            
            # Custom field: CustomerImpactData (set to Impact statement)
            if impact:
                operations.append({
                    "op": "add",
                    "path": "/fields/custom.CustomerImpactData",
                    "value": impact
                })
            
            # Custom field: CustomerScenarioandDesiredOutcome (formatted AI classification data)
            scenario_data_parts = []
            context_analysis = issue_data.get('context_analysis', {})
            
            print(f"\n[ADO DEBUG] issue_data keys: {list(issue_data.keys())}")
            print(f"[ADO DEBUG] context_analysis: {context_analysis}")
            print(f"[ADO DEBUG] selected_features: {issue_data.get('selected_features', [])}")
            print(f"[ADO DEBUG] selected_uats: {issue_data.get('selected_uats', [])}")
            
            # ⚠️ DEMO FIX (Jan 16 2026): Check BOTH nested and top-level fields
            # ORIGINAL ISSUE: Bot completion card showed blank URL, missing Category/Intent/Classification Reason
            # ROOT CAUSE: Bot sends top-level fields, web app sends nested context_analysis
            # FIX: Check both locations to support both calling patterns
            # This fixes missing classification data in created UAT work items
            category = None
            intent = None
            classification_reason = None
            
            # ⚠️ BUG FIX (Jan 16 2026): Handle None context_analysis properly
            # Previous code called .get() on None causing AttributeError
            if context_analysis and isinstance(context_analysis, dict):
                category = context_analysis.get('category')
                intent = context_analysis.get('intent')
                classification_reason = context_analysis.get('reasoning') or context_analysis.get('classification_reason')
            
            # Fall back to top-level fields if not in context_analysis
            if not category:
                category = issue_data.get('category', 'Unknown')
            if not intent:
                intent = issue_data.get('intent', 'Unknown')
            if not classification_reason:
                classification_reason = issue_data.get('classification_reason', '')
            
            # Add Category and Intent with proper formatting
            if category and category != 'Unknown':
                category_display = category.replace('_', ' ').title()
                scenario_data_parts.append(f"<strong>Category:</strong> {category_display}")
            
            if intent and intent != 'Unknown':
                intent_display = intent.replace('_', ' ').title()
                scenario_data_parts.append(f"<strong>Intent:</strong> {intent_display}")
            
            # Add classification reasoning
            if classification_reason:
                scenario_data_parts.append(f"<strong>Classification Reason:</strong> {classification_reason}")
            
            # Add selected features if present (with links)
            selected_features = issue_data.get('selected_features', [])
            if selected_features:
                feature_links = []
                for feature_id in selected_features:
                    # Create ADO link format: <a href="URL">ID</a>
                    feature_url = f"https://dev.azure.com/acrblockers/b47dfa86-3c5d-4fc9-8ab9-e4e10ec93dc4/_workitems/edit/{feature_id}"
                    feature_links.append(f'<a href="{feature_url}" target="_blank">#{feature_id}</a>')
                feature_html = ', '.join(feature_links)
                scenario_data_parts.append(f"<strong>Associated Features:</strong> {feature_html}")
            
            # Add selected related UATs if present (with links)
            selected_uats = issue_data.get('selected_uats', [])
            if selected_uats:
                uat_links = []
                for uat_id in selected_uats:
                    # Create ADO link format: <a href="URL">ID</a>
                    uat_url = f"https://dev.azure.com/unifiedactiontracker/Unified%20Action%20Tracker/_workitems/edit/{uat_id}"
                    uat_links.append(f'<a href="{uat_url}" target="_blank">#{uat_id}</a>')
                uat_html = ', '.join(uat_links)
                scenario_data_parts.append(f"<strong>Associated UATs:</strong> {uat_html}")
            
            if scenario_data_parts:
                # Join with <br><br> for proper HTML line breaks in Azure DevOps
                scenario_value = "<br><br>".join(scenario_data_parts)
                print(f"\n[ADO DEBUG] Writing to CustomerScenarioandDesiredOutcome:")
                print(f"[ADO DEBUG] Value: {scenario_value}")
                operations.append({
                    "op": "add",
                    "path": "/fields/custom.CustomerScenarioandDesiredOutcome",
                    "value": scenario_value
                })
            else:
                print("[ADO DEBUG] ⚠️ No scenario_data_parts to write!")
            
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
    
    def get_work_item(self, work_item_id: int) -> Dict:
        """
        Retrieve a work item by ID.
        
        Args:
            work_item_id: The ID of the work item to retrieve
            
        Returns:
            Dict with work item data or error information
        """
        try:
            url = f"{self.config.BASE_URL}/{quote(self.config.PROJECT)}/_apis/wit/workitems/{work_item_id}?api-version={self.config.API_VERSION}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f"Failed to retrieve work item: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'error': f"Failed to retrieve work item: {str(e)}"
            }
    
    def query_work_items(self, work_item_type: str = "Actions", state: Optional[str] = None, 
                        assigned_to: Optional[str] = None, max_results: int = 50) -> list:
        """
        Query work items with optional filters.
        
        Args:
            work_item_type: Type of work items to query (default: "Actions")
            state: Filter by state (optional)
            assigned_to: Filter by assignee (optional)
            max_results: Maximum number of results to return
            
        Returns:
            List of work items matching the criteria
        """
        try:
            # Build WIQL query
            query = f"SELECT [System.Id], [System.Title], [System.State], [System.CreatedDate], [System.AssignedTo] FROM WorkItems WHERE [System.TeamProject] = '{self.config.PROJECT}' AND [System.WorkItemType] = '{work_item_type}'"
            
            if state:
                query += f" AND [System.State] = '{state}'"
            if assigned_to:
                query += f" AND [System.AssignedTo] = '{assigned_to}'"
                
            query += f" ORDER BY [System.CreatedDate] DESC"
            
            # Execute WIQL query
            wiql_url = f"{self.config.BASE_URL}/{quote(self.config.PROJECT)}/_apis/wit/wiql?api-version={self.config.API_VERSION}"
            wiql_response = requests.post(wiql_url, json={"query": query}, headers=self.headers)
            
            if wiql_response.status_code != 200:
                return []
            
            wiql_result = wiql_response.json()
            work_item_ids = [item['id'] for item in wiql_result.get('workItems', [])][:max_results]
            
            if not work_item_ids:
                return []
            
            # Get full work item details
            ids_param = ",".join(str(id) for id in work_item_ids)
            details_url = f"{self.config.BASE_URL}/{quote(self.config.PROJECT)}/_apis/wit/workitems?ids={ids_param}&api-version={self.config.API_VERSION}"
            details_response = requests.get(details_url, headers=self.headers)
            
            if details_response.status_code == 200:
                return details_response.json().get('value', [])
            else:
                return []
                
        except Exception as e:
            print(f"Error querying work items: {e}")
            return []
    
    def update_work_item(self, work_item_id: int, updates: Dict[str, Any]) -> Dict:
        """
        Update a work item with the specified field changes.
        
        Args:
            work_item_id: The ID of the work item to update
            updates: Dictionary of field names to new values
            
        Returns:
            Dict with success status and updated work item details
        """
        try:
            # Build JSON Patch operations
            operations = []
            for field, value in updates.items():
                # Ensure field has proper path format
                if not field.startswith("/fields/"):
                    if not field.startswith("System.") and not field.startswith("Custom.") and not field.startswith("Microsoft."):
                        field = f"System.{field}"
                    field = f"/fields/{field}"
                else:
                    # Strip /fields/ prefix if present, we'll add it back
                    field = field.replace("/fields/", "")
                    if not field.startswith("System.") and not field.startswith("Custom.") and not field.startswith("Microsoft."):
                        field = f"System.{field}"
                    field = f"/fields/{field}"
                    
                operations.append({
                    "op": "add",
                    "path": field,
                    "value": value
                })
            
            url = f"{self.config.BASE_URL}/{quote(self.config.PROJECT)}/_apis/wit/workitems/{work_item_id}?api-version={self.config.API_VERSION}"
            
            response = requests.patch(url, json=operations, headers=self.headers)
            
            if response.status_code == 200:
                work_item = response.json()
                return {
                    'success': True,
                    'work_item_id': work_item['id'],
                    'work_item': work_item
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to update work item: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to update work item: {str(e)}"
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
    
    def search_tft_features(self, title: str, description: str, threshold: float = 0.7) -> List[Dict]:
        """
        Search Technical Feedback ADO for similar Features.
        
        Searches the Technical Feedback project for existing Feature work items
        that match the provided title and description.
        
        Args:
            title: Issue title to search for
            description: Issue description for matching
            threshold: Similarity threshold (0.0-1.0), default 0.7
            
        Returns:
            List of matching features with metadata and similarity scores
        """
        try:
            from datetime import datetime, timedelta
            
            # Search Technical Feedback organization
            tft_org = "unifiedactiontracker"
            tft_project = "Technical Feedback"
            tft_base_url = f"https://dev.azure.com/{tft_org}"
            
            # Get token for TFT org using InteractiveBrowserCredential
            # This will open a browser window for authentication on first use
            credential = self.config.get_tft_credential()
            token = credential.get_token(self.config.ADO_SCOPE).token
            tft_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Search last 24 months (expanded from 12 to capture older features)
            cutoff_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
            
            # SMART SERVICE NAME EXTRACTION & PROGRESSIVE SEARCH
            # Step 1: Extract base service name from title
            import re
            import json
            import os
            
            # Try to extract the actual Azure service name (skip Azure/Microsoft prefix)
            # Pattern 1: "Azure ServiceName" or "Microsoft ServiceName" - extract just ServiceName
            azure_service_pattern = r'(?:Azure|Microsoft)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            azure_match = re.search(azure_service_pattern, title)
            
            if azure_match:
                # Found "Azure Route Server" → extract "Route Server"
                base_service_name = azure_match.group(1).strip()
                print(f"[TFT Search] Extracted service name (with Azure prefix): {base_service_name}")
            else:
                # Pattern 2: Just find 2-word capitalized phrases
                service_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
                potential_services = re.findall(service_pattern, title)
                
                if not potential_services:
                    print("[TFT Search] No service name pattern found in title, searching all features")
                    product_filter = ""
                    base_service_name = None
                else:
                    # Use the LAST found service name
                    base_service_name = potential_services[-1].strip()
                    print(f"[TFT Search] Extracted service name: {base_service_name}")
            
            if not base_service_name:
                print("[TFT Search] No service name found, searching all features")
                product_filter = ""
            else:
                # Step 2: Use the base service name directly - CONTAINS will match all variations
                # "Route Server" matches: "Route Server", "Azure Route Server", "Route Server - IPv6", etc.
                print(f"[TFT Search] Using service filter: CONTAINS '{base_service_name}'")
                product_filter = f"AND [System.Title] CONTAINS '{base_service_name}'"

            
            # WIQL query to find Features (exclude Closed state)
            wiql_query = f"""
            SELECT [System.Id], [System.Title], [System.Description], [System.ChangedDate], [System.State]
            FROM workitems
            WHERE [System.TeamProject] = '{tft_project}'
            AND [System.WorkItemType] = 'Feature'
            AND [System.ChangedDate] >= '{cutoff_date}'
            AND [System.State] <> 'Closed'
            {product_filter}
            ORDER BY [System.ChangedDate] DESC
            """
            
            print(f"[TFT Search] WIQL Query:\n{wiql_query}")
            
            wiql_url = f"{tft_base_url}/{quote(tft_project)}/_apis/wit/wiql?api-version={self.config.API_VERSION}"
            wiql_response = requests.post(
                wiql_url,
                headers=tft_headers,
                json={'query': wiql_query}
            )
            
            if wiql_response.status_code != 200:
                print(f"[TFT Search] WIQL query failed: {wiql_response.status_code}")
                return []
            
            work_items = wiql_response.json().get('workItems', [])
            if not work_items:
                print("[TFT Search] No Features found in last 12 months")
                return []
            
            print(f"[TFT Search] Found {len(work_items)} Features, calculating similarity...")
            
            # Get detailed work item info (limit to 200 since we have product-filtered results)
            work_item_ids = [str(wi['id']) for wi in work_items[:200]]
            batch_url = f"{tft_base_url}/{quote(tft_project)}/_apis/wit/workitemsbatch?api-version={self.config.API_VERSION}"
            
            batch_response = requests.post(
                batch_url,
                headers=tft_headers,
                json={
                    'ids': work_item_ids,
                    'fields': ['System.Id', 'System.Title', 'System.Description', 'System.State', 'System.CreatedDate']
                }
            )
            
            if batch_response.status_code != 200:
                print(f"[TFT Search] Batch request failed: {batch_response.status_code}")
                return []
            
            # Use AI semantic search for better matching
            print("[TFT Search] Using AI semantic search for similarity matching...")
            try:
                from embedding_service import EmbeddingService
                import time
                
                embedding_service = EmbeddingService()
                
                # Generate embedding for search query
                search_text = f"{title} {description}"
                search_embedding = embedding_service.embed(search_text)
                
                items = batch_response.json().get('value', [])
                print(f"[TFT Search] Processing {len(items)} product-filtered features with AI embeddings")
                
                # Limit to 100 items max to avoid excessive processing
                if len(items) > 100:
                    print(f"[TFT Search] Limiting from {len(items)} to 100 features")
                    items = items[:100]
                
                matches = []
                
                # Process in smaller batches to avoid rate limits
                batch_size = 10
                for i in range(0, len(items), batch_size):
                    batch_items = items[i:i+batch_size]
                    
                    for item in batch_items:
                        try:
                            fields = item.get('fields', {})
                            item_id = fields.get('System.Id')
                            item_title = fields.get('System.Title', '')
                            item_desc = fields.get('System.Description', '')
                            
                            # Strip HTML tags from description
                            if item_desc:
                                from html import unescape
                                import re
                                # Remove HTML tags
                                item_desc = re.sub(r'<[^>]+>', '', item_desc)
                                # Unescape HTML entities (&nbsp;, etc.)
                                item_desc = unescape(item_desc)
                                # Clean up extra whitespace
                                item_desc = ' '.join(item_desc.split())
                            
                            # Generate embedding for TFT feature
                            feature_text = f"{item_title} {item_desc}" if item_desc else item_title
                            feature_embedding = embedding_service.embed(feature_text)
                            
                            # Calculate cosine similarity
                            similarity = embedding_service.cosine_similarity(search_embedding, feature_embedding)
                            
                            if similarity >= threshold:
                                matches.append({
                                    'id': item_id,
                                    'title': item_title,
                                    'description': item_desc,
                                    'state': fields.get('System.State', 'Unknown'),
                                    'created_date': fields.get('System.CreatedDate', ''),
                                    'similarity': round(similarity, 2),
                                    'url': f"{tft_base_url}/{quote(tft_project)}/_workitems/edit/{item_id}",
                                    'source': 'Technical Feedback'
                                })
                        except Exception as e:
                            # Rate limit or other error on individual item - skip it
                            if '429' in str(e) or 'RateLimitReached' in str(e):
                                print(f"[TFT Search] Rate limit hit, stopping AI search early")
                                raise  # Raise to trigger fallback
                            continue
                    
                    # Small delay between batches to avoid rate limits
                    if i + batch_size < len(items):
                        time.sleep(0.5)
                
                # Sort by similarity
                matches.sort(key=lambda x: x['similarity'], reverse=True)
                
                print(f"[TFT Search] AI semantic search found {len(matches)} Features above threshold {threshold}")
                return matches[:10]  # Return top 10 matches
                
            except Exception as e:
                error_msg = str(e)
                print(f"[TFT Search] AI semantic search failed: {e}")
                
                # Return error information instead of using inaccurate text matching fallback
                if '429' in error_msg or 'RateLimitReached' in error_msg:
                    return {
                        'error': 'rate_limit',
                        'message': 'AI search capacity exceeded. The embedding service is temporarily at capacity.',
                        'retry_after': 60,
                        'details': 'Please wait a moment and try Deep Search to search again with AI semantic matching.'
                    }
                else:
                    return {
                        'error': 'ai_failure',
                        'message': f'AI semantic search is temporarily unavailable: {error_msg}',
                        'details': 'Cannot perform accurate TFT Feature matching without AI embeddings.'
                    }
            
        except Exception as e:
            print(f"[TFT Search] Error: {e}")
            return []


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
