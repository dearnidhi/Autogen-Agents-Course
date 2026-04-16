"""
utils/helpers.py
-----------------
General-purpose utility functions used across all course modules.
"""

import os
import sys
import ast
from pathlib import Path
from typing import Optional, Tuple


def get_project_root() -> Path:
    """Returns the absolute path to the course root directory (Autogen/)."""
    return Path(__file__).parent.parent


def ensure_dir(path: str | Path) -> Path:
    """Creates a directory (and parents) if it doesn't exist. Returns Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_text_file(filepath: str | Path) -> str:
    """
    Reads a text file and returns its contents.
    Raises FileNotFoundError with a helpful message if missing.
    """
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(
            f"File not found: {p}\n"
            f"Current directory: {Path.cwd()}\n"
            f"Make sure you're running from the course root directory."
        )
    return p.read_text(encoding="utf-8")


def truncate_for_context(text: str, max_chars: int = 6000, label: str = "") -> str:
    """
    Truncates text to fit within LLM context limits.
    Adds a clear truncation notice so agents know they have partial content.

    Args:
        text: Input text to potentially truncate
        max_chars: Character limit before truncation
        label: Optional label for the truncation notice (e.g., "Code file")
    """
    if len(text) <= max_chars:
        return text

    prefix = f"[{label}] " if label else ""
    truncated = text[:max_chars]
    notice = (
        f"\n\n... [{prefix}TRUNCATED: showing first {max_chars:,} of "
        f"{len(text):,} characters. Remaining content omitted.] ..."
    )
    return truncated + notice


def validate_python_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validates Python code syntax without executing it.
    Safe to call with untrusted code.

    Returns:
        (is_valid, error_message) — error_message is None if valid
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Parse error: {e}"


def format_agent_separator(agent_name: str, width: int = 60) -> str:
    """Returns a formatted separator for agent output."""
    return f"\n{'='*width}\n[{agent_name}]\n{'='*width}"


def add_project_root_to_path() -> None:
    """
    Adds the project root to sys.path so that 'config' and 'utils'
    can be imported from any subdirectory.

    Call this at the top of any script that imports from config/ or utils/.
    """
    root = str(get_project_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def count_tokens_approx(text: str) -> int:
    """
    Rough token count estimate (1 token ≈ 4 characters for English text).
    Useful for staying within context limits without exact tokenization.
    """
    return len(text) // 4


def read_sample_file(module_folder: str, filename: str) -> str:
    """
    Reads a sample data file from a module's subdirectory.

    Args:
        module_folder: e.g., "project_02_code_reviewer/sample_code"
        filename: e.g., "buggy_script.py"

    Example:
        code = read_sample_file("project_02_code_reviewer/sample_code", "buggy_script.py")
    """
    root = get_project_root()
    filepath = root / "module_08_projects" / module_folder / filename
    return load_text_file(filepath)
