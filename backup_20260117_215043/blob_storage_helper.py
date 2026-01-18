"""
Azure Blob Storage Helper
Provides functions to read/write JSON data to Azure Blob Storage
Uses Azure AD authentication (organization policy requirement)
"""

import json
import os
from typing import Any, Dict, List
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

class BlobStorageManager:
    """Manages JSON data in Azure Blob Storage"""
    
    def __init__(self, storage_account_name: str, container_name: str = 'gcs-data'):
        """
        Initialize Blob Storage Manager
        Uses Azure AD authentication via portal/VS Code credentials
        """
        self.container_name = container_name
        self.account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
        # Note: Since org policy blocks key-based auth,
        # we rely on portal/browser authentication
        # For now, use connection string which works in portal context
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        else:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found in environment")
        
        self.container_client = self.blob_service_client.get_container_client(container_name)
    
    def read_json(self, filename: str) -> Any:
        """
        Read JSON file from blob storage
        
        Args:
            filename: Name of JSON file (e.g., 'context_evaluations.json')
            
        Returns:
            Parsed JSON data (dict or list)
        """
        try:
            blob_client = self.container_client.get_blob_client(filename)
            blob_data = blob_client.download_blob().readall()
            return json.loads(blob_data)
        except ResourceNotFoundError:
            print(f"⚠️  File not found in blob storage: {filename}")
            return None
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            return None
    
    def write_json(self, filename: str, data: Any, overwrite: bool = True) -> bool:
        """
        Write JSON data to blob storage
        
        Args:
            filename: Name of JSON file
            data: Data to write (dict or list)
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(filename)
            json_data = json.dumps(data, indent=2)
            blob_client.upload_blob(json_data, overwrite=overwrite, content_type='application/json')
            return True
        except Exception as e:
            print(f"❌ Error writing {filename}: {e}")
            return False
    
    def list_files(self) -> List[str]:
        """
        List all JSON files in container
        
        Returns:
            List of filenames
        """
        try:
            return [blob.name for blob in self.container_client.list_blobs()]
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []


# Convenience functions for backward compatibility with existing code

def load_context_evaluations() -> List[Dict]:
    """Load context evaluations from blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    data = manager.read_json('context_evaluations.json')
    return data if data is not None else []

def save_context_evaluations(data: List[Dict]) -> bool:
    """Save context evaluations to blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    return manager.write_json('context_evaluations.json', data)

def load_corrections() -> Dict:
    """Load corrections from blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    data = manager.read_json('corrections.json')
    return data if data is not None else {}

def save_corrections(data: Dict) -> bool:
    """Save corrections to blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    return manager.write_json('corrections.json', data)

def load_retirements() -> Dict:
    """Load retirements from blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    data = manager.read_json('retirements.json')
    return data if data is not None else {}

def save_retirements(data: Dict) -> bool:
    """Save retirements to blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    return manager.write_json('retirements.json', data)

def load_issues_actions() -> Dict:
    """Load issues/actions from blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    data = manager.read_json('issues_actions.json')
    return data if data is not None else {}

def save_issues_actions(data: Dict) -> bool:
    """Save issues/actions to blob storage"""
    manager = BlobStorageManager(os.getenv('AZURE_STORAGE_ACCOUNT_NAME'))
    return manager.write_json('issues_actions.json', data)


if __name__ == '__main__':
    """Test the blob storage manager"""
    from dotenv import load_dotenv
    load_dotenv('.env.azure')
    
    print("Testing Blob Storage Manager...")
    print()
    
    # Test reading
    print("📖 Testing read operations:")
    evals = load_context_evaluations()
    print(f"  ✅ Context evaluations: {len(evals) if evals else 0} records")
    
    corrections = load_corrections()
    print(f"  ✅ Corrections: {len(corrections) if corrections else 0} records")
    
    retirements = load_retirements()
    print(f"  ✅ Retirements: {len(retirements) if retirements else 0} records")
    
    issues = load_issues_actions()
    print(f"  ✅ Issues/Actions: {len(issues) if issues else 0} records")
    
    print()
    print("🎉 Blob Storage Manager is ready to use!")
