# analysis/providers/openai_provider.py
"""OpenAI LLM provider implementation."""

import os
from typing import Optional
from openai import OpenAI, AsyncOpenAI

from analysis.llm_provider import BaseLLMProvider
from models.llm_models import LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation."""
    
    MODELS = {
        "small": "gpt-4o-mini",
        "medium": "gpt-4o-mini",
        "large": "gpt-4o",
    }
    
    def __init__(self, api_key: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 2500):
        """Initialize OpenAI provider."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY or pass api_key parameter.")
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate(self, prompt: str, model: str = None) -> LLMResponse:
        """Generate response asynchronously."""
        model = model or self.MODELS["medium"]
        
        response = await self.async_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            tokens_used=response.usage.total_tokens,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens
        )
    
    def generate_sync(self, prompt: str, model: str = None) -> LLMResponse:
        """Generate response synchronously."""
        model = model or self.MODELS["medium"]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            tokens_used=response.usage.total_tokens,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens
        )