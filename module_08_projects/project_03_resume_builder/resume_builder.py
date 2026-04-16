"""
project_03_resume_builder/resume_builder.py
--------------------------------------------
AI Resume Builder: tailors your experience to any job description.

Usage:
    python module_08_projects/project_03_resume_builder/resume_builder.py
    python module_08_projects/project_03_resume_builder/resume_builder.py --resume path/to/experience.txt --job path/to/job.txt
"""

import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from autogen import GroupChat, GroupChatManager
from config.llm_config import get_llm_config
from module_08_projects.project_03_resume_builder.builder_agents import create_builder_agents


def run_resume_builder(
    raw_experience: str,
    job_description: str,
    provider: str = None,
) -> None:
    print("\n" + "="*65)
    print("AI RESUME BUILDER — 5-Agent Pipeline")
    print("="*65)

    llm_config = get_llm_config(provider=provider, temperature=0.6)
    agents = create_builder_agents(llm_config)

    groupchat = GroupChat(
        agents=[
            agents["admin"],
            agents["parser"],
            agents["analyzer"],
            agents["tailor"],
            agents["formatter"],
            agents["cl_writer"],
        ],
        messages=[],
        max_round=14,
        speaker_selection_method="round_robin",
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "COVER_LETTER_DONE" in msg.get("content", ""),
    )

    agents["admin"].initiate_chat(
        manager,
        message=f"""Build a tailored resume and cover letter.

RAW EXPERIENCE:
{raw_experience[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

Pipeline:
1. ExperienceParser: Structure the raw experience
2. JobAnalyzer: Extract job requirements and ATS keywords
3. ResumeTailor: Match experience to requirements
4. ResumeFormatter: Format the final resume in ATS-friendly markdown
5. CoverLetterWriter: Write the personalized cover letter

Work through each step in order.""",
    )


def main():
    parser = argparse.ArgumentParser(description="AI Resume Builder")
    parser.add_argument("--resume", default=None, help="Path to raw experience text file")
    parser.add_argument("--job", default=None, help="Path to job description text file")
    parser.add_argument("--provider", default=None, choices=["groq", "gemini", "openrouter", "huggingface"])
    args = parser.parse_args()

    sample_dir = Path(__file__).parent / "sample_input"

    resume_file = args.resume or str(sample_dir / "raw_experience.txt")
    job_file = args.job or str(sample_dir / "job_description.txt")

    raw_exp = Path(resume_file).read_text(encoding="utf-8")
    job_desc = Path(job_file).read_text(encoding="utf-8")

    run_resume_builder(raw_exp, job_desc, args.provider)


if __name__ == "__main__":
    main()
