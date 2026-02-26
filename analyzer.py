# analyzer.py
"""This module handles LLM-based analysis of parsed code to generate summaries and insights."""
import os
import json
from groq import Groq
from typing import List
from models import ParsedFile, ModuleSummary, ProjectAnalysis
from parser import parse_file
from scanner import scan_project
from generator import DocumentationGenerator

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
        # print(f"LLM response for {parsed_file.file_path}:\n{response}\n")

        # Parse response into ModuleSummary
        return self._parse_module_response(response, parsed_file)

    def synthesize_project(self, module_summaries: List[ModuleSummary], project_path: str) -> ProjectAnalysis:
        """
        Synthesize project-level understanding from module summaries.
    
        Args:
            module_summaries: List of all module summaries
            project_path: Root path of the project

        Returns:
            ProjectAnalysis with high-level insights
        """
        print(f"\n{'='*60}")
        print(f"SYNTHESIZING PROJECT OVERVIEW")
        print(f"Using model: {self.LARGE_MODEL}")
        print(f"{'='*60}")

        prompt = self._build_synsthesize_prompt(module_summaries, project_path)
        response = self._call_llm(prompt, model=self.LARGE_MODEL)

        return self._parse_synthesis_response(response)

    
    def _build_synsthesize_prompt(self, module_summaries: List[ModuleSummary], project_path: str) -> str:
        """Build a prompt to synthesize project-level insights."""

        modules_info = "\n\n".join([
            f"**{summary.file_path}**\n"
            f"  Purpose: {summary.purpose}\n"
            f"  Responsibilities: {', '.join(summary.responsibilities)}\n"
            f"  Key Components: {', '.join(summary.key_components)}"
            for summary in module_summaries
        ])

        prompt = f"""You are a senior software architect analyzing a Python project. Based on these module summaries, provide a comprehensive project overview.
PROJECT PATH: {project_path}

MODULE SUMMARIES:
{modules_info}

Analyze how these modules work together and respond with ONLY a JSON object in this exact format:
{{
  "project_purpose": "1-2 sentences explaining what this entire project does and why it exists",
  "architecture_overview": "2-3 sentences describing the overall architecture and how modules interact",
  "entry_points": ["main.py", "other_entry.py"],
  "module_relationships": "2-3 sentences explaining how modules depend on and interact with each other",
  "design_patterns": ["pattern1", "pattern2"]
}}

Guidelines:
- project_purpose: The "what" and "why" of the whole project
- architecture_overview: High-level structure (e.g., "CLI tool with parser→analyzer→generator pipeline")
- entry_points: Which files can be run directly (look for files that orchestrate or have main entry)
- module_relationships: How data flows between modules
- design_patterns: Any clear patterns used (e.g., "Factory", "Strategy", "Pipeline", "Modular design")

IMPORTANT: Respond with ONLY the JSON object. No markdown, no explanations, no code fences."""
    
        return prompt
    
    def _parse_synthesis_response(self, response: str) -> ProjectAnalysis:
        """Parse the LLM response from project synthesis."""
        try:
            # Clean response (same as module parsing)
            cleaned = response.strip()
            
            if "<think>" in cleaned:
                cleaned = cleaned.split("</think>")[-1].strip()
            
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.replace("```", "").strip()
            
            data = json.loads(cleaned)
            
            return ProjectAnalysis(
                project_purpose=data.get("project_purpose", "N/A"),
                architecture_overview=data.get("architecture_overview", "N/A"),
                entry_points=data.get("entry_points", []),
                module_relationships=data.get("module_relationships", "N/A"),
                design_patterns=data.get("design_patterns", [])
            )
    
        except json.JSONDecodeError as e:
            print(f"Failed to parse synthesis response: {e}")
            return ProjectAnalysis(
                project_purpose="Parse error",
                architecture_overview="Parse error",
                entry_points=[],
                module_relationships="Parse error",
                design_patterns=[]
            )
    
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
            # Clean response - remove <think> tags and markdown code blocks
            cleaned = response.strip()

            # Remove <think>...</think> blocks
            if "<think>" in cleaned:
                cleaned = cleaned.split("</think>")[-1].strip()

            # Remove markdown code fences if present
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.replace("```", "").strip()
            
            data = json.loads(cleaned)
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

if __name__ == "__main__":
    project_root = r"D:\AI_Documentation_Agent"
    project_name = "AI Documentation Agent"
    
    files = scan_project(project_root, ignore_dirs=["venv", ".venv", "__pycache__"])
    
    print(f"Found {len(files)} Python files\n")
    
    analyzer = CodeAnalyzer()
    all_summaries = []
    
    # Analyze all modules
    for file_path in files:
        parsed = parse_file(file_path, project_root)
        if parsed:
            summary = analyzer.analyze_module(parsed)
            all_summaries.append(summary)
            
            print("\n" + "="*60)
            print(f"Analysis of {summary.file_path}")
            print("="*60)
            print(f"\nPurpose: {summary.purpose}")
    
    print(f"\n{'='*60}")
    print(f"COMPLETED: Analyzed {len(all_summaries)} files")
    print(f"{'='*60}")
    
    # Synthesize project
    project_analysis = analyzer.synthesize_project(all_summaries, project_root)
    
    print(f"\n{'='*60}")
    print("PROJECT ANALYSIS")
    print(f"{'='*60}")
    print(f"\nPurpose: {project_analysis.project_purpose}")
    
    # Generate documentation
    print(f"\n{'='*60}")
    print("GENERATING DOCUMENTATION")
    print(f"{'='*60}\n")
    
    doc_generator = DocumentationGenerator(output_dir="output")
    generated_files = doc_generator.generate_all(project_analysis, all_summaries, project_name)
    
    print(f"✓ Generated README: {generated_files['readme']}")
    print(f"✓ Generated Technical Doc: {generated_files['technical_doc']}")
    print(f"\nDocumentation files saved to: output/")