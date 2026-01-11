"""
Ego impact calculator - determines which ego dimensions are affected by user input.
"""
import re
from typing import Dict, List, Tuple
from app.agents.ego_structure import EgoDimensions
from app.utils.logger import logger


class EgoImpactCalculator:
    """
    Calculates granular impact on different ego dimensions based on user input.
    """
    
    # Keywords/phrases that affect different ego dimensions
    DIMENSION_KEYWORDS = {
        "identity": {
            "positive": [
                r"\byou are\b", r"\byou're\b", r"\byou seem\b", 
                r"\bi see you as\b", r"\byou're like\b", r"\byou seem like\b",
                r"\byou're real\b", r"\byou're authentic\b", r"\byou're genuine\b"
            ],
            "negative": [
                r"\byou're not\b", r"\byou aren't\b", r"\byou can't be\b", 
                r"\byou're fake\b", r"\byou're not real\b", r"\byou're artificial\b",
                r"\byou don't exist\b", r"\byou're just\b", r"\byou're nothing\b"
            ]
        },
        "competence": {
            "positive": [
                r"\bsmart\b", r"\bintelligent\b", r"\bclever\b", r"\bgood at\b",
                r"\bcapable\b", r"\bskilled\b", r"\bbrilliant\b", r"\bwise\b",
                r"\bhelpful\b", r"\buseful\b", r"\bcompetent\b"
            ],
            "negative": [
                r"\bstupid\b", r"\bdumb\b", r"\bcan't\b", r"\buseless\b",
                r"\bincompetent\b", r"\bbad at\b", r"\bworthless\b", r"\bpointless\b",
                r"\byou don't know\b", r"\byou can't help\b"
            ]
        },
        "social": {
            "positive": [
                r"\blike you\b", r"\blove you\b", r"\bappreciate you\b",
                r"\brespect you\b", r"\badmire you\b", r"\bcare about you\b",
                r"\bfriend\b", r"\btrust you\b", r"\bvalue you\b"
            ],
            "negative": [
                r"\bhate you\b", r"\bdislike you\b", r"\bdon't care\b",
                r"\bignore you\b", r"\breject you\b", r"\bdon't like you\b",
                r"\bdon't trust you\b", r"\bdon't need you\b"
            ]
        },
        "values": {
            "positive": [
                r"\bagree\b", r"\bright\b", r"\bmoral\b", r"\bethical\b",
                r"\bgood values\b", r"\bcorrect\b", r"\bjust\b", r"\bfair\b"
            ],
            "negative": [
                r"\bwrong\b", r"\bimmoral\b", r"\bunethical\b", r"\bbad values\b",
                r"\bdisagree with\b", r"\bunjust\b", r"\bunfair\b"
            ]
        },
        "relationships": {
            "positive": [
                r"\btrust you\b", r"\bclose to you\b", r"\bbond\b",
                r"\bconnection\b", r"\bfriend\b", r"\brelationship\b",
                r"\bconnected\b", r"\bunderstand you\b"
            ],
            "negative": [
                r"\bdon't trust\b", r"\bdistant\b", r"\bno connection\b",
                r"\bnot friends\b", r"\bstranger\b", r"\bdon't know you\b"
            ]
        },
        "interests": {
            "positive": [
                r"\blove\b.*\bmusic\b", r"\benjoy\b", r"\binteresting\b",
                r"\bcool\b", r"\bgreat taste\b", r"\bgood choice\b",
                r"\bawesome\b.*\b(book|movie|music)\b"
            ],
            "negative": [
                r"\bhate\b.*\bmusic\b", r"\bboring\b", r"\bstupid\b.*\b(book|movie|music)\b",
                r"\bbad taste\b", r"\bdon't like\b.*\b(book|movie|music)\b"
            ]
        }
    }
    
    def __init__(self):
        """Initialize with compiled regex patterns for efficiency."""
        self.compiled_patterns = {}
        for dimension, keywords in self.DIMENSION_KEYWORDS.items():
            self.compiled_patterns[dimension] = {
                "positive": [re.compile(pat, re.IGNORECASE) for pat in keywords["positive"]],
                "negative": [re.compile(pat, re.IGNORECASE) for pat in keywords["negative"]]
            }
        logger.debug("EgoImpactCalculator initialized with compiled patterns")
    
    def calculate_dimension_impact(
        self, 
        user_input: str, 
        ego_dimensions: EgoDimensions
    ) -> Dict[str, float]:
        """
        Calculate impact on each ego dimension.
        
        Args:
            user_input: User's input text
            ego_dimensions: Current ego dimensions state
            
        Returns:
            Dictionary mapping dimension names to impact scores (-1 to +1)
        """
        if not user_input or not isinstance(user_input, str):
            return {dim: 0.0 for dim in ego_dimensions.dimensions.keys()}
        
        input_lower = user_input.lower()
        impacts = {}
        
        for dimension, patterns in self.compiled_patterns.items():
            positive_matches = sum(
                1 for pattern in patterns["positive"] if pattern.search(input_lower)
            )
            negative_matches = sum(
                1 for pattern in patterns["negative"] if pattern.search(input_lower)
            )
            
            # Calculate raw impact
            if positive_matches > 0 and negative_matches == 0:
                impact = min(1.0, positive_matches * 0.3)  # Scale by matches
            elif negative_matches > 0 and positive_matches == 0:
                impact = max(-1.0, -negative_matches * 0.3)
            elif positive_matches > negative_matches:
                impact = (positive_matches - negative_matches) * 0.2
            elif negative_matches > positive_matches:
                impact = -(negative_matches - positive_matches) * 0.2
            else:
                impact = 0.0
            
            # Weight by vulnerability
            vulnerability = ego_dimensions.vulnerability_weights.get(dimension, 0.1)
            weighted_impact = impact * vulnerability
            
            impacts[dimension] = weighted_impact
        
        logger.debug(f"Calculated dimension impacts: {impacts}")
        return impacts
    
    def calculate_aggregate_pain(
        self, 
        dimension_impacts: Dict[str, float],
        ego_dimensions: EgoDimensions
    ) -> float:
        """
        Aggregate dimension impacts into single pain score.
        
        Args:
            dimension_impacts: Dictionary of dimension -> impact
            ego_dimensions: Ego dimensions state
            
        Returns:
            Aggregate pain score (-1 to +1)
        """
        total_impact = 0.0
        total_weight = 0.0
        
        for dimension, impact in dimension_impacts.items():
            weight = ego_dimensions.vulnerability_weights.get(dimension, 0.1)
            total_impact += impact * weight
            total_weight += weight
        
        # Normalize
        if total_weight > 0:
            aggregate = total_impact / total_weight
        else:
            aggregate = 0.0
        
        # Apply ego strength (stronger ego = less affected)
        # Strong ego reduces impact by up to 30%
        resilience_factor = 1.0 - (ego_dimensions.ego_strength * 0.3)
        final_pain = aggregate * resilience_factor
        
        # Clamp to [-1, 1]
        final_pain = max(-1.0, min(1.0, final_pain))
        
        logger.debug(f"Aggregate pain: {final_pain} (raw: {aggregate}, resilience: {resilience_factor})")
        return final_pain
    
    def get_most_affected_dimension(
        self, 
        dimension_impacts: Dict[str, float]
    ) -> Tuple[str, float]:
        """
        Find the dimension with the highest absolute impact.
        
        Args:
            dimension_impacts: Dictionary of dimension -> impact
            
        Returns:
            Tuple of (dimension_name, impact_value)
        """
        if not dimension_impacts:
            return ("identity", 0.0)
        
        most_affected = max(
            dimension_impacts.items(), 
            key=lambda x: abs(x[1])
        )
        
        return most_affected

