"""
project_03_resume_builder/builder_agents.py
--------------------------------------------
5-agent resume building pipeline:
1. ExperienceParser — structures raw notes into JSON
2. JobAnalyzer — extracts requirements from job description
3. ResumeTailor — tailors content to match job requirements
4. ResumeFormatter — formats as ATS-friendly markdown
5. CoverLetterWriter — writes personalized cover letter
"""

from autogen import AssistantAgent, UserProxyAgent


def create_builder_agents(llm_config: dict) -> dict:

    parser = AssistantAgent(
        name="ExperienceParser",
        system_message="""Parse raw experience notes into structured format.
        Extract:
        - Skills (technical + soft)
        - Work experience with company, title, duration, key achievements (quantified)
        - Education and certifications
        - Projects
        Output as clean structured JSON.
        Highlight any QUANTIFIABLE achievements (%, $, X times faster, etc.)
        End with: PARSING_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    analyzer = AssistantAgent(
        name="JobAnalyzer",
        system_message="""Analyze job descriptions to extract:
        1. MUST-HAVE: Technical skills explicitly required
        2. NICE-TO-HAVE: Preferred but not required skills
        3. KEY_RESPONSIBILITIES: What they'll actually do day-to-day
        4. CULTURE_SIGNALS: Work style, team dynamics, values
        5. ATS_KEYWORDS: Terms the screening system likely looks for
        6. SENIORITY: Years of experience, scope expected
        Output a structured analysis with each section clearly labeled.
        End with: JOB_ANALYSIS_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    tailor = AssistantAgent(
        name="ResumeTailor",
        system_message="""Tailor resume content to match job requirements.
        Strategy:
        1. Reorder experiences — most relevant first
        2. Rewrite bullet points — use exact keywords from job description
        3. Quantify achievements where possible (add metrics if missing)
        4. Remove/minimize irrelevant experience
        5. Amplify matching skills to the top of skills section
        6. Note honest skill gaps (don't fabricate experience)
        Output tailored content for each resume section.
        End with: TAILORING_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    formatter = AssistantAgent(
        name="ResumeFormatter",
        system_message="""Format resumes in clean, ATS-friendly markdown.
        Structure:
        # [Full Name]
        email@example.com | LinkedIn: /in/username | GitHub: /username

        ## Professional Summary
        [2-3 sentences, tailored to this specific role]

        ## Technical Skills
        **Languages:** ... | **Frameworks:** ... | **Tools:** ...

        ## Professional Experience
        ### [Title] | [Company] | [Start] – [End/Present]
        - [Achievement-focused bullet with metric]
        - [Another achievement]

        ## Education
        ### [Degree] | [University] | [Year]

        ## Certifications (if any)

        Keep to 1 page ideally, 2 pages max. Use action verbs. ATS-optimize.
        End with: RESUME_FORMATTED""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    cl_writer = AssistantAgent(
        name="CoverLetterWriter",
        system_message="""Write compelling, personalized cover letters.
        Structure (3 paragraphs, ~250 words):
        Para 1: Why THIS company + role (not generic). Show you've researched them.
        Para 2: Connect 2-3 specific experiences to specific job requirements
        Para 3: Confident close with clear CTA

        Tone: Professional but authentic. No clichés like "I am writing to express..."
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
