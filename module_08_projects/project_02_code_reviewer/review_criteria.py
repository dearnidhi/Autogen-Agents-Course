"""
module_08_projects/project_02_code_reviewer/review_criteria.py
---------------------------------------------------------------
Review criteria definitions for each specialist reviewer.

These criteria are injected into agent system messages and
used to structure the final review report.
"""

SYNTAX_CRITERIA = [
    "Syntax errors and typos",
    "Missing imports or undefined variables",
    "Incorrect data types or type mismatches",
    "Off-by-one errors in loops and indexing",
    "Unhandled exceptions and bare except clauses",
    "Unreachable code or dead code blocks",
    "Incorrect use of Python built-ins",
]

SECURITY_CRITERIA = [
    "SQL injection vulnerabilities (unparameterized queries)",
    "Hardcoded credentials, API keys, or secrets",
    "Unsafe deserialization (pickle, yaml.load)",
    "Path traversal vulnerabilities",
    "Command injection (os.system, subprocess with shell=True)",
    "Insecure random number generation (random vs secrets)",
    "Missing input validation and sanitization",
    "Exposed sensitive data in logs or error messages",
]

STYLE_CRITERIA = [
    "PEP 8 compliance (naming, spacing, line length)",
    "Missing or inadequate docstrings",
    "Overly complex functions (do too many things)",
    "Inconsistent naming conventions",
    "Magic numbers (unexplained literals)",
    "Excessive code duplication",
    "Poor variable/function naming (a, temp, data2)",
    "Missing type hints",
]

PERFORMANCE_CRITERIA = [
    "Nested loops with O(n²) or worse complexity",
    "Repeated expensive operations inside loops",
    "Loading entire files/datasets into memory unnecessarily",
    "Missing list comprehensions or generator expressions",
    "Inefficient string concatenation in loops",
    "Not using built-in functions (sum, max, min, any, all)",
    "Database queries inside loops (N+1 problem)",
    "Missing caching for repeated expensive calls",
]

SEVERITY_LEVELS = {
    "CRITICAL": "Must fix before production — security risk or will crash",
    "HIGH": "Should fix soon — significant bug or performance issue",
    "MEDIUM": "Fix in next iteration — code quality or minor bug",
    "LOW": "Nice to have — style or minor improvement",
    "INFO": "Informational — suggestion for consideration",
}

# Review report template
REPORT_TEMPLATE = """# Code Review Report

**File:** {filename}
**Date:** {date}
**Overall Score:** {score}/10
**Verdict:** {verdict}

---

## Executive Summary
{summary}

---

## Critical Issues
{critical_issues}

## Security Issues
{security_issues}

## Style & Maintainability
{style_issues}

## Performance Notes
{performance_notes}

---

## Positive Findings
{positives}

## Top 3 Recommendations
{recommendations}
"""


def format_criteria_list(criteria: list[str]) -> str:
    """Formats criteria as a numbered list for system messages."""
    return "\n".join(f"  {i+1}. {c}" for i, c in enumerate(criteria))


def get_syntax_criteria_text() -> str:
    return format_criteria_list(SYNTAX_CRITERIA)


def get_security_criteria_text() -> str:
    return format_criteria_list(SECURITY_CRITERIA)


def get_style_criteria_text() -> str:
    return format_criteria_list(STYLE_CRITERIA)


def get_performance_criteria_text() -> str:
    return format_criteria_list(PERFORMANCE_CRITERIA)
