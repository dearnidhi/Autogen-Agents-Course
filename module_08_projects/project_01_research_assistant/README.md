# Project 01: Research Assistant

A 5-agent pipeline that researches any topic and produces a structured markdown report.

## What It Does
1. **Orchestrator** breaks the topic into focused sub-questions
2. **Researcher** answers each sub-question with factual depth
3. **FactChecker** verifies claims and flags uncertainties
4. **Analyst** identifies patterns and insights across findings
5. **ReportWriter** produces a structured markdown report saved to `output/`

## Usage
```bash
# Default topic
python module_08_projects/project_01_research_assistant/research_assistant.py

# Custom topic
python module_08_projects/project_01_research_assistant/research_assistant.py --topic "quantum computing applications"

# Use specific provider
python module_08_projects/project_01_research_assistant/research_assistant.py --topic "AI in healthcare" --provider groq
```

## Output
Reports are saved to `module_08_projects/project_01_research_assistant/output/` as markdown files.

## Architecture
```
Admin → GroupChatManager → Orchestrator → Researcher → FactChecker → Analyst → Writer → [save to file]
```

## Extension Ideas
- Add a real web search tool (Serper.dev, Tavily)
- Export to PDF using pandoc
- Add a citation manager tool
- Send report via email using SMTP tool
