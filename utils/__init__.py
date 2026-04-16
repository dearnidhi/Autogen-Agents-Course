"""
utils/__init__.py
-----------------
Shared utilities for the AutoGen Complete Course.
"""

from .helpers import (
    get_project_root,
    ensure_dir,
    truncate_for_context,
    load_text_file,
    validate_python_syntax,
)

__all__ = [
    "get_project_root",
    "ensure_dir",
    "truncate_for_context",
    "load_text_file",
    "validate_python_syntax",
]
