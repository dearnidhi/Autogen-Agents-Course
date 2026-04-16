"""
module_08_projects/project_03_resume_builder/templates.py
----------------------------------------------------------
Resume and cover letter templates.

Provides markdown templates for ATS-friendly resumes
and structured cover letters.
"""

from datetime import datetime


# ============================================================
# Resume Template
# ============================================================

RESUME_TEMPLATE = """# {full_name}
{location} | {email} | {phone} | {linkedin}

---

## Professional Summary
{summary}

---

## Technical Skills
{skills_section}

---

## Professional Experience
{experience_section}

---

## Education
{education_section}

---

## Projects
{projects_section}

---

## Certifications & Achievements
{certifications_section}
"""

EXPERIENCE_ENTRY_TEMPLATE = """### {job_title}
**{company}** | {location} | {start_date} – {end_date}

{bullets}
"""

EDUCATION_ENTRY_TEMPLATE = """### {degree}
**{institution}** | {year}
{details}
"""

PROJECT_ENTRY_TEMPLATE = """### {project_name}
*{tech_stack}*
{description}
"""


# ============================================================
# Cover Letter Template
# ============================================================

COVER_LETTER_TEMPLATE = """---

{date}

Hiring Manager
{company_name}
{company_location}

---

**Re: {job_title} Position**

Dear Hiring Manager,

{opening_paragraph}

{body_paragraph}

{closing_paragraph}

Sincerely,

{full_name}
{email} | {phone}
{linkedin}

---
"""


# ============================================================
# ATS Keywords Section Template
# ============================================================

ATS_SECTION_TEMPLATE = """
<!-- ATS Optimization Notes (remove before submitting) -->
<!-- Keywords detected in job description: {keywords} -->
<!-- Match score estimate: {match_score}% -->
<!-- Missing keywords to consider adding: {missing_keywords} -->
"""


# ============================================================
# Helper Functions
# ============================================================

def format_bullet_points(bullets: list[str]) -> str:
    """Formats a list of bullet points with proper markdown."""
    return "\n".join(f"- {b.strip()}" for b in bullets if b.strip())


def format_skills_section(skills_by_category: dict) -> str:
    """Formats skills grouped by category."""
    lines = []
    for category, skills in skills_by_category.items():
        skills_str = " · ".join(skills) if isinstance(skills, list) else skills
        lines.append(f"**{category}:** {skills_str}")
    return "\n".join(lines)


def build_resume(data: dict) -> str:
    """
    Builds a formatted resume from structured data.

    Args:
        data: dict with keys matching RESUME_TEMPLATE placeholders

    Returns:
        Formatted markdown resume string
    """
    # Set defaults for missing fields
    defaults = {
        "full_name": "Your Name",
        "location": "City, State",
        "email": "email@example.com",
        "phone": "(555) 000-0000",
        "linkedin": "linkedin.com/in/yourname",
        "summary": "",
        "skills_section": "",
        "experience_section": "",
        "education_section": "",
        "projects_section": "",
        "certifications_section": "",
    }
    defaults.update(data)
    return RESUME_TEMPLATE.format(**defaults)


def build_cover_letter(data: dict) -> str:
    """
    Builds a formatted cover letter from structured data.

    Args:
        data: dict with keys matching COVER_LETTER_TEMPLATE placeholders

    Returns:
        Formatted markdown cover letter string
    """
    defaults = {
        "date": datetime.now().strftime("%B %d, %Y"),
        "company_name": "Company Name",
        "company_location": "City, State",
        "job_title": "Position",
        "opening_paragraph": "",
        "body_paragraph": "",
        "closing_paragraph": "",
        "full_name": "Your Name",
        "email": "email@example.com",
        "phone": "(555) 000-0000",
        "linkedin": "linkedin.com/in/yourname",
    }
    defaults.update(data)
    return COVER_LETTER_TEMPLATE.format(**defaults)


def extract_resume_text(formatted_resume: str) -> str:
    """
    Extracts plain text from a markdown resume (for ATS scoring).
    Removes markdown formatting symbols.
    """
    import re
    # Remove markdown headers
    text = re.sub(r"^#{1,6}\s+", "", formatted_resume, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text.strip()
