#!/usr/bin/env python3

"""
Retirement Checker for Azure services and features
Checks submissions against known Azure service retirements
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher

class RetirementChecker:
    """
    Checks submissions against Azure service retirements database
    """
    
    def __init__(self, retirements_json_path: str = "retirements.json"):
        """
        Initialize with retirements database
        
        Args:
            retirements_json_path: Path to retirements JSON file
        """
        self.retirements_json_path = retirements_json_path
        self.retirements_data = self._load_retirements()
        
    def _load_retirements(self) -> Dict:
        """Load retirements data from JSON file"""
        try:
            with open(self.retirements_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Retirements file not found at {self.retirements_json_path}")
            return {"retirements": []}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in retirements file {self.retirements_json_path}")
            return {"retirements": []}
    
    def check_retirement_match(self, title: str, description: str = "") -> Tuple[bool, List[Dict]]:
        """
        Check if submission matches any known retirements
        
        Args:
            title: Issue title to check
            description: Issue description to check
            
        Returns:
            Tuple of (is_retirement_issue, list_of_matching_retirements)
        """
        if not self.retirements_data or not self.retirements_data.get("retirements"):
            return False, []
        
        combined_text = f"{title} {description}".lower().strip()
        
        # Pre-filter: Check if this is clearly NOT about retirements
        if not self._is_retirement_related(combined_text):
            return False, []
        
        matching_retirements = []
        
        for retirement in self.retirements_data["retirements"]:
            match_score = self._calculate_match_score(combined_text, retirement)
            
            if match_score > 0.6:  # Threshold for retirement match - strict relevance required
                matching_retirements.append({
                    **retirement,
                    "match_score": match_score,
                    "match_reason": self._get_match_reason(combined_text, retirement)
                })
        
        # Sort by match score (highest first)
        matching_retirements.sort(key=lambda x: x["match_score"], reverse=True)
        
        is_retirement_issue = len(matching_retirements) > 0
        return is_retirement_issue, matching_retirements
    
    def _calculate_match_score(self, text: str, retirement: Dict) -> float:
        """
        Calculate match score between text and retirement entry with stricter matching
        
        Args:
            text: Text to match against
            retirement: Retirement entry
            
        Returns:
            Match score between 0 and 1
        """
        score = 0.0
        text_words = set(re.findall(r'\b\w+\b', text.lower()))
        
        # 1. Exact service name match (highest weight) - must be substantial match
        service_name = retirement["service_name"].lower()
        service_words = service_name.split()
        
        if service_name in text:
            score += 0.6  # Full service name match
        elif len(service_words) >= 2:
            # For multi-word services, require at least 2 words to match
            matching_service_words = sum(1 for word in service_words if word in text_words and len(word) > 2)
            if matching_service_words >= 2:
                score += 0.4
            elif matching_service_words == 1 and len(service_words) == 2:
                score += 0.2  # Partial match for 2-word services
        
        # 2. Retiring feature match - must be meaningful
        retiring_feature = retirement["retiring_feature"].lower()
        if retiring_feature in text:
            score += 0.4
        else:
            # Only count feature word matches if they're substantial (> 3 chars)
            feature_words = [word for word in retiring_feature.split() if len(word) > 3]
            matching_feature_words = sum(1 for word in feature_words if word in text_words)
            if matching_feature_words >= 2:
                score += 0.2
            elif matching_feature_words == 1 and len(feature_words) <= 2:
                score += 0.1
        
        # 3. Key terms match - only meaningful terms (> 2 chars)
        meaningful_terms = [term for term in retirement["key_terms"] if len(term) > 2]
        key_terms_matched = sum(1 for term in meaningful_terms if term in text)
        
        # Require multiple key term matches for significant score
        if key_terms_matched >= 3:
            score += 0.3
        elif key_terms_matched >= 2:
            score += 0.2
        elif key_terms_matched == 1:
            score += 0.05  # Very low score for single term match
        
        # 4. Semantic similarity - only if there's already some match
        if score > 0.2:  # Only apply semantic similarity if there's already some relevance
            searchable_text = retirement["searchable_text"]
            similarity = SequenceMatcher(None, text, searchable_text).ratio()
            if similarity > 0.3:  # Only count if similarity is meaningful
                score += similarity * 0.2  # Reduced weight
        
        # 5. Boost score for critical retirements - only if already relevant
        if score > 0.3:
            if retirement.get("criticality") == "critical":
                score *= 1.1  # Reduced boost
            elif retirement.get("criticality") == "high":
                score *= 1.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _is_retirement_related(self, text: str) -> bool:
        """
        Determine if the text is actually about service retirements/deprecations
        
        Args:
            text: Combined title and description text
            
        Returns:
            True if likely about retirements, False if clearly about other topics
        """
        # Strong indicators this is NOT about retirements
        non_retirement_indicators = [
            # Compliance and regulatory topics
            'compliance', 'regulatory', 'nist', 'sox', 'hipaa', 'gdpr', 'pci dss', 'iso 27001',
            'audit', 'certification', 'policy', 'governance', 'regulation',
            
            # Feature requests and support topics  
            'feature request', 'enhancement', 'new feature', 'functionality',
            'configuration', 'setup', 'installation', 'deployment',
            'troubleshooting', 'bug', 'issue', 'error', 'problem',
            'how to', 'guidance', 'documentation', 'best practice',
            
            # Specific product features (not retirements)
            'defender for cloud', 'security center', 'sentinel', 'purview',
            'cost management', 'billing', 'subscription', 'rbac', 'permissions',
            'networking', 'virtual network', 'storage account', 'backup',
            
            # Business/organizational contexts
            'customer needs', 'client requires', 'organization', 'company',
            'business requirement', 'project', 'implementation'
        ]
        
        # Strong indicators this IS about retirements
        retirement_indicators = [
            'retirement', 'retiring', 'deprecated', 'deprecating', 'end of life',
            'end of support', 'discontinued', 'sunsetting', 'migration required',
            'service ending', 'no longer supported', 'being retired',
            'replacement needed', 'alternative required'
        ]
        
        # Check for retirement indicators first
        retirement_score = sum(1 for indicator in retirement_indicators if indicator in text)
        if retirement_score >= 1:
            return True  # Clearly about retirements
        
        # Check for non-retirement indicators
        non_retirement_score = sum(1 for indicator in non_retirement_indicators if indicator in text)
        if non_retirement_score >= 2:
            return False  # Clearly NOT about retirements
        
        # Edge case: If text contains specific Azure service names but no retirement context,
        # it's likely a feature/support request, not a retirement inquiry
        azure_services = [
            'azure synapse', 'azure functions', 'azure monitor', 'azure sql',
            'application gateway', 'application insights', 'cosmos db'
        ]
        
        service_mentions = sum(1 for service in azure_services if service in text)
        
        # If mentions Azure services but has compliance/support context, it's not retirement
        if service_mentions >= 1 and non_retirement_score >= 1:
            return False
        
        # Default: allow retirement checking for ambiguous cases
        return True
    
    def _get_match_reason(self, text: str, retirement: Dict) -> str:
        """
        Generate human-readable match reason
        
        Args:
            text: Matched text
            retirement: Retirement entry
            
        Returns:
            String explaining why this retirement matched
        """
        reasons = []
        
        service_name = retirement["service_name"].lower()
        retiring_feature = retirement["retiring_feature"].lower()
        
        if service_name in text:
            reasons.append(f"Service '{retirement['service_name']}' mentioned")
        
        if retiring_feature in text:
            reasons.append(f"Retiring feature '{retirement['retiring_feature']}' mentioned")
        
        # Check for key terms
        matched_terms = [term for term in retirement["key_terms"] if term in text]
        if matched_terms:
            reasons.append(f"Key terms matched: {', '.join(matched_terms[:3])}")
        
        return "; ".join(reasons) if reasons else "Semantic similarity detected"
    
    def get_retirement_summary(self, retirement_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific retirement
        
        Args:
            retirement_id: ID of the retirement
            
        Returns:
            Retirement details or None if not found
        """
        for retirement in self.retirements_data.get("retirements", []):
            if retirement["id"] == retirement_id:
                return retirement
        return None
    
    def get_critical_retirements(self) -> List[Dict]:
        """
        Get all critical retirements (already retired or retiring soon)
        
        Returns:
            List of critical retirements
        """
        return [
            r for r in self.retirements_data.get("retirements", [])
            if r.get("criticality") == "critical"
        ]
    
    def format_retirement_for_display(self, retirement: Dict) -> Dict:
        """
        Format retirement data for display in results
        
        Args:
            retirement: Retirement entry
            
        Returns:
            Formatted retirement data for UI display
        """
        try:
            # Parse retirement date
            retirement_date = datetime.fromisoformat(retirement["retirement_date"])
            formatted_date = retirement_date.strftime("%B %d, %Y")
            
            # Determine status
            now = datetime.now()
            if retirement_date < now:
                status = "ALREADY RETIRED"
                urgency = "critical"
            else:
                days_left = (retirement_date - now).days
                if days_left <= 90:
                    status = f"RETIRING IN {days_left} DAYS"
                    urgency = "critical"
                elif days_left <= 180:
                    status = f"RETIRING IN {days_left} DAYS"
                    urgency = "high"
                else:
                    status = f"RETIRING {formatted_date}"
                    urgency = "medium"
            
            return {
                "id": retirement["id"],
                "title": f"{retirement['service_name']} - {retirement['retiring_feature']}",
                "description": f"Service retirement scheduled for {formatted_date}",
                "service": retirement["service_name"],
                "feature": retirement["retiring_feature"],
                "retirement_date": formatted_date,
                "status": status,
                "urgency": urgency,
                "link": retirement["link"],
                "match_score": retirement.get("match_score", 0),
                "match_reason": retirement.get("match_reason", ""),
                "source": "Retirement Notice",
                "type": "retirement"
            }
            
        except (ValueError, KeyError) as e:
            # Fallback formatting if date parsing fails
            return {
                "id": retirement.get("id", "unknown"),
                "title": f"{retirement.get('service_name', 'Unknown')} - {retirement.get('retiring_feature', 'Feature')}",
                "description": "Azure service retirement notice",
                "status": "RETIREMENT SCHEDULED",
                "urgency": retirement.get("criticality", "medium"),
                "link": retirement.get("link", ""),
                "match_score": retirement.get("match_score", 0),
                "source": "Retirement Notice",
                "type": "retirement"
            }

# Test the retirement checker
if __name__ == "__main__":
    checker = RetirementChecker("C:\\Projects\\Hack\\retirements.json")
    
    # Test cases
    test_cases = [
        ("Azure Synapse Runtime for Apache Spark 3.2 issues", "Having problems with Spark 3.2 in Synapse"),
        ("Storage Account Classic migration", "Need help migrating classic storage accounts"),
        ("Basic Load Balancer configuration", "Setting up basic load balancer"),
        ("Random unrelated issue", "This should not match any retirements"),
    ]
    
    print("=== RETIREMENT CHECKER TEST ===")
    for title, desc in test_cases:
        print(f"\nTesting: '{title}'")
        is_retirement, matches = checker.check_retirement_match(title, desc)
        print(f"Is Retirement: {is_retirement}")
        if matches:
            print(f"Top Match: {matches[0]['service_name']} - {matches[0]['retiring_feature']} (Score: {matches[0]['match_score']:.2f})")
            print(f"Reason: {matches[0]['match_reason']}")