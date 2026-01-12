"""
Hybrid ego pain calculator - combines rule-based and LLM-based approaches.
Novel contribution: Hybrid approach for more reliable ego pain calculation.
"""
from typing import Dict, Any, Optional
from app.agents.ego_impact import EgoImpactCalculator
from app.agents.ego_structure import EgoDimensions
from app.agents.wedana import wedana_classifier
from app.utils.logger import logger
from app.utils.error_handler import EgoCalculationError, handle_error


class HybridEgoPainCalculator:
    """
    Combines rule-based and LLM-based ego pain calculation.
    Provides confidence scores based on agreement between methods.
    """
    
    def __init__(self, rule_weight: float = 0.6, llm_weight: float = 0.4):
        """
        Initialize hybrid calculator.
        
        Args:
            rule_weight: Weight for rule-based calculation (default 0.6)
            llm_weight: Weight for LLM-based calculation (default 0.4)
        """
        self.impact_calculator = EgoImpactCalculator()
        self.rule_weight = rule_weight
        self.llm_weight = llm_weight
        
        # Normalize weights
        total = rule_weight + llm_weight
        if total > 0:
            self.rule_weight /= total
            self.llm_weight /= total
        
        logger.debug(f"HybridEgoPainCalculator initialized (rule: {self.rule_weight}, llm: {self.llm_weight})")
    
    def calculate_pain(
        self, 
        user_input: str, 
        ego_dimensions: EgoDimensions,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive pain analysis using hybrid approach.
        
        Args:
            user_input: User's input text
            ego_dimensions: Current ego dimensions
            use_llm: Whether to use LLM calculation (default True)
            
        Returns:
            Dictionary with comprehensive pain analysis
        """
        # Rule-based calculation
        dimension_impacts = self.impact_calculator.calculate_dimension_impact(
            user_input, ego_dimensions
        )
        rule_based_pain = self.impact_calculator.calculate_aggregate_pain(
            dimension_impacts, ego_dimensions
        )
        
        # LLM-based calculation (if enabled)
        llm_pain = 0.0
        llm_error = None
        if use_llm:
            try:
                # Convert ego dimensions to dict for LLM
                ego_dict = ego_dimensions.to_dict()
                llm_result = wedana_classifier(user_input, ego_dict)
                llm_pain = float(llm_result.get("final_answer", 0.0))
                
                # Validate LLM result
                if not (-1.0 <= llm_pain <= 1.0):
                    logger.warning(f"LLM returned out-of-range value: {llm_pain}, clamping")
                    llm_pain = max(-1.0, min(1.0, llm_pain))
                    
            except Exception as e:
                logger.warning(f"LLM calculation failed: {e}, using rule-based only")
                llm_error = str(e)
                llm_pain = rule_based_pain  # Fallback to rule-based
        
        # Weighted combination
        if use_llm and not llm_error:
            final_pain = (
                rule_based_pain * self.rule_weight + 
                llm_pain * self.llm_weight
            )
        else:
            # If LLM failed, use rule-based only
            final_pain = rule_based_pain
        
        # Clamp to [-1, 1]
        final_pain = max(-1.0, min(1.0, final_pain))
        
        # Find most affected dimension
        most_affected = self.impact_calculator.get_most_affected_dimension(
            dimension_impacts
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            dimension_impacts, 
            rule_based_pain, 
            llm_pain if use_llm and not llm_error else None
        )
        
        return {
            "final_pain": final_pain,
            "rule_based_pain": rule_based_pain,
            "llm_pain": llm_pain if use_llm else None,
            "llm_error": llm_error,
            "dimension_impacts": dimension_impacts,
            "most_affected_dimension": most_affected[0],
            "most_affected_impact": most_affected[1],
            "ego_strength": ego_dimensions.ego_strength,
            "confidence": confidence,
            "method": "hybrid" if use_llm and not llm_error else "rule_based_only"
        }
    
    def _calculate_confidence(
        self, 
        dimension_impacts: Dict[str, float],
        rule_pain: float,
        llm_pain: Optional[float]
    ) -> float:
        """
        Calculate confidence based on agreement between methods and signal strength.
        
        Args:
            dimension_impacts: Impact scores per dimension
            rule_pain: Rule-based pain score
            llm_pain: LLM-based pain score (optional)
            
        Returns:
            Confidence score (0-1)
        """
        # Agreement between rule and LLM
        if llm_pain is not None:
            agreement = 1.0 - abs(rule_pain - llm_pain) / 2.0
        else:
            agreement = 0.5  # Neutral if no LLM comparison
        
        # Strength of signal (how clear the impact is)
        max_impact = max(abs(v) for v in dimension_impacts.values()) if dimension_impacts else 0.0
        
        # Combined confidence
        # 60% from agreement, 40% from signal strength
        confidence = (agreement * 0.6) + (max_impact * 0.4)
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence

