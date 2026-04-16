"""Capstone project tools."""
from .web_search import simulated_web_search, register_search_tools
from .file_manager import save_content, load_content
from .formatter import format_for_platform

__all__ = [
    "simulated_web_search",
    "register_search_tools",
    "save_content",
    "load_content",
    "format_for_platform",
]
