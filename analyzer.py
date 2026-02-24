# analyzer.py
"""This module handles LLM-based analysis of parsed code to generate summaries and insights."""
import os
import json
from groq import Groq
from typing import List
from models import ParsedFile, ModuleSummary, ProjectAnalysis

class CodeAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set in environment variables or passed to CodeAnalyzer.")
        
        self.client = Groq(api_key=self.api_key)

        self.SMALL_MODEL = "qwen/qwen3-32b"
        self.MEDIUM_MODEL = "openai/gpt-oss-120b"
        self.LARGE_MODEL = "llama-3.3-70b-versatile"

    def analyze_module(self, parsed_file: ParsedFile) -> ModuleSummary:
        """
        Analyze a single module and generate summary.
        
        Args:
            parsed_file: Parsed file information
            
        Returns:
            ModuleSummary with LLM-generated insights
        """
        # Select appropriate model based on complexity
        model = self._select_model_for_file(parsed_file)
        print(f"Analyzing {parsed_file.file_path} using model: {model}")

        prompt = self._build_module_prompt(parsed_file)
        response = self._call_llm(prompt, model=model)

        # Parse response into ModuleSummary
        return self._parse_module_response(response, parsed_file)
    
    def _build_module_prompt(self, parsed_file: ParsedFile) -> str:
        """
        Build a prompt for the LLM based on the parsed file information.
        
        Args:
            parsed_file: Parsed file information
        
        Returns:
            A string prompt to send to the LLM
        """
        prompt = f"""
You are an expert software engineer analyzing a Python module. Here is the information about the module:
- File path: {parsed_file.file_path}
- Module docstring: {parsed_file.module_docstring}
- Imports: {', '.join(parsed_file.imports)}
- Classes: {', '.join(cls.name for cls in parsed_file.classes)}
- Functions: {', '.join(func.name for func in parsed_file.functions)}
"""
        return prompt
    
    def _call_llm(self, prompt: str, model: str) -> str:
        """
        Call the LLM with the given prompt and model.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The model to use for analysis
            
        Returns:
            The raw response from the LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=2500,
                temperature=0.2
            )
            return response.text
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""

    def _select_model_for_file(self, parsed_file: ParsedFile) -> str:
        """
        Select an LLM model based on the complexity of the parsed file.
        
        Args:
            parsed_file: Parsed file information
            
        Returns:
            Model name to use for analysis
        """
        num_classes = len(parsed_file.classes)
        num_functions = len(parsed_file.functions)
        num_methods = sum(len(cls.methods) for cls in parsed_file.classes)

        total_items = num_classes + num_functions + num_methods

        if total_items <= 5:
            return self.SMALL_MODEL
        
        elif total_items < 15:
            return self.MEDIUM_MODEL
        
        else:
            return self.LARGE_MODEL