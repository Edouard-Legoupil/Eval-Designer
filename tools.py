# tools.py
from crewai.tools import BaseTool
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats

class SampleSizeCalculator(BaseTool):
    """Tool for calculating sample sizes for RCTs"""
    
    name: str = "Sample Size Calculator"
    description: str = "Calculate required sample sizes for randomized evaluations"
    
    def _run(self, 
             mde: float = 0.2, 
             alpha: float = 0.05, 
             power: float = 0.8,
             icc: float = 0.05,  # Intra-cluster correlation
             cluster_size: int = 30,
             n_arms: int = 2) -> Dict[str, Any]:
        """
        Calculate required sample sizes
        
        Args:
            mde: Minimum detectable effect size (in standard deviations)
            alpha: Significance level
            power: Statistical power
            icc: Intra-cluster correlation
            cluster_size: Average cluster size
            n_arms: Number of treatment arms
        """
        # Basic sample size for individual randomization
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n_per_arm = int(2 * ((z_alpha + z_beta) ** 2) / (mde ** 2))
        
        # Adjust for clustering
        design_effect = 1 + (cluster_size - 1) * icc
        n_per_arm_clustered = int(n_per_arm * design_effect)
        
        # Total clusters needed
        clusters_needed = int(np.ceil((n_per_arm_clustered * n_arms) / cluster_size))
        
        return {
            "n_per_arm_individual": n_per_arm,
            "n_per_arm_clustered": n_per_arm_clustered,
            "total_sample_size": n_per_arm_clustered * n_arms,
            "clusters_needed": clusters_needed,
            "design_effect": round(design_effect, 2),
            "assumptions": {
                "mde": mde,
                "alpha": alpha,
                "power": power,
                "icc": icc,
                "cluster_size": cluster_size
            }
        }

class IndicatorLibrary(BaseTool):
    """Database of validated humanitarian indicators"""
    
    name: str = "Indicator Library"
    description: str = "Retrieve validated indicators for humanitarian sectors"
    
    def _run(self, sector: str, outcome: str) -> List[Dict[str, Any]]:
        """Return indicators for given sector and outcome"""
        
        indicator_db = {
            "food_security": {
                "consumption": [
                    {"name": "Food Consumption Score (FCS)", 
                     "type": "continuous", 
                     "validation": "WFP standard",
                     "questions": ["Over the last 7 days, how many days did your household eat..."]},
                    {"name": "Coping Strategies Index (CSI)", 
                     "type": "continuous", 
                     "validation": "WFP/FAO standard",
                     "questions": ["In the past 7 days, did your household..."]}
                ],
                "hunger": [
                    {"name": "Household Hunger Scale (HHS)", 
                     "type": "categorical", 
                     "validation": "FANTA validated",
                     "questions": ["In the past 30 days, was there ever no food to eat..."]}
                ]
            },
            "mental_health": {
                "depression": [
                    {"name": "PHQ-9", 
                     "type": "continuous", 
                     "validation": "Clinically validated",
                     "questions": ["Over the last 2 weeks, how often have you been bothered by..."]}
                ],
                "ptsd": [
                    {"name": "PCL-5", 
                     "type": "continuous", 
                     "validation": "Clinically validated",
                     "questions": ["In the past month, how much were you bothered by..."]}
                ]
            },
            "protection": {
                "safety": [
                    {"name": "Perceived Safety Scale", 
                     "type": "continuous", 
                     "validation": "Adapted from IASC guidelines",
                     "questions": ["How safe do you feel in your current location?"]},
                    {"name": "Incidence of Violence", 
                     "type": "binary", 
                     "validation": "Protection cluster standard",
                     "questions": ["In the past 30 days, have you experienced..."]}
                ]
            }
        }
        
        return indicator_db.get(sector, {}).get(outcome, [])