"""AI Resume Builder: tailors your experience to a job description."""

import argparse
import re
from pathlib import Path

from autogen import GroupChat, GroupChatManager
from llm import get_llm_config
from builder_agents import create_builder_agents

# Fixed order: each agent speaks once, then stop. No wasted rounds.
PIPELINE = ["ExperienceParser", "JobAnalyzer", "ResumeTailor",
            "ResumeFormatter", "CoverLetterWriter"]


def _next_speaker(last_speaker, groupchat):
    """Pick the next agent in fixed order; stop after the cover letter."""
    by_name = {a.name: a for a in groupchat.agents}
    name = last_speaker.name
    if name not in PIPELINE:        # admin started -> first agent
        return by_name["ExperienceParser"]
    i = PIPELINE.index(name)
    if i + 1 < len(PIPELINE):
        return by_name[PIPELINE[i + 1]]
    return None                     # cover letter done -> stop


def run_resume_builder(raw_experience: str, job_description: str) -> str:
    """Run the pipeline. Returns the final resume + cover letter text."""
    print("\n" + "="*65)
    print("AI RESUME BUILDER — 5-Agent Pipeline")
    print("="*65)

    llm_config = get_llm_config(temperature=0.6)
    llm_config["max_tokens"] = 900  # shorter replies = faster, stays under rate limit
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
        max_round=7,
        speaker_selection_method=_next_speaker,
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "COVER_LETTER_DONE" in msg.get("content", ""),
    )

    agents["admin"].initiate_chat(
        manager,
        message=f"""Build a resume and cover letter for this job.

MY EXPERIENCE:
{raw_experience[:1500]}

JOB:
{job_description[:1200]}

Steps: Parser -> JobAnalyzer -> Tailor -> Formatter -> CoverLetterWriter.
Keep each step short.""",
    )

    # Grab the final resume and cover letter to show in the UI
    parts = []
    for msg in groupchat.messages:
        if msg.get("name") in ("ResumeFormatter", "CoverLetterWriter") and msg.get("content"):
            # remove any ALL_CAPS marker the agent added (e.g. COVER_LETTER_DONE)
            text = re.sub(r"\*{0,2}[A-Z][A-Z_]+_DONE\*{0,2}", "", msg["content"]).strip()
            parts.append(text)
    return "\n\n---\n\n".join(parts)

def main():
    parser = argparse.ArgumentParser(description="AI Resume Builder")
    parser.add_argument("--resume", default=None, help="Path to raw experience text file")
    parser.add_argument("--job", default=None, help="Path to job description text file")
    args = parser.parse_args()

    sample_dir = Path(__file__).parent / "sample_input"

    resume_file = args.resume or str(sample_dir / "raw_experience.txt")
    job_file = args.job or str(sample_dir / "job_description.txt")

    raw_exp = Path(resume_file).read_text(encoding="utf-8")
    job_desc = Path(job_file).read_text(encoding="utf-8")

    run_resume_builder(raw_exp, job_desc)


if __name__ == "__main__":
    main()


