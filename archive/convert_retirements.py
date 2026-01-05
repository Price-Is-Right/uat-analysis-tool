#!/usr/bin/env python3

"""
Convert retirements CSV file to JSON for the Evaluating Retirements process
"""

import csv
import json
from datetime import datetime
from typing import List, Dict

def convert_csv_to_json(csv_file_path: str, json_file_path: str) -> None:
    """
    Convert retirements CSV to structured JSON for semantic matching
    
    Args:
        csv_file_path: Path to the retirements CSV file
        json_file_path: Path to output JSON file
    """
    retirements = []
    
    with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Debug: Print column names from first row
            if len(retirements) == 0:
                print("CSV Columns:", list(row.keys()))
            
            # Parse retirement date
            try:
                retirement_date = datetime.strptime(row['RetirementDate'], '%m/%d/%Y').isoformat()
            except ValueError:
                # Handle different date formats if needed
                retirement_date = row['RetirementDate']
            
            # Create structured retirement entry
            retirement_entry = {
                "id": row['Id'],
                "service_name": row['ServiceName'].strip(),
                "retiring_feature": row['RetiringFeature'].strip(),
                "retirement_date": retirement_date,
                "link": row['Link'].strip(),
                # Create searchable text combining all relevant fields
                "searchable_text": f"{row['ServiceName']} {row['RetiringFeature']}".lower().strip(),
                # Extract key terms for semantic matching
                "key_terms": extract_key_terms(row['ServiceName'], row['RetiringFeature']),
                # Determine criticality based on retirement date
                "criticality": determine_criticality(retirement_date)
            }
            
            retirements.append(retirement_entry)
    
    # Create final JSON structure
    retirements_data = {
        "last_updated": datetime.now().isoformat(),
        "total_retirements": len(retirements),
        "retirements": retirements
    }
    
    # Write to JSON file
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(retirements_data, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Successfully converted {len(retirements)} retirements from CSV to JSON")
    print(f"Output saved to: {json_file_path}")

def extract_key_terms(service_name: str, retiring_feature: str) -> List[str]:
    """
    Extract key terms from service name and retiring feature for matching
    
    Args:
        service_name: Name of the Azure service
        retiring_feature: Feature being retired
        
    Returns:
        List of key terms for semantic matching
    """
    combined_text = f"{service_name} {retiring_feature}".lower()
    
    # Common words to ignore
    stop_words = {'azure', 'microsoft', 'the', 'and', 'or', 'for', 'in', 'on', 'at', 'to', 'from', 'by', 'with'}
    
    # Split and clean terms
    terms = []
    words = combined_text.replace('-', ' ').replace('_', ' ').split()
    
    for word in words:
        # Remove punctuation and normalize
        clean_word = ''.join(c for c in word if c.isalnum()).strip()
        if clean_word and len(clean_word) > 2 and clean_word not in stop_words:
            terms.append(clean_word)
    
    # Add original phrases for exact matching
    if service_name.lower() not in terms:
        terms.append(service_name.lower().strip())
    if retiring_feature.lower() not in terms:
        terms.append(retiring_feature.lower().strip())
    
    return list(set(terms))  # Remove duplicates

def determine_criticality(retirement_date_str: str) -> str:
    """
    Determine criticality level based on retirement date
    
    Args:
        retirement_date_str: ISO format date string
        
    Returns:
        Criticality level: 'critical', 'high', 'medium', 'low'
    """
    try:
        if retirement_date_str.count('/') > 0:
            # Handle original date format
            retirement_date = datetime.strptime(retirement_date_str, '%m/%d/%Y')
        else:
            # Handle ISO format
            retirement_date = datetime.fromisoformat(retirement_date_str.replace('Z', '+00:00'))
        
        now = datetime.now()
        days_until_retirement = (retirement_date - now).days
        
        if days_until_retirement < 0:
            return 'critical'  # Already retired
        elif days_until_retirement <= 90:
            return 'critical'  # Less than 3 months
        elif days_until_retirement <= 180:
            return 'high'     # Less than 6 months
        elif days_until_retirement <= 365:
            return 'medium'   # Less than 1 year
        else:
            return 'low'      # More than 1 year
            
    except (ValueError, TypeError):
        return 'medium'  # Default if date parsing fails

if __name__ == "__main__":
    # Convert the retirements CSV to JSON
    convert_csv_to_json(
        csv_file_path="C:\\Projects\\Hack\\retirements.csv",
        json_file_path="C:\\Projects\\Hack\\retirements.json"
    )