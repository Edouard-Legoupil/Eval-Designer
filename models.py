# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ProgrammeType(str, Enum):
    CASH_TRANSFER = "cash_transfer"
    PSYCHOSOCIAL_SUPPORT = "psychosocial_support"
    FOOD_ASSISTANCE = "food_assistance"
    SHELTER = "shelter"
    PROTECTION = "protection"
    WASH = "wash"
    HEALTH = "health"
    EDUCATION = "education"

class ContextType(str, Enum):
    CONFLICT = "conflict"
    NATURAL_DISASTER = "natural_disaster"
    DISPLACEMENT = "displacement"
    URBAN = "urban"
    RURAL = "rural"
    CAMP = "camp"

class EvaluationPlan(BaseModel):
    """The complete evaluation plan structure"""
    model_config = {
        "extra": "allow",
        "populate_by_name": True
    }

    executive_summary: Optional[Any] = Field(None, alias="ExecutiveSummary")
    introduction: Optional[Any] = Field(None, alias="Introduction")
    
    programme_identification: Optional[Dict[str, Any]] = Field(None, alias="ProgrammeIdentification")
    research_questions: Optional[Dict[str, Any]] = Field(None, alias="ResearchQuestions")
    core_design: Optional[Dict[str, Any]] = Field(None, alias="CoreDesign")
    measurement_framework: Optional[Dict[str, Any]] = Field(None, alias="MeasurementFramework")
    ethical_operational_plan: Optional[Dict[str, Any]] = Field(
        None, 
        alias="EthicalAndOperationalPlan"
    )
    analysis_learning_plan: Optional[Dict[str, Any]] = Field(
        None, 
        alias="AnalysisAndLearningPlan"
    )
    quality_assurance: Optional[Dict[str, Any]] = Field(None, alias="QualityAssurance")

class ProgrammeInput(BaseModel):
    """User input for the evaluation plan"""
    programme_type: ProgrammeType
    programme_name: str
    programme_description: str
    target_population: str
    context: ContextType
    geographic_scope: str
    estimated_beneficiaries: int
    duration_months: int
    budget_constraint: Optional[float] = None
    existing_data_sources: Optional[List[str]] = None
    specific_questions: Optional[List[str]] = None