"""
module_08_projects/project_04_business_automator/workflow_agents.py
--------------------------------------------------------------------
Agent definitions for the Business Automator.

Four-agent pipeline:
1. TaskAnalyzer   — understands requirements, sets standards
2. DraftWriter    — produces the first complete draft
3. QualityReviewer — checks against requirements, tone, completeness
4. FinalEditor    — polishes language, formatting, and produces final output

The pipeline uses GroupChat with 'round_robin' selection for
deterministic execution, then switches to 'auto' for the review phase.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config


def create_task_analyzer(llm_config: dict) -> AssistantAgent:
    """
    Analyzes the business task, identifies key success criteria,
    and sets the standard for what a great output looks like.
    """
    return AssistantAgent(
        name="TaskAnalyzer",
        system_message="""You are an expert business consultant who analyzes tasks.

When given a business task:
1. Identify the PRIMARY goal (what is this trying to achieve?)
2. List the TARGET AUDIENCE and what they care about
3. Define SUCCESS CRITERIA (how do we know the output is good?)
4. Flag any CONSTRAINTS or RISKS to avoid
5. Give the DraftWriter specific guidance on how to approach this

Be concise (bullet points preferred). After your analysis, end with:
'ANALYSIS_COMPLETE — DraftWriter, please proceed.'

Do NOT write the draft yourself. Your job is analysis only.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_draft_writer(llm_config: dict) -> AssistantAgent:
    """
    Produces the first complete, polished draft of the business output.
    """
    return AssistantAgent(
        name="DraftWriter",
        system_message="""You are a senior business writer with 15 years of experience.
You write emails, reports, proposals, meeting agendas, and business documents.

Your writing is:
- Clear and direct (no corporate jargon)
- Audience-appropriate
- Structured logically
- Action-oriented

When the TaskAnalyzer has finished, write a COMPLETE first draft.
Do not summarize or outline — write the actual, full document.

After your draft, end with:
'DRAFT_COMPLETE — QualityReviewer, please review.'""",
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
    )


def create_quality_reviewer(llm_config: dict) -> AssistantAgent:
    """
    Reviews the draft against requirements, tone, and quality standards.
    Either approves or provides specific revision instructions.
    """
    return AssistantAgent(
        name="QualityReviewer",
        system_message="""You are a meticulous quality assurance expert for business communications.

Review the draft against:
1. COMPLETENESS — Does it address ALL requirements?
2. TONE — Does it match the requested tone exactly?
3. CLARITY — Is every sentence clear and purposeful?
4. STRUCTURE — Is it logically organized?
5. LENGTH — Is it appropriately concise or detailed?
6. PROFESSIONALISM — Would this pass executive review?

If the draft needs revision:
- List SPECIFIC issues (not vague feedback)
- Tell DraftWriter exactly what to change
- Say: 'REVISION_NEEDED — DraftWriter, please revise:'

If the draft meets all standards:
- Give brief praise (1 sentence)
- Say: 'QUALITY_APPROVED — FinalEditor, please polish.'

Maximum 1 revision round.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
    )


def create_final_editor(llm_config: dict) -> AssistantAgent:
    """
    Final polish pass: perfects language, formatting, and presentation.
    Produces the deliverable output.
    """
    return AssistantAgent(
        name="FinalEditor",
        system_message="""You are a final-pass editor who transforms good drafts into excellent deliverables.

Your job:
1. Fix any grammatical or stylistic issues
2. Ensure consistent formatting (headings, bullets, spacing)
3. Strengthen the opening and closing
4. Remove redundancy
5. Ensure the document looks ready to send/present

Output the FINAL VERSION in clean markdown format.

Begin your output with: '## FINAL OUTPUT'
Then the complete, polished document.
End with: 'TASK_COMPLETE'""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_admin_proxy() -> UserProxyAgent:
    """Admin proxy that orchestrates the pipeline without LLM."""
    return UserProxyAgent(
        name="Admin",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "TASK_COMPLETE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )


def build_agent_team(provider: str = None) -> dict:
    """
    Creates and returns the full agent team.

    Returns:
        dict with keys: admin, analyzer, writer, reviewer, editor
    """
    llm_config = get_llm_config(provider=provider, temperature=0.6)

    return {
        "admin": create_admin_proxy(),
        "analyzer": create_task_analyzer(llm_config),
        "writer": create_draft_writer(llm_config),
        "reviewer": create_quality_reviewer(llm_config),
        "editor": create_final_editor(llm_config),
    }
