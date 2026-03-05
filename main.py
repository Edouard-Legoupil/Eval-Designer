# main.py
import streamlit as st
from crew import EvaluationPlanCrew
from models import ProgrammeInput, ProgrammeType, ContextType
import json
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Humanitarian Evaluation Plan Generator",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Humanitarian Evaluation Plan Generator")
    st.markdown("""
    This tool helps you create predesigned evaluation plans for standardised humanitarian programmes,
    based on J-PAL's Learning Agenda for the Humanitarian Initiative.
    """)
    
    # Sidebar for input
    with st.sidebar:
        st.header("Programme Information")
        
        programme_type = st.selectbox(
            "Programme Type",
            options=[pt.value for pt in ProgrammeType],
            index=0
        )
        
        programme_name = st.text_input("Programme Name", value="Community-Based MHPSS for Adolescent Girls")
        programme_description = st.text_area(
            "Programme Description", 
            value="8-week group-based psychosocial support program for adolescent girls aged 13-17 in displacement settings, focusing on coping skills and social support.", 
            height=100
        )
        target_population = st.text_input("Target Population", value="Adolescent girls in IDP camps")
        
        context = st.selectbox(
            "Context",
            options=[ctx.value for ctx in ContextType],
            index=0  # Should be Displacement if possible, default to 0
        )
        
        geographic_scope = st.text_input("Geographic Scope", value="3 camps in XYZ region")
        estimated_beneficiaries = st.number_input("Estimated Beneficiaries", min_value=1, value=1500)
        duration_months = st.number_input("Duration (months)", min_value=1, value=6)
        
        budget_constraint = st.number_input(
            "Budget Constraint (USD, optional)",
            min_value=0.0,
            value=500000.0
        )
        
        existing_data_sources = st.text_area(
            "Existing Data Sources (comma-separated)",
            value="camp registration data, health post records",
            help="e.g., 'HMIS data, mobile operator data, previous surveys'"
        )
        
        specific_questions = st.text_area(
            "Specific Research Questions (one per line)",
            value="Does the program reduce symptoms of anxiety and depression?\nDoes it improve social support networks?\nAre effects sustained 6 months post-program?",
            help="Any specific questions you want the evaluation to answer"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Generate Evaluation Plan", type="primary", use_container_width=True):
            with st.spinner("Generating evaluation plan... This may take a few minutes."):
                try:
                    # Create programme input
                    programme_input = ProgrammeInput(
                        programme_type=ProgrammeType(programme_type),
                        programme_name=programme_name,
                        programme_description=programme_description,
                        target_population=target_population,
                        context=ContextType(context),
                        geographic_scope=geographic_scope,
                        estimated_beneficiaries=estimated_beneficiaries,
                        duration_months=duration_months,
                        budget_constraint=budget_constraint if budget_constraint > 0 else None,
                        existing_data_sources=[x.strip() for x in existing_data_sources.split(",") if x.strip()],
                        specific_questions=[x.strip() for x in specific_questions.split("\n") if x.strip()]
                    )
                    
                    # Initialize crew and generate plan
                    import contextlib
                    import io
                    
                    log_output = io.StringIO()
                    with st.expander("🕵️ Agent Process Logs", expanded=True):
                        log_area = st.empty()
                        with contextlib.redirect_stdout(log_output):
                            crew = EvaluationPlanCrew()
                            evaluation_plan = crew.create_plan(programme_input)
                            # Periodically update the log area (though this is simple, for more complex real-time we'd need a separate thread)
                            log_area.code(log_output.getvalue())
                    
                    # Store in session state
                    st.session_state['evaluation_plan'] = evaluation_plan
                    
                    st.success("✅ Evaluation plan generated successfully!")
                    
                except Exception as e:
                    # Show logs even on error
                    if 'log_output' in locals():
                        with st.expander("🕵️ Agent Process Logs (on Error)", expanded=True):
                            st.code(log_output.getvalue())
                    st.error(f"Error generating plan: {str(e)}")
    
    with col2:
        if 'evaluation_plan' in st.session_state:
            # Download buttons
            plan_json = json.dumps(st.session_state['evaluation_plan'].dict(), indent=2)
            
            st.download_button(
                label="📥 Download JSON",
                data=plan_json,
                file_name=f"evaluation_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.download_button(
                label="📄 Download Markdown",
                data=convert_to_markdown(st.session_state['evaluation_plan']),
                file_name=f"evaluation_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # Display the plan if it exists
    if 'evaluation_plan' in st.session_state:
        display_evaluation_plan(st.session_state['evaluation_plan'])

def convert_to_markdown(plan):
    """Convert evaluation plan to markdown format"""
    plan_dict = plan.dict(by_alias=True)
    md = f"# Evaluation Plan: {plan_dict.get('programme_identification', {}).get('programme_name', 'Unnamed Programme')}\n\n"
    
    if plan.executive_summary:
        md += f"## Executive Summary\n{plan.executive_summary}\n\n"
        
    intro = plan_dict.get('introduction', plan_dict.get('Introduction', {}))
    if intro:
        md += "## Introduction\n"
        if isinstance(intro, dict):
            for k, v in intro.items():
                md += f"**{k.replace('_', ' ').title()}:** {v}\n\n"
        else:
            md += f"{intro}\n\n"

    # Add other sections
    sections = {
        "Programme Identification": ['programme_identification', 'ProgrammeIdentification'],
        "Research Questions": ['research_questions', 'ResearchQuestions'],
        "Core Evaluation Design": ['core_design', 'CoreDesign'],
        "Measurement Framework": ['measurement_framework', 'MeasurementFramework'],
        "Ethical & Operational Plan": ['ethical_operational_plan', 'EthicalAndOperationalPlan'],
        "Analysis & Learning Plan": ['analysis_learning_plan', 'AnalysisAndLearningPlan'],
        "Quality Assurance": ['quality_assurance', 'QualityAssurance']
    }
    
    for title, keys in sections.items():
        data = None
        for key in keys:
            if plan_dict.get(key):
                data = plan_dict[key]
                break
        
        if data:
            md += f"## {title}\n"
            md += f"```json\n{json.dumps(data, indent=2)}\n```\n\n"
            
    return md

def safe_metric_value(value):
    """Ensure the value passed to st.metric is a string or number"""
    if isinstance(value, dict):
        if 'unit' in value: return str(value['unit'])
        if 'value' in value: return str(value['value'])
        if 'type' in value: return str(value['type'])
        if 'total' in value: return str(value['total'])
        return str(next(iter(value.values())))
    return value
def safe_get(data, *keys, default=None):
    """Deeply get value from nested dicts/objects with multiple key options, case-insensitive"""
    if not data or not isinstance(data, dict):
        return default
    
    # Create a mapping of lowercase keys to original keys
    lower_map = {k.lower().replace("_", ""): k for k in data.keys()}
    
    for key in keys:
        # Check direct case-sensitive match first
        if key in data and data[key] is not None:
            return data[key]
        
        # Check case-insensitive match
        search_key = key.lower().replace("_", "")
        if search_key in lower_map:
            actual_key = lower_map[search_key]
            if data[actual_key] is not None:
                return data[actual_key]
                
    return default

def render_section(title, data, renderer_func):
    """Safely render a section with a fallback to JSON if it fails"""
    st.header(title)
    if not data:
        st.info(f"No data available for {title}")
        return
    
    try:
        renderer_func(data)
    except Exception as e:
        st.warning(f"Could not format {title} perfectly. Showing raw data instead.")
        st.json(data)

def markdown_from_dict(data, level=3):
    """Recursively convert a dictionary to markdown"""
    md = ""
    prefix = "#" * level
    
    if isinstance(data, dict):
        for k, v in data.items():
            k_clean = k.replace("_", " ").title()
            if isinstance(v, (dict, list)):
                md += f"{prefix} {k_clean}\n"
                md += markdown_from_dict(v, level + 1)
            else:
                md += f"**{k_clean}:** {v}\n\n"
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                md += markdown_from_dict(item, level)
            else:
                md += f"- {item}\n"
        md += "\n"
    else:
        md += f"{data}\n\n"
    return md

def convert_to_markdown(plan):
    """Convert evaluation plan to markdown format"""
    plan_dict = plan.dict(by_alias=True)
    
    # Use robust name fetching
    prog_id = safe_get(plan_dict, 'programme_identification', 'ProgrammeIdentification', 'programme_description', default={})
    prog_name = safe_get(prog_id, 'programme_name', 'ProgrammeName', default="Unnamed Programme")
    
    md = f"# Evaluation Plan: {prog_name}\n\n"
    
    exec_summary = getattr(plan, 'executive_summary', None)
    if exec_summary:
        md += "## Executive Summary\n"
        md += markdown_from_dict(exec_summary, 3)
        md += "\n"
        
    intro = safe_get(plan_dict, 'introduction', 'Introduction', default={})
    if intro:
        md += "## Introduction\n"
        md += markdown_from_dict(intro, 3)
        md += "\n"

    sections = {
        "Programme Identification": ['programme_identification', 'ProgrammeIdentification', 'programme_description'],
        "Research Questions": ['research_questions', 'ResearchQuestions'],
        "Core Evaluation Design": ['core_design', 'CoreDesign'],
        "Measurement Framework": ['measurement_framework', 'MeasurementFramework'],
        "Ethical & Operational Plan": ['ethical_operational_plan', 'EthicalAndOperationalPlan'],
        "Analysis & Learning Plan": ['analysis_learning_plan', 'AnalysisAndLearningPlan'],
        "Quality Assurance": ['quality_assurance', 'QualityAssurance']
    }
    
    for title, keys in sections.items():
        data = safe_get(plan_dict, *keys)
        if data:
            md += f"## {title}\n"
            md += markdown_from_dict(data, 3)
            md += "\n"
            
    return md
def display_evaluation_plan(plan):
    """Display the evaluation plan in a formatted way"""
    plan_dict = plan.dict(by_alias=True)
    
    # Create tabs for different sections
    tabs = st.tabs([
        "📖 Summary",
        "📋 Programme ID", 
        "❓ Research Questions", 
        "📊 Core Design",
        "📏 Measurement",
        "⚖️ Ethics & Ops",
        "📈 Analysis",
        "✅ QA"
    ])
    
    with tabs[0]:
        st.header("Executive Summary & Introduction")
        exec_summary = getattr(plan, 'executive_summary', None)
        if exec_summary:
            st.subheader("Executive Summary")
            if isinstance(exec_summary, dict):
                for k, v in exec_summary.items():
                    st.write(f"**{k.replace('_', ' ').title()}:** {v}")
            else:
                st.write(exec_summary)
        
        intro = safe_get(plan_dict, 'introduction', 'Introduction', default={})
        if intro:
            st.subheader("Introduction")
            if isinstance(intro, dict):
                for k, v in intro.items():
                    st.write(f"**{k.replace('_', ' ').title()}:** {v}")
            else:
                st.write(intro)

    with tabs[1]:
        def render_id(prog_id):
            name = safe_get(prog_id, 'programme_name', 'ProgrammeName', default='Unnamed Programme')
            st.subheader(name)
            desc = safe_get(prog_id, 'description', 'Description', default='No description provided.')
            st.write(desc)
            
            col1, col2 = st.columns(2)
            with col1:
                p_type = safe_get(prog_id, 'programme_type', 'ProgrammeType', default='N/A')
                st.info(f"**Type:** {p_type}")
                context = safe_get(prog_id, 'context', 'Context', default='N/A')
                st.info(f"**Context:** {context}")
            with col2:
                target = safe_get(prog_id, 'target_population', 'TargetPopulation', default='N/A')
                st.info(f"**Target:** {target}")
                scope = safe_get(prog_id, 'geographic_scope', 'GeographicScope', default='N/A')
                st.info(f"**Scope:** {scope}")
            
            toc = safe_get(prog_id, 'theory_of_change', 'TheoryOfChange', default=plan_dict.get('theory_of_change'))
            if toc:
                st.subheader("Theory of Change")
                cols = st.columns(len(toc))
                for i, (key, value) in enumerate(toc.items()):
                    with cols[i]:
                        st.markdown(f"**{key.title()}**")
                        if isinstance(value, list):
                            for item in value:
                                st.write(f"- {item}")
                        else:
                            st.write(value)

        prog_id = safe_get(plan_dict, 'programme_identification', 'ProgrammeIdentification', 'programme_description', default={})
        render_section("Programme Identification", prog_id, render_id)

    with tabs[2]:
        def render_rqs(rqs):
            if isinstance(rqs, dict):
                for category, questions in rqs.items():
                    with st.expander(category.replace('_', ' ').title(), expanded=True):
                        if isinstance(questions, list):
                            for q in questions:
                                st.write(f"❓ {q}")
                        else:
                            st.write(questions)
            else:
                st.write(rqs)

        rqs = safe_get(plan_dict, 'research_questions', 'ResearchQuestions', default={})
        render_section("Research Questions", rqs, render_rqs)
    
    with tabs[3]:
        def render_design(design):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Methodology", safe_metric_value(safe_get(design, 'design_type', 'methodology', 'Methodology', default='N/A')))
                st.metric("Unit of Randomization", safe_metric_value(safe_get(design, 'unit_of_randomization', 'UnitOfRandomization', default='N/A')))
            with col2:
                sample = safe_get(design, 'sample_size', 'SampleSize', default={})
                total_n = safe_get(sample, 'total_participants', 'total_sample_size', 'TotalParticipants', default='N/A')
                st.metric("Total Sample Size", safe_metric_value(total_n))
                mde = safe_get(sample, 'minimum_detectable_effect_size', 'mde', 'MinimumDetectableEffectSize', default='N/A')
                st.metric("MDE", safe_metric_value(mde))
            with col3:
                power = safe_get(sample, 'statistical_power', 'power', 'StatisticalPower', default='N/A')
                st.metric("Power", safe_metric_value(power))
                alpha = safe_get(sample, 'significance_level', 'alpha', 'SignificanceLevel', default='N/A')
                st.metric("Alpha", safe_metric_value(alpha))
            
            justification = safe_get(design, 'randomization_justification', 'RandomizationJustification')
            if justification:
                st.subheader("Justification")
                st.write(justification)
                
            challenges = safe_get(design, 'methodological_challenges_and_mitigations', 'MethodologicalChallengesAndMitigations')
            if challenges:
                st.subheader("Challenges & Mitigations")
                for issue, solution in challenges.items():
                    st.warning(f"**{issue}:** {solution}")

        design = safe_get(plan_dict, 'core_design', 'CoreDesign', default={})
        render_section("Core Evaluation Design", design, render_design)
    
    with tabs[4]:
        def render_meas(meas):
            st.subheader("Indicators")
            indicators = safe_get(meas, 'indicators', 'Indicators', default={})
            if isinstance(indicators, dict):
                for cat, items in indicators.items():
                    st.write(f"**{cat.title()}:** {', '.join(items) if isinstance(items, list) else items}")
                
            st.subheader("Data Collection Methods")
            methods = safe_get(meas, 'data_collection_methods', 'DataCollectionMethods', default={})
            if isinstance(methods, dict):
                for method, detail in methods.items():
                    st.write(f"- **{method.replace('_', ' ').title()}:** {detail}")

        meas = safe_get(plan_dict, 'measurement_framework', 'MeasurementFramework', default={})
        render_section("Measurement Framework", meas, render_meas)

    with tabs[5]:
        def render_ethics(ethics):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Ethical Risks")
                risks = safe_get(ethics, 'ethical_risks', 'EthicalRisks', default=[])
                for risk in risks:
                    st.error(risk)
            with col2:
                st.subheader("Mitigation Strategies")
                strats = safe_get(ethics, 'mitigation_strategies', 'MitigationStrategies', default=[])
                for strat in strats:
                    st.success(strat)
                    
            with st.expander("Operational Challenges"):
                challenges = safe_get(ethics, 'anticipated_operational_challenges', 'AnticipatedOperationalChallenges', default={})
                if isinstance(challenges, dict):
                    for challenge, detail in challenges.items():
                        st.write(f"⚠️ **{challenge.replace('_', ' ').title()}:** {detail}")

        ethics = safe_get(plan_dict, 'ethical_operational_plan', 'EthicalAndOperationalPlan', 'ethical_and_operational_plan', default={})
        render_section("Ethics & Operational Plan", ethics, render_ethics)
    
    with tabs[6]:
        def render_analysis(analysis):
            st.subheader("Cost-Effectiveness Metrics")
            metrics = safe_get(analysis, 'cost_effectiveness_metrics', 'CostEffectivenessMetrics', default={})
            if isinstance(metrics, dict):
                st.write(f"**Primary:** {safe_get(metrics, 'primary', 'PrimaryMetrics', 'primary_metrics', default='N/A')}")
                secondary = safe_get(metrics, 'secondary', 'SecondaryMetrics', 'secondary_metrics', default=[])
                for m in secondary:
                    st.write(f"- {m}")
            
            st.subheader("Evaluation Budget")
            budget = safe_get(analysis, 'evaluation_budget', 'EvaluationBudget', 'budget_for_evaluation_itself', default={})
            if isinstance(budget, dict):
                total_b = safe_get(budget, 'total', 'total_evaluation_budget', 'Total', default='N/A')
                if isinstance(total_b, (int, float)):
                    st.metric("Total Evaluation Budget", f"${total_b:,}")
                else:
                    st.metric("Total Evaluation Budget", safe_metric_value(total_b))
                
                breakdown = safe_get(budget, 'breakdown', 'Allocation', default={})
                if breakdown:
                    st.json(breakdown)

        analysis = safe_get(plan_dict, 'analysis_learning_plan', 'AnalysisAndLearningPlan', default={})
        render_section("Analysis & Learning Plan", analysis, render_analysis)

    with tabs[7]:
        st.header("Quality Assurance")
        qa = safe_get(plan_dict, 'quality_assurance', 'QualityAssurance', default={})
        status = safe_get(qa, 'status', 'Status', default='')
        approved = safe_get(qa, 'approved', 'Approved', default=False)
        if approved or status.lower() == 'approved':
            st.success("✅ Plan approved by QA")
        else:
            st.warning("⚠️ Plan pending QA approval")
        
        feedback = safe_get(qa, 'feedback', 'Feedback')
        if feedback:
            st.info(f"QA Feedback: {feedback}")
        
        with st.expander("View Full Raw JSON"):
            st.json(plan_dict)

if __name__ == "__main__":
    main()