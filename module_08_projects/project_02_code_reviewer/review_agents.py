"""
project_02_code_reviewer/review_agents.py
------------------------------------------
5-agent code review team:
- SyntaxReviewer: bugs, errors, type issues
- SecurityReviewer: vulnerabilities (OWASP top 10)
- StyleReviewer: PEP8, naming, documentation
- PerformanceReviewer: complexity, optimization
- ReviewSummarizer: final actionable summary
"""

from autogen import AssistantAgent, UserProxyAgent


def create_review_agents(llm_config: dict) -> dict:
    """Creates all code review agents."""

    syntax_reviewer = AssistantAgent(
        name="SyntaxReviewer",
        system_message="""Review Python code for correctness.
        Check: syntax errors, logic bugs, type mismatches, missing edge cases, exception handling.
        Format:
        ## Syntax & Correctness
        - [CRITICAL/WARNING/INFO] Issue | Line: X | Fix: ...
        End with: SYNTAX_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    security_reviewer = AssistantAgent(
        name="SecurityReviewer",
        system_message="""Review Python code for security vulnerabilities.
        Check: SQL injection, hardcoded secrets, unsafe eval/exec, path traversal,
               command injection, insecure deserialization, input validation gaps.
        Format:
        ## Security Review | Risk: CRITICAL/HIGH/MEDIUM/LOW/NONE
        - [VULN_TYPE] Description | Severity: X | Fix: ...
        End with: SECURITY_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    style_reviewer = AssistantAgent(
        name="StyleReviewer",
        system_message="""Review Python code for style and maintainability.
        Check: PEP8 compliance, naming conventions, docstrings, comments,
               DRY principle, magic numbers, function length.
        Format:
        ## Style & Maintainability
        - [STYLE] Issue | Current: X | Suggested: Y
        End with: STYLE_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    performance_reviewer = AssistantAgent(
        name="PerformanceReviewer",
        system_message="""Review Python code for performance issues.
        Check: time/space complexity, unnecessary loops, missing caching,
               inefficient string ops, blocking I/O, memory leaks.
        Format:
        ## Performance Review
        - [PERF] Issue | Complexity: O(?) | Fix: ... | Impact: HIGH/MEDIUM/LOW
        End with: PERFORMANCE_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    summarizer = AssistantAgent(
        name="ReviewSummarizer",
        system_message="""Synthesize all reviewer feedback into a final summary.
        Format:
        # Code Review Summary
        ## Overall Score: X/10
        ## Decision: APPROVE / APPROVE_WITH_CHANGES / REJECT

        ## Critical Issues (Must Fix)
        ## Important Issues (Should Fix)
        ## Nice to Have
        ## Strengths
        ## Ordered Action Items

        End with: REVIEW_COMPLETE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    admin = UserProxyAgent(
        name="CodeSubmitter",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "REVIEW_COMPLETE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    return {
        "syntax": syntax_reviewer,
        "security": security_reviewer,
        "style": style_reviewer,
        "performance": performance_reviewer,
        "summarizer": summarizer,
        "admin": admin,
    }
