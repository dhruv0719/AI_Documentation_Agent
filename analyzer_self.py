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
        """
        # select model
        model = self._select_model_for_file(parsed_file)
        print(f"Analyzing {parsed_file.file_path} using model: {model}")

        # prompt setup
        prompt = self._build_module_prompt(parsed_file)

        # call LLM
        response = self._call_llm(prompt, model=model)

        # parse response into ModuleSummary
        return self._parse_module_response(response, parsed_file)

    def _select_model_for_file(self, parsed_file: ParsedFile) -> str:
        """
        Select an model base on the complexity of the parsed file.
        """
        num_classes = len(parsed_file.classes)
        num_functions = len(parsed_file.functions)
        
        total_elements = num_classes + num_functions

        if total_elements <= 5:
            return self.SMALL_MODEL
        elif total_elements <= 20:
            return self.MEDIUM_MODEL
        else:
            return self.LARGE_MODEL

    def _build_module_prompt(self, parsed_file: ParsedFile) -> str:
        """
        Build a prompt for the LLM based on the parsed file information.
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

Module Docstring:
{parsed_file.module_docstring or "None"}

Classes:
{classes_info if classes_info else "None"}

Functions:
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

Respond with ONLY the JSON object, nothing else.
"""
        return prompt
    

    def _call_llm(self, prompt: str, model: str) -> str:
        """
        Call the LLM with the given prompt and model.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user",
                     "content": prompt
                    }
                ],
                max_tokens=2500,
                temperature=0.2
            )
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "{}"  # Return empty JSON on error
        
    def _parse_module_response(self, response: str, parsed_file: ParsedFile) -> ModuleSummary:
        """
        Parse the LLM response into a ModuleSummary object.
        """
        try:
            data = json.loads(response)
            return ModuleSummary(
                file_path=parsed_file.file_path,
                purpose=data.get("purpose", "No purpose provided"),
                responsibilities=data.get("responsibilities", []),
                key_components=data.get("key_components", []),
                dependencies=parsed_file.imports
            )
        
        except json.JSONDecodeError:
            print(f"Error parsing LLM response for {parsed_file.file_path}. Response was not valid JSON.")
            return ModuleSummary(
                file_path=parsed_file.file_path,
                purpose="No purpose provided",
                responsibilities=[],
                key_components=[],
                dependencies=parsed_file.imports
            )