"""
module_08_projects/project_04_business_automator/tasks.py
----------------------------------------------------------
Task definitions and loaders for the Business Automator.

Defines the task schema and provides sample tasks for
email drafting, report generation, and meeting planning.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class BusinessTask:
    """Represents a business automation task."""
    task_type: str          # "email", "report", "meeting", "proposal"
    description: str        # What needs to be done
    context: str            # Background information
    requirements: list[str] = field(default_factory=list)  # Must-haves
    tone: str = "professional"
    output_format: str = "markdown"
    max_length: Optional[int] = None  # Word limit if any


# ============================================================
# Sample Tasks (hardcoded for demo)
# ============================================================

EMAIL_TASK = BusinessTask(
    task_type="email",
    description="Draft a professional delay notification email to an enterprise client",
    context="""
    From: Sarah Chen, Product Manager at TechFlow Inc.
    To: Mr. James Whitfield, GlobalRetail Corp
    Situation: API integration is 2 weeks behind schedule.
    We discovered unexpected complexity in the client's legacy API during testing.
    """,
    requirements=[
        "Acknowledge the delay professionally",
        "Provide brief, honest explanation (no excuses)",
        "Describe concrete recovery actions",
        "Offer compensation: 2 weeks free post-launch support",
        "Propose a 30-minute call this week",
        "New delivery date: March 15, 2025",
    ],
    tone="professional, accountable, solution-focused",
    output_format="email with subject line",
    max_length=250,
)

REPORT_TASK = BusinessTask(
    task_type="report",
    description="Generate a Monthly Business Review (MBR) for NovaTech Startup",
    context="""
    Company: NovaTech (B2B SaaS, 18 months old)
    Period: February 2025
    Audience: Board of directors and investors

    Key Metrics:
    - MRR: $47,500 (+24.3% MoM)
    - ARR: $570,000
    - Burn rate: $62,000/month | Runway: 14 months
    - Gross Margin: 71% | CAC: $1,850 | LTV: $14,200
    - New customers: 12 | Total: 67
    - Churn: 2.9% | Net Revenue Retention: 108%
    - NPS: 67 (up from 58)
    - Pipeline: $280,000 | 3 deals in final negotiation
    """,
    requirements=[
        "Executive summary (3-4 sentences)",
        "Key highlights section",
        "Risks and challenges section",
        "Metrics summary table",
        "Next month priorities",
        "Professional markdown formatting",
    ],
    tone="executive, data-driven, concise",
    output_format="structured markdown report",
)

MEETING_AGENDA_TASK = BusinessTask(
    task_type="meeting",
    description="Create a focused meeting agenda for a product roadmap planning session",
    context="""
    Meeting: Q2 2025 Product Roadmap Planning
    Duration: 90 minutes
    Attendees: CEO, CTO, 3 Product Managers, Head of Engineering, Sales Lead
    Goal: Decide top 5 product priorities for Q2 based on customer feedback and business goals

    Input data:
    - 142 feature requests collected from customers in Q1
    - Top requested: AI integrations (47 votes), Mobile app (38 votes), API webhooks (29 votes)
    - Business goal: Reduce churn from 2.9% to <2% by end of Q2
    - Engineering capacity: 3 squads, each with 6-week sprint cycles
    - Constraint: 1 squad committed to technical debt reduction
    """,
    requirements=[
        "Pre-meeting prep assignments for each attendee",
        "Timed agenda items (must fit 90 minutes)",
        "Decision framework for prioritizing features",
        "Clear owner for each agenda item",
        "Action items template for post-meeting",
    ],
    tone="structured, action-oriented",
    output_format="formatted meeting agenda",
)

PROPOSAL_TASK = BusinessTask(
    task_type="proposal",
    description="Draft a project proposal for implementing an internal AI assistant",
    context="""
    Company: MidScale Manufacturing Co. (500 employees)
    Requestor: IT Department
    Proposal for: Leadership team approval
    Budget range: $50,000 - $80,000 first year

    Current pain points:
    - Customer support team spends 40% of time answering repetitive questions
    - HR team handles 200+ policy queries per month manually
    - Sales team needs faster proposal generation (currently 3-4 hours each)

    Proposed solution: Internal AI assistant using open-source LLMs + RAG
    """,
    requirements=[
        "Problem statement with quantified impact",
        "Proposed solution overview",
        "Implementation timeline (phases)",
        "Cost breakdown",
        "Expected ROI calculation",
        "Risks and mitigation",
        "Success metrics",
    ],
    tone="persuasive, data-backed, executive-friendly",
    output_format="structured business proposal",
)


# ============================================================
# Task Loader
# ============================================================

SAMPLE_TASKS = {
    "email": EMAIL_TASK,
    "report": REPORT_TASK,
    "meeting": MEETING_AGENDA_TASK,
    "proposal": PROPOSAL_TASK,
}


def load_task(task_type: str) -> BusinessTask:
    """Returns a sample task by type."""
    task_type = task_type.lower()
    if task_type not in SAMPLE_TASKS:
        available = ", ".join(SAMPLE_TASKS.keys())
        raise ValueError(f"Unknown task type '{task_type}'. Available: {available}")
    return SAMPLE_TASKS[task_type]


def load_task_from_file(filepath: str) -> BusinessTask:
    """
    Parses a task from a text file.
    File format: Key: Value pairs, with multi-line context.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Task file not found: {filepath}")

    content = path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    task_data = {
        "task_type": "general",
        "description": "",
        "context": "",
        "requirements": [],
        "tone": "professional",
    }

    current_section = None
    context_lines = []

    for line in lines:
        if line.startswith("Task:"):
            task_data["description"] = line.split("Task:", 1)[1].strip()
        elif line.startswith("Type:"):
            task_data["task_type"] = line.split("Type:", 1)[1].strip()
        elif line.startswith("Tone:"):
            task_data["tone"] = line.split("Tone:", 1)[1].strip()
        elif line.startswith("Context:"):
            current_section = "context"
        elif line.startswith("Constraints:") or line.startswith("Requirements:"):
            current_section = "requirements"
        elif current_section == "context" and line.strip():
            context_lines.append(line)
        elif current_section == "requirements" and line.strip().startswith("-"):
            task_data["requirements"].append(line.strip()[2:])

    task_data["context"] = "\n".join(context_lines)

    return BusinessTask(**task_data)


def format_task_for_agents(task: BusinessTask) -> str:
    """Converts a BusinessTask into a prompt string for agents."""
    req_list = "\n".join(f"  - {r}" for r in task.requirements) if task.requirements else "  - Produce high-quality output"

    return f"""BUSINESS TASK: {task.task_type.upper()}

DESCRIPTION:
{task.description}

CONTEXT:
{task.context.strip()}

REQUIREMENTS:
{req_list}

TONE: {task.tone}
OUTPUT FORMAT: {task.output_format}
{f'WORD LIMIT: ~{task.max_length} words' if task.max_length else ''}

Produce the best possible {task.task_type} output based on the above."""
