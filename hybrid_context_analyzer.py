"""
AI-Powered Hybrid Context Analyzer
Combines LLM classification with pattern matching features
Designed to work alongside existing intelligent_context_analyzer.py

This module:
1. Uses pattern matching from intelligent_context_analyzer as features
2. Feeds those features into LLM for final classification
3. Provides semantic similarity search via vector search
4. Maintains full backward compatibility
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os

# Import existing pattern-based analyzer
from intelligent_context_analyzer import IntelligentContextAnalyzer

# Import AI services
from ai_config import get_config, validate_config
from llm_classifier import LLMClassifier, ClassificationResult
from embedding_service import EmbeddingService
from vector_search import VectorSearchService


@dataclass
class HybridAnalysisResult:
    """Result from hybrid AI+pattern analysis"""
    # LLM results (primary)
    category: str
    intent: str
    business_impact: str
    confidence: float
    reasoning: str
    
    # Pattern matching features (supporting evidence)
    pattern_category: str
    pattern_intent: str
    pattern_confidence: float
    pattern_features: Dict[str, Any]
    
    # Semantic search results
    similar_issues: List[Dict]
    
    # Metadata
    source: str  # "llm", "pattern", or "hybrid"
    agreement: bool  # LLM and patterns agree
    
    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "intent": self.intent,
            "business_impact": self.business_impact,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "pattern_features": {
                "category": self.pattern_category,
                "intent": self.pattern_intent,
                "confidence": self.pattern_confidence,
                "features": self.pattern_features
            },
            "similar_issues": self.similar_issues,
            "metadata": {
                "source": self.source,
                "agreement": self.agreement
            }
        }


class HybridContextAnalyzer:
    """
    Hybrid analyzer combining LLM and pattern matching
    
    Strategy:
    1. Run pattern matching first (fast, provides features)
    2. Pass pattern features to LLM as context
    3. LLM makes final decision with pattern insights
    4. Search for similar issues using embeddings
    5. Fall back to patterns if LLM fails
    """
    
    def __init__(self, use_ai: bool = True):
        """
        Initialize hybrid analyzer
        
        Args:
            use_ai: Whether to use AI services (default True)
                    If False, falls back to pure pattern matching
        """
        # Always initialize pattern matcher
        self.pattern_analyzer = IntelligentContextAnalyzer()
        
        # AI configuration
        self.use_ai = use_ai
        self.config = get_config()
        
        # Initialize AI services if enabled
        if self.use_ai:
            try:
                validate_config()
                
                self.llm_classifier = LLMClassifier()
                self.embedding_service = EmbeddingService()
                self.vector_search = VectorSearchService()
                
                print("[HybridAnalyzer] AI services initialized successfully")
                print(f"[HybridAnalyzer] Mode: AI-powered with pattern features")
            except Exception as e:
                print(f"[HybridAnalyzer] AI initialization failed: {e}")
                print("[HybridAnalyzer] Falling back to pattern matching only")
                self.use_ai = False
        else:
            print("[HybridAnalyzer] Mode: Pattern matching only (AI disabled)")
    
    def _extract_pattern_features(self, pattern_result: Any) -> Dict[str, Any]:
        """
        Extract features from pattern matching result
        
        Args:
            pattern_result: Result from IntelligentContextAnalyzer
            
        Returns:
            Dictionary of features for LLM
        """
        features = {}
        
        # Basic classification
        features["category_scores"] = {}
        features["detected_products"] = []
        features["technical_indicators"] = []
        
        # Extract category if available
        if hasattr(pattern_result, 'category'):
            # Add the pattern category with its confidence
            category_str = str(pattern_result.category)
            if hasattr(pattern_result, 'confidence'):
                features["category_scores"][category_str] = pattern_result.confidence
            else:
                features["category_scores"][category_str] = 0.5
            
            # Get additional category scores from reasoning if available
            if hasattr(pattern_result, 'reasoning') and isinstance(pattern_result.reasoning, dict):
                reasoning = pattern_result.reasoning
                
                # Look for confidence factors or category analysis
                if "confidence_factors" in reasoning:
                    for factor in reasoning["confidence_factors"]:
                        if "Category confidence" in factor:
                            confidence = float(factor.split(":")[-1].strip())
                            features["category_scores"][category_str] = confidence
                
                # Extract Microsoft products
                if "microsoft_products_detected" in reasoning:
                    products = reasoning["microsoft_products_detected"]
                    if isinstance(products, list):
                        for product in products:
                            if isinstance(product, dict):
                                features["detected_products"].append(product.get("name", ""))
                            else:
                                features["detected_products"].append(str(product))
        
        # Look for technical indicators in text
        technical_keywords = [
            "error", "issue", "problem", "not working", "failing", "failed",
            "unable to", "cannot", "can't", "trouble", "difficulty"
        ]
        
        return features
    
    def analyze(
        self,
        title: str,
        description: str,
        impact: str = "",
        search_similar: bool = True
    ) -> HybridAnalysisResult:
        """
        Perform hybrid analysis using AI + patterns
        
        Args:
            title: Issue title
            description: Issue description
            impact: Business impact statement
            search_similar: Whether to search for similar issues
            
        Returns:
            HybridAnalysisResult with complete analysis
        """
        print(f"\n{'='*80}")
        print(f"🔬 HYBRID CONTEXT ANALYZER - Processing Issue")
        print(f"{'='*80}")
        print(f"Title: {title[:70]}...")
        print(f"Mode: {'AI-Powered' if self.use_ai else 'Pattern Only'}")
        print(f"{'='*80}\n")
        
        # STEP 1: Run pattern matching (always, provides features)
        print("📊 Step 1: Pattern Matching Analysis...")
        pattern_result = self.pattern_analyzer.analyze_context(title, description, impact)
        
        # Extract pattern features
        pattern_features = self._extract_pattern_features(pattern_result)
        pattern_category = pattern_result.category if hasattr(pattern_result, 'category') else "technical_support"
        pattern_intent = pattern_result.intent if hasattr(pattern_result, 'intent') else "service_inquiry"
        pattern_confidence = pattern_result.confidence if hasattr(pattern_result, 'confidence') else 0.5
        
        print(f"   ✓ Pattern Category: {pattern_category}")
        print(f"   ✓ Pattern Intent: {pattern_intent}")
        print(f"   ✓ Pattern Confidence: {pattern_confidence:.2f}")
        
        # STEP 2: Search for similar issues (if enabled)
        similar_issues = []
        if search_similar and self.use_ai:
            print("\n🔍 Step 2: Semantic Similarity Search...")
            try:
                # This would search indexed UATs/issues
                # For now, return empty list (needs indexed data)
                similar_results = []
                for result in similar_results:
                    similar_issues.append({
                        "id": result.item_id,
                        "title": result.title,
                        "similarity": result.similarity
                    })
                print(f"   ✓ Found {len(similar_issues)} similar issues")
            except Exception as e:
                print(f"   ⚠ Similarity search failed: {e}")
        
        # STEP 3: LLM Classification (if AI enabled)
        if self.use_ai:
            print("\n🤖 Step 3: LLM Classification with Pattern Features...")
            try:
                llm_result = self.llm_classifier.classify(
                    title=title,
                    description=description,
                    impact=impact,
                    pattern_features=pattern_features,
                    use_cache=True
                )
                
                # Check if LLM and patterns agree
                agreement = (
                    llm_result.category == pattern_category and
                    llm_result.intent == pattern_intent
                )
                
                print(f"   ✓ LLM Category: {llm_result.category}")
                print(f"   ✓ LLM Intent: {llm_result.intent}")
                print(f"   ✓ LLM Confidence: {llm_result.confidence:.2f}")
                print(f"   {'✓' if agreement else '⚠'} LLM/Pattern Agreement: {agreement}")
                
                # Use LLM results as primary
                result = HybridAnalysisResult(
                    category=llm_result.category,
                    intent=llm_result.intent,
                    business_impact=llm_result.business_impact,
                    confidence=llm_result.confidence,
                    reasoning=llm_result.reasoning,
                    pattern_category=pattern_category,
                    pattern_intent=pattern_intent,
                    pattern_confidence=pattern_confidence,
                    pattern_features=pattern_features,
                    similar_issues=similar_issues,
                    source="hybrid" if agreement else "llm",
                    agreement=agreement
                )
                
                print(f"\n✅ Analysis Complete (Source: {result.source})")
                return result
                
            except Exception as e:
                print(f"   ✗ LLM classification failed: {e}")
                print(f"   ↩️  Falling back to pattern matching")
        
        # STEP 4: Fallback to pattern matching
        print("\n📋 Using Pattern Matching Results...")
        
        result = HybridAnalysisResult(
            category=pattern_category,
            intent=pattern_intent,
            business_impact=impact if impact else "medium",
            confidence=pattern_confidence,
            reasoning=f"Pattern matching only (AI {'disabled' if not self.use_ai else 'unavailable'})",
            pattern_category=pattern_category,
            pattern_intent=pattern_intent,
            pattern_confidence=pattern_confidence,
            pattern_features=pattern_features,
            similar_issues=similar_issues,
            source="pattern",
            agreement=True  # Only using patterns, so agreement is N/A
        )
        
        print(f"✅ Analysis Complete (Source: pattern fallback)")
        return result
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get status of AI services"""
        if not self.use_ai:
            return {
                "enabled": False,
                "reason": "AI disabled"
            }
        
        try:
            return {
                "enabled": True,
                "llm_cache_stats": self.llm_classifier.get_cache_stats(),
                "embedding_cache_stats": self.embedding_service.get_cache_stats()
            }
        except Exception as e:
            return {
                "enabled": False,
                "reason": f"Error: {e}"
            }


def test_hybrid_analyzer():
    """Test the hybrid analyzer with real cases"""
    print("Hybrid Context Analyzer Test")
    print("=" * 80)
    
    # Test cases from previous issues
    test_cases = [
        {
            "title": "SCVMM to Azure Migrate Roadmap",
            "description": "We are looking to migrate several workloads from SCVMM to Azure Migrate, but I am running into trouble connecting the SCVMM service to Azure Migrate. Is this possible?",
            "impact": "Blocking our migration to Azure",
            "expected_category": "technical_support"
        },
        {
            "title": "SQL MI in West Europe",
            "description": "Is SQL Managed Instance with Azure SQL Database Hyperscale available in West Europe region? This service is required in West Europe.",
            "impact": "Critical for production deployment",
            "expected_category": "service_availability"
        },
        {
            "title": "Planner & Roadmap demo",
            "description": "Can you give me a demo of the Planner & Roadmap feature to understand how it works?",
            "impact": "Want to evaluate if it fits our needs",
            "expected_category": "seeking_guidance"
        }
    ]
    
    analyzer = HybridContextAnalyzer(use_ai=True)
    
    print("\n" + "="*80)
    print("AI Services Status:")
    status = analyzer.get_ai_status()
    print(json.dumps(status, indent=2))
    print("="*80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}: {test_case['title']}")
        print(f"Expected Category: {test_case['expected_category']}")
        print(f"{'='*80}")
        
        result = analyzer.analyze(
            title=test_case['title'],
            description=test_case['description'],
            impact=test_case['impact'],
            search_similar=False  # Don't search without indexed data
        )
        
        print(f"\n📊 RESULTS:")
        print(f"   Category: {result.category}")
        print(f"   Intent: {result.intent}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Source: {result.source}")
        print(f"   Agreement: {result.agreement}")
        print(f"   Reasoning: {result.reasoning[:200]}...")
        
        # Check if matches expected
        matches = result.category == test_case['expected_category']
        print(f"\n   {'✅ CORRECT' if matches else '❌ INCORRECT'}")


if __name__ == "__main__":
    import json
    test_hybrid_analyzer()
