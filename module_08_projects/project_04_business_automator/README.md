# Project 04: AI Business Document Automator

Automates professional business writing using a 4-agent quality pipeline.

## What It Does
1. **TaskAnalyzer** — deconstructs requirements and sets quality standards
2. **DraftWriter** — produces a complete, professional first draft
3. **QualityReviewer** — checks completeness, tone, and clarity; requests one revision if needed
4. **FinalEditor** — polishes language, formatting, and delivers the final document

## Supported Document Types
| Type | Description |
|------|-------------|
| `email` | Professional business emails (delays, proposals, follow-ups) |
| `report` | Business reviews, status reports, MBRs |
| `meeting` | Meeting agendas with timed items and owners |
| `proposal` | Project proposals with ROI and risk sections |

## Usage
```bash
# Quick start — generate a sample email
python module_08_projects/project_04_business_automator/business_automator.py --task email

# Generate a monthly business report
python module_08_projects/project_04_business_automator/business_automator.py --task report

# Use your own task file
python module_08_projects/project_04_business_automator/business_automator.py \
    --file sample_tasks/email_draft_request.txt

# With a specific provider
python module_08_projects/project_04_business_automator/business_automator.py \
    --task proposal --provider gemini
```

## Custom Task File Format
Create a `.txt` file with this structure:
```
Task: Brief description of what to write
Type: email|report|meeting|proposal
Tone: professional|formal|casual

Context:
All the background information, data, and details the agent needs.
Multiple lines are fine.

Constraints:
- Requirement 1
- Requirement 2
```

## Extension Ideas
- Add `--voice` parameter for brand voice (formal/casual/technical)
- Integrate with Gmail API to send approved emails directly
- Connect to Notion/Confluence for automatic report publishing
- Add a human approval step before finalizing
- Build a web UI with Gradio or Streamlit
