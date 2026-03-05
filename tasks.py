# tasks.py
from crewai import Task
from typing import List
from models import ProgrammeInput, EvaluationPlan

class EvaluationPlanTasks:
    """Define all tasks for the evaluation plan creation process"""
    
    def create_analysis_task(self, agent, programme_input: ProgrammeInput) -> Task:
        """Task for programme analysis"""
        return Task(
            description=f"""
            Analyze the following programme and produce a detailed specification:
            
            Programme Type: {programme_input.programme_type.value}
            Programme Name: {programme_input.programme_name}
            Description: {programme_input.programme_description}
            Target Population: {programme_input.target_population}
            Context: {programme_input.context.value}
            Geographic Scope: {programme_input.geographic_scope}
            
            Your tasks:
            1. Identify core programme components and activities
            2. Develop a clear theory of change with inputs, activities, outputs, outcomes, and impact
            3. Specify key assumptions that need testing
            4. Identify potential unintended consequences to monitor
            5. Map the causal pathway from activities to protection outcomes (if applicable)
            
            Format the output as a structured JSON matching the programme_identification section.
            """,
            agent=agent,
            expected_output="A comprehensive programme analysis with theory of change"
        )
    
    def create_methodology_task(self, agent, programme_analysis: dict) -> Task:
        """Task for methodology design"""
        return Task(
            description=f"""
            Based on the programme analysis, design the core evaluation methodology:
            
            Programme Analysis: {programme_analysis}
            
            Your tasks:
            1. Recommend the most appropriate randomization design (justify your choice)
            2. Calculate required sample sizes using standard parameters (power=0.8, alpha=0.05)
            3. Specify unit of randomization and justify
            4. Define minimum detectable effect size (MDE) based on sector standards
            5. Anticipate methodological challenges and propose solutions
            
            Consider:
            - Ethical constraints in {programme_analysis.get('context')} context
            - Feasibility of randomization
            - Potential for contamination and how to address it
            
            Format output as JSON for the core_design section.
            """,
            agent=agent,
            expected_output="Detailed methodology design with sample size calculations"
        )
    
    def create_measurement_task(self, agent, programme_analysis: dict) -> Task:
        """Task for measurement framework"""
        return Task(
            description=f"""
            Develop a comprehensive measurement framework:
            
            Programme Outcomes from analysis: {programme_analysis.get('outcomes')}
            
            Your tasks:
            1. Select validated indicators for each outcome (prefer standard humanitarian indicators)
            2. Design survey modules with exact question wording
            3. Identify existing data sources that could be leveraged
            4. Specify data collection methods and frequency
            5. Create a measurement matrix linking indicators to outcomes
            
            Use the indicator library to find:
            - Food security indicators (FCS, CSI, HHS)
            - Mental health measures (PHQ-9, PCL-5)
            - Protection outcomes (safety perceptions, incident reports)
            - Economic measures (consumption, assets)
            
            Format output as JSON for measurement_framework section.
            """,
            agent=agent,
            expected_output="Complete measurement framework with survey instruments"
        )
    
    def create_ethics_task(self, agent, context_info: dict) -> Task:
        """Task for ethics and operational planning"""
        return Task(
            description=f"""
            Develop ethics and operational plan for context: {context_info}
            
            Your tasks:
            1. Identify key ethical risks and mitigation strategies
            2. Develop informed consent protocols
            3. Plan for vulnerable population protections
            4. Anticipate operational challenges (attrition, security, access)
            5. Create contingency plans for each risk
            
            Reference ethical guidelines and past case studies.
            
            Format output as JSON for ethical_operational_plan section.
            """,
            agent=agent,
            expected_output="Comprehensive ethics and operations plan"
        )
    
    def create_economics_task(self, agent, programme_budget: float) -> Task:
        """Task for cost analysis"""
        return Task(
            description=f"""
            Integrate cost-effectiveness analysis with budget: {programme_budget}
            
            Your tasks:
            1. Design cost data collection protocol
            2. Specify cost categories to track
            3. Define cost-effectiveness metrics
            4. Plan for cost comparison with alternatives
            5. Create budget for the evaluation itself
            
            Format output as JSON for analysis_learning_plan section.
            """,
            agent=agent,
            expected_output="Cost analysis framework and evaluation budget"
        )
    
    def create_synthesis_task(self, agent, all_inputs: List[dict]) -> Task:
        """Task for synthesizing all components"""
        return Task(
            description=f"""
            Synthesize all evaluation components into a coherent plan:
            
            Inputs from all agents: {all_inputs}
            
            Your tasks:
            1. Integrate all sections into a unified narrative
            2. Ensure consistency across sections
            3. Check that all research questions are addressed
            4. Add executive summary and introduction
            5. Format according to the template structure
            
            Format output as complete EvaluationPlan JSON.
            """,
            agent=agent,
            expected_output="Complete integrated evaluation plan"
        )
    
    def create_qa_task(self, agent, draft_plan: dict) -> Task:
        """Final quality assurance task"""
        return Task(
            description=f"""
            Review the draft evaluation plan for quality and completeness:
            
            Draft Plan: {draft_plan}
            
            Quality checklist:
            ✓ Is the theory of change logical and complete?
            ✓ Are sample sizes adequate and justified?
            ✓ Are indicators validated and appropriate?
            ✓ Are ethical risks adequately addressed?
            ✓ Is the plan operationally feasible?
            ✓ Are cost considerations included?
            ✓ Is the plan aligned with humanitarian principles?
            
            Provide feedback and request revisions if needed.
            If approved, output the final evaluation plan.
            """,
            agent=agent,
            expected_output="Quality-assured final evaluation plan",
            output_pydantic=EvaluationPlan
        )