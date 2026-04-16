# Project 03: AI Resume Builder

Transforms raw experience notes + job description → tailored resume + cover letter.

## What It Does
1. **ExperienceParser** structures your raw notes into organized experience data
2. **JobAnalyzer** extracts must-have skills, ATS keywords, and culture signals
3. **ResumeTailor** rewrites your bullets to match the job requirements
4. **ResumeFormatter** outputs an ATS-friendly markdown resume
5. **CoverLetterWriter** writes a personalized 3-paragraph cover letter

## Usage
```bash
# Use sample data
python module_08_projects/project_03_resume_builder/resume_builder.py

# Use your own files
python module_08_projects/project_03_resume_builder/resume_builder.py \
    --resume my_experience.txt \
    --job job_description.txt
```

## Input Format
- `raw_experience.txt` — messy notes about your background (no format required)
- `job_description.txt` — paste the full job description text

## Extension Ideas
- Export to .docx using python-docx
- Connect to LinkedIn job scraper
- A/B test multiple resume versions
- Score ATS compatibility before submitting
