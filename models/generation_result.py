# models/generation_result.py
"""Data model for generation results."""
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class GenerationResult:
    """Result of documentation generation."""
    readme_path: Path
    technical_doc_path: Path
    api_reference_path: Optional[Path] = None
    generated_at: datetime = field(default_factory=datetime.now)
    files_documented: int = 0
    total_classes: int = 0
    total_functions: int = 0
    generation_time_seconds: float = 0.0
    
    def summary(self) -> str:
        """Human-readable generation summary."""
        return (
            f"Documentation Generated:\n"
            f"  README: {self.readme_path}\n"
            f"  Technical Doc: {self.technical_doc_path}\n"
            f"  API Reference: {self.api_reference_path or 'N/A'}\n"
            f"  Files documented: {self.files_documented}\n"
            f"  Classes: {self.total_classes}\n"
            f"  Functions: {self.total_functions}\n"
            f"  Time: {self.generation_time_seconds:.2f}s"
        )