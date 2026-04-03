# analysis/llm_provider.py
"""Abstract interface for LLM providers."""

import time
import asyncio
from abc import ABC, abstractmethod
from models.llm_models import LLMResponse

class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM providers (Groq, OpenAI, Anthropic, etc.) must implement this interface.
    """

    # Subclasses MUST override this
    MODELS: dict = {}  # Class variable, not property

    # Default system prompt for code analysis
    DEFAULT_SYSTEM_PROMPT = (
        "You are an expert code analyst. "
        "When asked to respond with JSON, output ONLY valid JSON. "
        "No markdown code fences, no explanations before or after."
    )

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    @abstractmethod
    async def generate(self, prompt: str, model: str = None, system_prompt: str = None) -> LLMResponse:
        """
        Generate response from LLM (async).
        
        Args:
            prompt: The prompt to send to the LLM
            model: Specific model to use (optional, uses default if not provided)
            
        Returns:
            LLMResponse with generated content and metadata
            
        Raises:
            LLMProviderError: If API call fails
        """
        pass
    
    @abstractmethod
    def generate_sync(self, prompt: str, model: str = None, system_prompt: str = None) -> LLMResponse:
        """
        Generate response from LLM (synchronous).
        
        Args:
            prompt: The prompt to send to the LLM
            model: Specific model to use (optional)
            
        Returns:
            LLMResponse with generated content and metadata
        """
        pass

    async def generate_with_retry(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        max_retries: int = None
    ) -> LLMResponse:
        """
        Generate with automatic retry on failure.
        
        Retries on:
        - Rate limit errors (with exponential backoff)
        - Temporary API errors
        
        Does NOT retry on:
        - Authentication errors
        - Invalid model errors
        """
        retries = max_retries or self.MAX_RETRIES
        last_error = None
        
        for attempt in range(retries):
            try:
                return await self.generate(prompt, model, system_prompt)
            
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Don't retry auth errors
                if "auth" in error_msg or "api key" in error_msg:
                    raise
                
                # Don't retry on last attempt
                if attempt == retries - 1:
                    raise
                
                # Exponential backoff
                wait_time = self.RETRY_DELAY * (2 ** attempt)
                print(f"    ⚠ Retry {attempt + 1}/{retries} in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        
        raise last_error
    
    def generate_sync_with_retry(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        max_retries: int = None
    ) -> LLMResponse:
        """Sync version of generate_with_retry."""
        retries = max_retries or self.MAX_RETRIES
        last_error = None
        
        for attempt in range(retries):
            try:
                return self.generate_sync(prompt, model, system_prompt)
            
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                if "auth" in error_msg or "api key" in error_msg:
                    raise
                
                if attempt == retries - 1:
                    raise
                
                wait_time = self.RETRY_DELAY * (2 ** attempt)
                print(f"    ⚠ Retry {attempt + 1}/{retries} in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        raise last_error
    
    def get_model(self, size: str = "medium") -> str:
        """Get model name by size category."""
        return self.MODELS.get(size, self.MODELS.get("medium", ""))