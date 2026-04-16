# Module 08: Real-World Projects

Apply everything from Modules 01–07 by building four production-quality AI projects.

---

## Projects at a Glance

| # | Project | Agents | Pattern | Complexity |
|---|---------|--------|---------|-----------|
| 01 | Research Assistant | 5 | GroupChat + RAG | ★★★☆ |
| 02 | Code Reviewer | 5 | Specialist Panel | ★★★☆ |
| 03 | Resume Builder | 5 | Sequential Pipeline | ★★★☆ |
| 04 | Business Automator | 4 | Quality Pipeline | ★★☆☆ |

---

## Project 01: Research Assistant

**What it does:** Takes a topic → produces a structured research report with fact-checking.

**Agent pipeline:**
```
Orchestrator → Researcher → FactChecker → Analyst → ReportWriter → [saves to output/]
```

**Key concepts practiced:**
- GroupChat with auto speaker selection
- Tool registration (`save_report`, `create_outline`)
- Multi-step research pipeline
- Output file management

**Run:** `python module_08_projects/project_01_research_assistant/research_assistant.py --topic "Quantum Computing"`

---

## Project 02: Code Reviewer

**What it does:** Analyzes Python code files and produces a multi-dimensional review report.

**Agent pipeline:**
```
SyntaxReviewer → SecurityReviewer → StyleReviewer → PerformanceReviewer → ReviewSummarizer
```

**Key concepts practiced:**
- Specialist agents with narrow, focused roles
- Reviewing code with security expertise
- Structured output formatting
- Real-world code quality criteria

**Run:** `python module_08_projects/project_02_code_reviewer/code_reviewer.py --file sample_code/buggy_script.py`

---

## Project 03: Resume Builder

**What it does:** Transforms raw career notes + a job description → tailored resume + cover letter.

**Agent pipeline:**
```
ExperienceParser → JobAnalyzer → ResumeTailor → ResumeFormatter → CoverLetterWriter
```

**Key concepts practiced:**
- Document transformation pipeline
- ATS keyword optimization
- Sequential conversation pattern
- Structured output (markdown resume)

**Run:** `python module_08_projects/project_03_resume_builder/resume_builder.py`

---

## Project 04: Business Document Automator

**What it does:** Generates professional business documents (emails, reports, agendas, proposals) with a quality review loop.

**Agent pipeline:**
```
TaskAnalyzer → DraftWriter → QualityReviewer → FinalEditor
```

**Key concepts practiced:**
- Critic/revision loop (QualityReviewer → DraftWriter)
- Task-agnostic system design
- Document type routing
- Production-quality output formatting

**Run:** `python module_08_projects/project_04_business_automator/business_automator.py --task email`

---

## How to Approach Each Project

1. **Read the README.md** first — understand the goal and agent roles
2. **Read `agents.py` / `workflow_agents.py`** — understand each agent's system message
3. **Run the demo** — see the pipeline in action
4. **Modify a system message** — change the tone or output format
5. **Add a new agent** — extend the pipeline
6. **Connect to a real data source** — replace sample data with live API calls

---

## Common Patterns Across All Projects

```python
# Pattern 1: GroupChat with specialist agents
groupchat = GroupChat(
    agents=[admin, specialist1, specialist2, ..., summarizer],
    messages=[],
    max_round=10,
    speaker_selection_method="auto",
)

# Pattern 2: Pipeline termination
is_termination_msg=lambda msg: "TASK_COMPLETE" in msg.get("content", "")

# Pattern 3: Saving output
output_path = Path("output") / f"result_{timestamp}.md"
output_path.write_text(final_content)
```

---

## Interview Questions for This Module

**Q: How do you ensure agent specialization in GroupChat?**
A: Each agent's system_message strictly defines their role, what they should NOT do, and what signal ends their turn (e.g., "DRAFT_COMPLETE — Reviewer, please proceed"). The manager's speaker_selection_method (auto or round_robin) controls flow.

**Q: How do you extract the final output from a GroupChat?**
A: Iterate `groupchat.messages` in reverse order, search for a specific marker (e.g., "## FINAL OUTPUT"), and extract the content after that marker.

**Q: What's the difference between sequential chat and GroupChat for pipelines?**
A: Sequential chat (initiate_chat chains) is cleaner for strict linear flows. GroupChat is better when agents need to react to each other's outputs or when you need flexible routing. For production, GroupChat with `round_robin` closely approximates sequential with more flexibility.
