"""The 5 agents that build a resume and cover letter."""

from autogen import AssistantAgent, UserProxyAgent


def create_builder_agents(llm_config: dict) -> dict:

    parser = AssistantAgent(
        name="ExperienceParser",
        system_message="""Read the raw experience notes.
        Pull out skills, jobs (company, title, dates, achievements), education, projects.
        Show numbers where you can (%, $, etc.).
        End with: PARSING_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    analyzer = AssistantAgent(
        name="JobAnalyzer",
        system_message="""Read the job description and list:
        - Must-have skills
        - Nice-to-have skills
        - Main tasks
        - Important keywords (for ATS)
        End with: JOB_ANALYSIS_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    tailor = AssistantAgent(
        name="ResumeTailor",
        system_message="""Match the experience to the job.
        Put the most relevant experience first.
        Use the job's keywords in the bullet points.
        Add numbers to achievements. Do not make up facts.
        End with: TAILORING_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    formatter = AssistantAgent(
        name="ResumeFormatter",
        system_message="""Write the final resume in clean Markdown.
        Sections: Name + contact, Summary, Skills, Experience, Education, Certifications.
        Use action verbs. Keep it 1-2 pages.
        End with: RESUME_FORMATTED""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    cl_writer = AssistantAgent(
        name="CoverLetterWriter",
        system_message="""Write a short cover letter (3 paragraphs, ~250 words).
        1: Why this company and role.
        2: 2-3 experiences that match the job.
        3: Confident closing.
        End with: COVER_LETTER_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    admin = UserProxyAgent(
        name="ApplicantProxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "COVER_LETTER_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    return {
        "parser": parser,
        "analyzer": analyzer,
        "tailor": tailor,
        "formatter": formatter,
        "cl_writer": cl_writer,
        "admin": admin,
    }
