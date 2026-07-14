"""Domain-specific errors raised by the documentation platform."""


class DocAgentError(Exception):
    """Base class for errors that can be presented to a DocAgent user."""


class ConfigurationError(DocAgentError):
    """Raised when a configuration file is invalid or inconsistent."""


class EnvironmentError(DocAgentError):
    """Raised when required environment configuration cannot be loaded."""


class AnalysisError(DocAgentError):
    """Raised when source analysis cannot produce a reliable result."""


class GenerationError(DocAgentError):
    """Raised when documentation output cannot be generated."""
