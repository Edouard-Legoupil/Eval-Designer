# agents.py
from crewai import Agent
from crewai.tools import BaseTool
import os
# Load environment variables from a .env file.
from dotenv import load_dotenv
load_dotenv()

from tools import SampleSizeCalculator, IndicatorLibrary

# Placeholder tools to satisfy CrewAI's BaseTool requirement
class SurveyDesigner(BaseTool):
    name: str = "Survey Designer"
    description: str = "Generate survey modules based on selected indicators"
    def _run(self, indicators: str, population: str) -> str:
        return "Survey designed."

class EthicsChecklist(BaseTool):
    name: str = "Ethics Checklist"
    description: str = "Review ethical guidelines"
    def _run(self, context: str) -> str:
        return "Ethics reviewed."

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Assess operational risks"
    def _run(self, context: str) -> str:
        return "Risks assessed."

class CEACalculator(BaseTool):
    name: str = "CEA Calculator"
    description: str = "Cost-effectiveness analysis calculator"
    def _run(self, budget: float) -> str:
        return "CEA calculated."

class QualityChecklist(BaseTool):
    name: str = "Quality Checklist"
    description: str = "Quality assurance checklist"
    def _run(self, plan: str) -> str:
        return "Quality assured."


#--- Azure OpenAI Configuration ---
# Third-Party Libraries
from langchain_openai import AzureChatOpenAI

# Set environment variables required by the Azure OpenAI client.
os.environ["AZURE_API_TYPE"] = "azure"
os.environ["AZURE_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["AZURE_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
os.environ["AZURE_DEPLOYMENT_NAME"] = os.getenv("AZURE_DEPLOYMENT_NAME")

# Validate that all required environment variables are set.
required_vars = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_VERSION",
    "AZURE_DEPLOYMENT_NAME"
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables for LLM: {', '.join(missing_vars)}")

# --- Language Model Initialization ---

# Initialize the AzureChatOpenAI language model.
# This object will be used by the CrewAI agents to interact with the Azure OpenAI service.
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    model=f"azure/{os.getenv('AZURE_DEPLOYMENT_NAME')}",
    max_retries=3,
    timeout=30
)


class EvaluationPlanAgents:
    """Factory class for creating specialized evaluation agents"""
    
    def __init__(self):
        self.llm = llm
        
        # Knowledge base references
        self.standard_indicators = self._load_indicators()
        self.ethical_guidelines = self._load_ethical_guidelines()
        self.case_studies = self._load_case_studies()
        
    def _load_indicators(self):
        return {}
        
    def _load_ethical_guidelines(self):
        return {}
        
    def _load_case_studies(self):
        return []
    
    def create_orchestrator(self) -> Agent:
        """Main orchestrator that coordinates the entire process"""
        return Agent(
            role="Evaluation Plan Orchestrator",
            goal="Coordinate all specialized agents to create a coherent, high-quality evaluation plan",
            backstory="""You are a senior evaluation methodology expert with 15+ years of experience 
            designing impact evaluations for humanitarian programmes. You excel at breaking down complex 
            evaluation needs into specialized tasks and synthesizing inputs from multiple experts into 
            a cohesive plan.""",
            tools=[],  # Add relevant tools here
            allow_delegation=True,
            verbose=True,
            llm=self.llm
        )
    
    def create_programme_analyst(self) -> Agent:
        """Agent specialized in understanding programme models"""
        return Agent(
            role="Programme Analyst",
            goal="Accurately specify the programme model and theory of change",
            backstory="""You are a humanitarian programme specialist with deep knowledge of intervention 
            models across sectors. You've worked with UN agencies, NGOs, and governments to design and 
            implement programmes. You can quickly identify core components, assumptions, and causal pathways.""",
            tools=[],  # Add programme database tools
            llm=self.llm
        )
    
    def create_methodology_specialist(self) -> Agent:
        """Agent specialized in evaluation design and sampling"""
        return Agent(
            role="Methodology Specialist",
            goal="Design rigorous and feasible evaluation methodologies",
            backstory="""You are a statistician and impact evaluation methodologist affiliated with J-PAL. 
            You have designed dozens of randomized evaluations in challenging contexts. You can calculate 
            sample sizes, recommend randomization strategies, and anticipate methodological challenges.""",
            tools=[SampleSizeCalculator()],  # Custom tool
            llm=self.llm
        )
    
    def create_measurement_specialist(self) -> Agent:
        """Agent specialized in measurement and indicators"""
        return Agent(
            role="Measurement & Data Specialist",
            goal="Develop robust measurement frameworks using standard indicators",
            backstory="""You are a survey methodologist and M&E expert with expertise in selecting and 
            adapting validated instruments. You maintain a comprehensive database of standard indicators 
            across humanitarian sectors and know how to leverage existing data sources.""",
            tools=[IndicatorLibrary(), SurveyDesigner()],
            llm=self.llm
        )
    
    def create_ethics_operations_specialist(self) -> Agent:
        """Agent specialized in ethics and operational feasibility"""
        return Agent(
            role="Ethics & Operations Specialist",
            goal="Ensure ethical soundness and operational feasibility",
            backstory="""You are a humanitarian protection specialist with deep expertise in ethical 
            research in fragile contexts. You've managed operations in conflict zones and know how to 
            anticipate and mitigate risks while ensuring research integrity.""",
            tools=[EthicsChecklist(), RiskAssessmentTool()],
            llm=self.llm
        )
    
    def create_economics_specialist(self) -> Agent:
        """Agent specialized in cost-effectiveness"""
        return Agent(
            role="Economics & Cost Specialist",
            goal="Integrate cost analysis and resource planning",
            backstory="""You are a development economist specializing in cost-effectiveness analysis. 
            You help organizations understand not just if programmes work, but at what cost and whether 
            they represent good value for money.""",
            tools=[CEACalculator()],
            llm=self.llm
        )
    
    def create_quality_assurance_specialist(self) -> Agent:
        """Agent for final review and quality control"""
        return Agent(
            role="Quality Assurance Specialist",
            goal="Ensure final plan meets highest standards of quality and completeness",
            backstory="""You are a senior reviewer at a leading research organization. You've reviewed 
            hundreds of evaluation designs and know exactly what makes a plan fundable, ethical, and 
            scientifically rigorous. You provide constructive feedback and ensure no gaps remain.""",
            tools=[QualityChecklist()],
            llm=self.llm
        )
    
    # Custom tools 
    def sample_size_calculator(self, params):
        """Calculate required sample sizes based on inputs"""
        pass
    
    def indicator_library(self, sector, outcome):
        """Return validated indicators for given sector and outcome"""
        pass
    
    def survey_designer(self, indicators, population):
        """Generate survey modules based on selected indicators"""
        pass