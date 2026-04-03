# analysis/provider_factory.py
"""Factory for creating LLM providers."""

from typing import Optional
from analysis.llm_provider import BaseLLMProvider
from analysis.providers.groq_provider import GroqProvider
from analysis.providers.openai_provider import OpenAIProvider
from models.config_models import LLMConfig

def get_llm_provider(
    provider: str = "groq",
    api_key: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 2500,
    config: Optional[LLMConfig] = None
) -> BaseLLMProvider:
    """
    Factory function to create LLM provider.
    
    Args:
        provider: Provider name
        api_key: API key
        temperature: Sampling temperature
        max_tokens: Max tokens
        config: Optional LLMConfig for model overrides
    """
    providers = {
        "groq": GroqProvider,
        "openai": OpenAIProvider,
    }
    
    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}")
    
    instance = providers[provider](
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Override models from config if provided
    if config:
        instance.MODELS = {
            "small": config.small_model,
            "medium": config.medium_model,
            "large": config.large_model,
        }
    
    return instance

def get_llm_provider_from_config(config: LLMConfig) -> BaseLLMProvider:
    """
    Create provider directly from config.
    
    This is the preferred way when you have a Config object.
    """
    return get_llm_provider(
        provider=config.provider,
        api_key=config.api_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        config=config
    )