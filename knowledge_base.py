# knowledge_base.py
import json
from typing import Dict, Any

class KnowledgeBase:
    """Central knowledge repository for the agents"""
    
    def __init__(self):
        self.indicators = self._load_indicators()
        self.ethical_guidelines = self._load_ethical_guidelines()
        self.case_studies = self._load_case_studies()
        self.templates = self._load_templates()
    
    def _load_indicators(self) -> Dict[str, Any]:
        """Load standard humanitarian indicators"""
        return {
            "food_security": {
                "fcs": {
                    "name": "Food Consumption Score",
                    "type": "continuous",
                    "min": 0,
                    "max": 112,
                    "thresholds": {"poor": "0-28", "borderline": "28.5-42", "acceptable": "42+"}
                },
                "csi": {
                    "name": "Coping Strategies Index",
                    "type": "continuous",
                    "min": 0,
                    "max": 100
                }
            },
            "protection": {
                "safety_index": {
                    "name": "Perceived Safety Index",
                    "type": "likert_scale",
                    "range": "1-5"
                }
            }
        }
    
    def _load_ethical_guidelines(self) -> Dict[str, Any]:
        """Load ethical guidelines from key sources"""
        return {
            "do_no_harm": {
                "principle": "Ensure evaluation activities do not increase risk",
                "checklist": [
                    "Avoid collecting sensitive data that could endanger participants",
                    "Ensure referral pathways for participants in distress",
                    "Train enumerators on trauma-informed approaches"
                ]
            },
            "informed_consent": {
                "principle": "Obtain voluntary and informed consent",
                "checklist": [
                    "Use plain language appropriate for literacy levels",
                    "Document consent process",
                    "Allow participants to withdraw at any time"
                ]
            }
        }
    
    def _load_case_studies(self) -> list:
        """Load relevant case studies from J-PAL and others"""
        return [
            {
                "title": "Cash transfers in Niger",
                "context": "conflict",
                "design": "RCT with 3 arms",
                "outcome": "food security"
            }
        ]
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load evaluation templates"""
        return {
            "cash_transfer": {
                "typical_indicators": ["consumption", "food_security", "child_labor"],
                "typical_design": "cluster RCT",
                "sample_size_formula": "standard"
            },
            "psychosocial_support": {
                "typical_indicators": ["mental_health", "wellbeing", "social_support"],
                "typical_design": "individual RCT",
                "sample_size_formula": "small_effect"
            }
        }