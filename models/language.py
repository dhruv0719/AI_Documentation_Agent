"""Language-neutral contracts shared by current and future parsers."""

from enum import Enum


class SourceLanguage(str, Enum):
    """Languages currently planned by the documentation platform."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"

    @classmethod
    def from_extension(cls, extension: str) -> "SourceLanguage":
        """Resolve a supported language from a file extension."""
        extensions = {
            ".py": cls.PYTHON,
            ".js": cls.JAVASCRIPT,
            ".jsx": cls.JAVASCRIPT,
            ".ts": cls.TYPESCRIPT,
            ".tsx": cls.TYPESCRIPT,
        }
        try:
            return extensions[extension.lower()]
        except KeyError as error:
            raise ValueError(f"Unsupported source extension: {extension}") from error
