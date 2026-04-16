"""File management tools for saving and loading content."""

from pathlib import Path
from datetime import datetime


def save_content(content: str, filename: str, output_dir: Path) -> str:
    """Saves content to a file and returns the filepath."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def load_content(filepath: str) -> str:
    """Loads content from a file."""
    path = Path(filepath)
    if not path.exists():
        return f"File not found: {filepath}"
    return path.read_text(encoding="utf-8")


def list_outputs(output_dir: Path) -> str:
    """Lists all generated output files."""
    if not output_dir.exists():
        return "No output directory found."

    files = sorted(output_dir.glob("*.md")) + sorted(output_dir.glob("*.json"))
    if not files:
        return "No output files found."

    lines = [f"Output files in {output_dir}:"]
    for f in files:
        size = f.stat().st_size
        lines.append(f"  {f.name} ({size:,} bytes)")
    return "\n".join(lines)
