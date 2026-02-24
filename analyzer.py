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
        # Build detailed context
        classes_info = "\n".join([
            f" -{cls.name}: {len(cls.methods)} methods" 
            for cls in parsed_file.classes
        ])

        functions_info = "\n".join([
            f" -{func.name}({', '.join(func.params)})" 
            for func in parsed_file.functions
        ])

        prompt = f"""You are a code analysis expert. Analyze this Python module and provide insights.

FILE: {parsed_file.file_path}

MODULE DOCSTRING:
{parsed_file.module_docstring or "None"}

IMPORTS:
{', '.join(parsed_file.imports) if parsed_file.imports else "None"}

CLASSES ({len(parsed_file.classes)}):
{classes_info if classes_info else "None"}

FUNCTIONS ({len(parsed_file.functions)}):
{functions_info if functions_info else "None"}

Analyze this module and respond with ONLY a JSON object (no markdown, no explanations) in this exact format:
{{
  "purpose": "Brief 1-2 sentence explanation of what this module does",
  "responsibilities": ["responsibility 1", "responsibility 2", "responsibility 3"],
  "key_components": ["component 1", "component 2"]
}}

Remember:
- "purpose": High-level what and why
- "responsibilities": List of 2-4 main tasks this module handles
- "key_components": List of 2-4 most important classes/functions

Respond with ONLY the JSON object, nothing else."""
    
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
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""

    def _parse_module_response(self, response: str, parsed_file: ParsedFile) -> ModuleSummary:
        """
        Parse the LLM response into a ModuleSummary object.
        
        Args:
            response: The raw response from the LLM
            parsed_file: The original parsed file information for reference
            
        Returns:
            A ModuleSummary object with the extracted insights
        """
        try:
            data = json.loads(response)
            return ModuleSummary(
                file_path=parsed_file.file_path,
                purpose=data.get("purpose", "N/A"),
                responsibilities=data.get("responsibilities", []),
                key_components=data.get("key_components", []),
                dependencies=parsed_file.imports
            )
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON. Returning empty summary.")
            return ModuleSummary(
                file_path=parsed_file.file_path,
                purpose="N/A",
                responsibilities=[],
                key_components=[],
                dependencies=parsed_file.imports
            )

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

        total_items = num_classes + num_functions
        if total_items <= 5:
            return self.SMALL_MODEL
        
        elif total_items < 15:
            return self.MEDIUM_MODEL
        
        else:
            return self.LARGE_MODEL