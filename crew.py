# crew.py
from crewai import Crew, Process
from agents import EvaluationPlanAgents
from tasks import EvaluationPlanTasks
from models import ProgrammeInput, EvaluationPlan
import json

class EvaluationPlanCrew:
    """Main crew for generating evaluation plans"""
    
    def __init__(self):
        self.agents_factory = EvaluationPlanAgents()
        self.tasks_factory = EvaluationPlanTasks()
    
    def create_plan(self, programme_input: ProgrammeInput) -> EvaluationPlan:
        """Generate a complete evaluation plan"""
        
        # Initialize agents
        orchestrator = self.agents_factory.create_orchestrator()
        programme_analyst = self.agents_factory.create_programme_analyst()
        methodology_specialist = self.agents_factory.create_methodology_specialist()
        measurement_specialist = self.agents_factory.create_measurement_specialist()
        ethics_specialist = self.agents_factory.create_ethics_operations_specialist()
        economics_specialist = self.agents_factory.create_economics_specialist()
        qa_specialist = self.agents_factory.create_quality_assurance_specialist()
        
        # Create tasks
        analysis_task = self.tasks_factory.create_analysis_task(
            programme_analyst, programme_input
        )
        
        methodology_task = self.tasks_factory.create_methodology_task(
            methodology_specialist, {}  # Will be filled with analysis output
        )
        
        measurement_task = self.tasks_factory.create_measurement_task(
            measurement_specialist, {}
        )
        
        ethics_task = self.tasks_factory.create_ethics_task(
            ethics_specialist, {"context": programme_input.context.value}
        )
        
        economics_task = self.tasks_factory.create_economics_task(
            economics_specialist, programme_input.budget_constraint
        )
        
        synthesis_task = self.tasks_factory.create_synthesis_task(
            orchestrator, []  # Will be filled with all outputs
        )
        
        qa_task = self.tasks_factory.create_qa_task(
            qa_specialist, {}
        )
        
        # Create the crew with sequential processing
        crew = Crew(
            agents=[
                programme_analyst,
                methodology_specialist,
                measurement_specialist,
                ethics_specialist,
                economics_specialist,
                orchestrator,
                qa_specialist
            ],
            tasks=[
                analysis_task,
                methodology_task,
                measurement_task,
                ethics_task,
                economics_task,
                synthesis_task,
                qa_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        # Parse and return the evaluation plan
        # result is a CrewOutput object, we need its raw string
        if hasattr(result, 'pydantic') and result.pydantic:
            return result.pydantic
            
        raw_output = result.raw if hasattr(result, 'raw') else str(result)
        
        # Parse JSON and handle potential nesting
        try:
            from json_repair import repair_json
            
            # Clean up raw_output if it contains markdown code blocks
            json_str = raw_output.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Use json_repair to fix common syntax errors (missing colons, quotes, etc.)
            repaired_json = repair_json(json_str)
            data = json.loads(repaired_json)
            
            # Advanced unwrapping: if the data is a dictionary with only one key, 
            # and that key looks like a wrapper (e.g., "evaluation_plan", "EvaluationPlan", etc.)
            if isinstance(data, dict) and len(data) == 1:
                key = next(iter(data))
                if key.lower().replace("_", "") == "evaluationplan":
                    data = data[key]
            
            return EvaluationPlan(**data)
        except Exception as e:
            # Fallback if even repair fails or validation fails
            raise ValueError(f"Failed to generate valid evaluation plan: {str(e)}\nRaw output was slightly malformed and repair failed.")