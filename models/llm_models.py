# models/llm_models.py
"""Data models for LLM interactions."""

from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str              # The generated text
    model: str                # Model that generated it
    tokens_used: int = 0      # Total tokens consumed
    prompt_tokens: int = 0    # Tokens in prompt
    completion_tokens: int = 0  # Tokens in completion

class LLMProviderError(Exception):
    """Base error for LLM provider issues."""
    pass

class RateLimitError(LLMProviderError):
    """API rate limit hit."""
    pass

class AuthenticationError(LLMProviderError):
    """Invalid API key."""
    pass

class ModelNotFoundError(LLMProviderError):
    """Requested model doesn't exist."""
    pass