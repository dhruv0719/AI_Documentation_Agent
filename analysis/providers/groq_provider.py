# analysis/providers/groq_provider.py
"""Groq LLM provider implementation."""

import os
from typing import Optional
from groq import Groq, AsyncGroq

from analysis.llm_provider import BaseLLMProvider
from models.llm_models import LLMResponse, LLMProviderError


class GroqProvider(BaseLLMProvider):
    """Groq API provider implementation."""

    # Model mappings
    MODELS = {
        "small": "qwen/qwen3-32b",
        "medium": "openai/gpt-oss-20b",
        "large": "llama-3.3-70b-versatile",
    }
    def __init__(self, api_key: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 2500):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key (reads from GROQ_API_KEY env var if not provided)
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY or pass api_key parameter.")
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize clients
        self.client = Groq(api_key=self.api_key)
        self.async_client = AsyncGroq(api_key=self.api_key)

    def _build_messages(self, prompt: str, system_prompt: str = None) -> list:
        """Build message list with system prompt."""
        messages = []
        
        sys_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    async def generate(
        self, 
        prompt: str, 
        model: str = None,
        system_prompt: str = None
    ) -> LLMResponse:
        """Generate response asynchronously."""
        model = model or self.MODELS["medium"]
        messages = self._build_messages(prompt, system_prompt)
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0
            )
        
        except Exception as e:
            raise LLMProviderError(f"Groq API error: {e}") from e
    
    def generate_sync(
        self, 
        prompt: str, 
        model: str = None,
        system_prompt: str = None
    ) -> LLMResponse:
        """Generate response synchronously."""
        model = model or self.MODELS["medium"]
        messages = self._build_messages(prompt, system_prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0
            )
        
        except Exception as e:
            raise LLMProviderError(f"Groq API error: {e}") from e