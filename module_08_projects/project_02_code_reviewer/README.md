# Project 02: AI Code Reviewer

A 4-specialist code review panel that analyzes Python code for bugs, security issues, style problems, and performance bottlenecks.

## What It Does
1. **SyntaxReviewer** — bugs, type errors, logic issues, exception handling
2. **SecurityReviewer** — SQL injection, hardcoded secrets, path traversal, OWASP top 10
3. **StyleReviewer** — PEP8, naming, docstrings, DRY principle
4. **PerformanceReviewer** — complexity analysis, optimization opportunities
5. **ReviewSummarizer** — overall score, decision (APPROVE/REJECT), ordered action items

## Usage
```bash
# Review sample buggy code (demo)
python module_08_projects/project_02_code_reviewer/code_reviewer.py

# Review your own file
python module_08_projects/project_02_code_reviewer/code_reviewer.py --file path/to/your_script.py
```

## Sample Files
- `sample_code/buggy_script.py` — intentional bugs for demo (SQL injection, hardcoded passwords, etc.)
- `sample_code/messy_function.py` — style and performance issues

## Extension Ideas
- Save reviews to markdown reports
- Integrate with GitHub Actions as a PR review bot
- Add a TypeScript/Java reviewer variant
- Compare before/after improvement scores
