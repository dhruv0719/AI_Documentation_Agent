# analysis/analyzer.py
"""Code analyzer using LLM for understanding and documentation."""

import json
import asyncio
from typing import List, Optional

from models.parsed_file import ParsedFile, ModuleSummary, ProjectAnalysis
from analysis.provider_factory import get_llm_provider, get_llm_provider_from_config
from analysis.llm_provider import BaseLLMProvider
from models.config_models import LLMConfig


_LANGUAGE_LABELS = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
}


def _language_label(parsed_file: ParsedFile) -> str:
    """Human-readable language name for prompt text.

    Previously this was hardcoded as "Python" everywhere, which told the LLM
    it was looking at Python even when analyzing JS/TS files - producing
    confused or wrong descriptions (e.g. calling arrow functions "lambdas",
    or describing JSX/TS-specific patterns incorrectly).
    """
    lang = parsed_file.language
    lang_value = lang.value if hasattr(lang, "value") else str(lang)
    return _LANGUAGE_LABELS.get(lang_value, lang_value.capitalize() if lang_value else "source")


class CodeAnalyzer:
    """
    Analyzes code using LLM to generate summaries and insights.

    Supports both sync and async operation for flexibility.
    """

    def __init__(
        self,
        provider: str = "groq",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2500
    ):
        self.llm: BaseLLMProvider = get_llm_provider(
            provider=provider,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.total_tokens_used = 0

    @classmethod
    def from_config(cls, llm_config: LLMConfig) -> 'CodeAnalyzer':
        instance = cls.__new__(cls)
        instance.llm = get_llm_provider_from_config(llm_config)
        instance.total_tokens_used = 0
        return instance

    # ============================================================
    # SYNC METHODS
    # ============================================================

    def analyze_module(self, parsed_file: ParsedFile) -> ModuleSummary:
        """Analyze a single module synchronously."""
        model_size = self._select_model_size(parsed_file)
        model = self.llm.MODELS[model_size]

        print(f"  Analyzing {parsed_file.file_path} [{model_size}]...")

        prompt = self._build_module_prompt(parsed_file)

        try:
            response = self.llm.generate_sync(prompt, model)
            self.total_tokens_used += response.tokens_used
            return self._parse_module_response(response.content, parsed_file)
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            return self._empty_summary(parsed_file)

    def synthesize_project(
        self,
        module_summaries: List[ModuleSummary],
        project_path: str,
        languages: Optional[List[str]] = None
    ) -> ProjectAnalysis:
        """Synthesize project-level understanding synchronously.

        Args:
            module_summaries: Per-module summaries to synthesize.
            project_path: Path to the project root.
            languages: Distinct languages detected in the project (e.g. from
                ScanResult.languages). Optional and backward-compatible -
                when omitted, the prompt stays language-neutral rather than
                assuming Python.
        """
        print(f"\n  Synthesizing project overview...")

        prompt = self._build_synthesis_prompt(module_summaries, project_path, languages)

        try:
            response = self.llm.generate_sync(prompt, self.llm.MODELS["large"])
            self.total_tokens_used += response.tokens_used
            return self._parse_synthesis_response(response.content)
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            return self._empty_project_analysis()

    # ============================================================
    # ASYNC METHODS (Faster for batch processing)
    # ============================================================

    async def analyze_module_async(self, parsed_file: ParsedFile) -> ModuleSummary:
        """Analyze a single module asynchronously."""
        model_size = self._select_model_size(parsed_file)
        model = self.llm.MODELS[model_size]

        prompt = self._build_module_prompt(parsed_file)

        try:
            response = await self.llm.generate(prompt, model)
            self.total_tokens_used += response.tokens_used
            return self._parse_module_response(response.content, parsed_file)
        except Exception as e:
            print(f"  ⚠ Error analyzing {parsed_file.file_path}: {e}")
            return self._empty_summary(parsed_file)

    async def analyze_modules_async(
        self,
        parsed_files: List[ParsedFile],
        max_concurrent: int = 5
    ) -> List[ModuleSummary]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_with_limit(pf: ParsedFile) -> ModuleSummary:
            async with semaphore:
                return await self.analyze_module_async(pf)

        tasks = [analyze_with_limit(pf) for pf in parsed_files]
        return await asyncio.gather(*tasks)

    # ============================================================
    # PROMPT BUILDERS (Private)
    # ============================================================

    def _build_module_prompt(self, parsed_file: ParsedFile) -> str:
        """Build prompt for module analysis."""

        language_label = _language_label(parsed_file)

        classes_info = ""
        for cls in parsed_file.classes:
            methods = [m.name for m in cls.methods]
            classes_info += f"  - {cls.name}: methods={methods}\n"

        functions_info = ""
        for func in parsed_file.functions:
            params = func.params if isinstance(func.params, list) else []
            if params and hasattr(params[0], 'name'):
                param_str = ", ".join(p.name for p in params)
            else:
                param_str = ", ".join(str(p) for p in params)
            functions_info += f"  - {func.name}({param_str})\n"

        import_strs = []
        for imp in parsed_file.imports:
            if hasattr(imp, 'module'):
                import_strs.append(imp.module)
            else:
                import_strs.append(str(imp))

        prompt = f"""Analyze this {language_label} module and respond with ONLY a JSON object.

FILE: {parsed_file.file_path}

DOCSTRING: {parsed_file.module_docstring or "None"}

IMPORTS: {', '.join(import_strs) if import_strs else "None"}

CLASSES ({len(parsed_file.classes)}):
{classes_info or "  None"}

FUNCTIONS ({len(parsed_file.functions)}):
{functions_info or "  None"}

Respond with this exact JSON format:
{{
  "purpose": "1-2 sentence description of what this module does",
  "responsibilities": ["responsibility 1", "responsibility 2"],
  "key_components": ["component 1", "component 2"]
}}

ONLY output the JSON. No markdown, no explanation."""

        return prompt

    def _build_synthesis_prompt(
        self,
        module_summaries: List[ModuleSummary],
        project_path: str,
        languages: Optional[List[str]] = None
    ) -> str:
        """Build prompt for project synthesis."""

        modules_info = "\n\n".join([
            f"**{s.file_path}**\n"
            f"  Purpose: {s.purpose}\n"
            f"  Responsibilities: {', '.join(s.responsibilities)}\n"
            f"  Components: {', '.join(s.key_components)}"
            for s in module_summaries
        ])

        if languages:
            labels = [_LANGUAGE_LABELS.get(l, l.capitalize()) for l in languages]
            if len(labels) == 1:
                language_line = f"This is a {labels[0]} project."
            else:
                language_line = f"This project uses multiple languages: {', '.join(labels)}."
        else:
            language_line = ""

        prompt = f"""You are a senior software architect. Analyze this software project.
{language_line}

PROJECT: {project_path}

MODULES ({len(module_summaries)}):
{modules_info}

Respond with this exact JSON format:
{{
  "project_purpose": "What this project does and why",
  "architecture_overview": "How the project is structured",
  "entry_points": ["main.py", "cli.py"],
  "module_relationships": "How modules connect and data flows",
  "design_patterns": ["Pattern 1", "Pattern 2"]
}}

ONLY output the JSON. No markdown, no explanation."""

        return prompt

    # ============================================================
    # RESPONSE PARSERS (Private)
    # ============================================================

    def _parse_module_response(
        self,
        response: str,
        parsed_file: ParsedFile
    ) -> ModuleSummary:
        try:
            cleaned = self._clean_llm_response(response)
            data = json.loads(cleaned)

            dependencies = []
            for imp in parsed_file.imports:
                if hasattr(imp, 'module'):
                    dependencies.append(imp.module)
                else:
                    dependencies.append(str(imp))

            return ModuleSummary(
                file_path=parsed_file.file_path,
                purpose=data.get("purpose", "N/A"),
                responsibilities=data.get("responsibilities", []),
                key_components=data.get("key_components", []),
                dependencies=dependencies
            )
        except json.JSONDecodeError as e:
            print(f"    JSON parse error: {e}")
            return self._empty_summary(parsed_file)

    def _parse_synthesis_response(self, response: str) -> ProjectAnalysis:
        try:
            cleaned = self._clean_llm_response(response)
            data = json.loads(cleaned)

            return ProjectAnalysis(
                project_purpose=data.get("project_purpose", "N/A"),
                architecture_overview=data.get("architecture_overview", "N/A"),
                entry_points=data.get("entry_points", []),
                module_relationships=data.get("module_relationships", "N/A"),
                design_patterns=data.get("design_patterns", [])
            )
        except json.JSONDecodeError as e:
            print(f"    JSON parse error in synthesis: {e}")
            return self._empty_project_analysis()

    def _clean_llm_response(self, response: str) -> str:
        cleaned = response.strip()

        if "<think>" in cleaned:
            cleaned = cleaned.split("</think>")[-1].strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return cleaned.strip()

    # ============================================================
    # HELPERS (Private)
    # ============================================================

    def _select_model_size(self, parsed_file: ParsedFile) -> str:
        total = len(parsed_file.classes) + len(parsed_file.functions)

        if total <= 3:
            return "small"
        elif total <= 10:
            return "medium"
        else:
            return "large"

    def _empty_summary(self, parsed_file: ParsedFile) -> ModuleSummary:
        return ModuleSummary(
            file_path=parsed_file.file_path,
            purpose="Analysis failed",
            responsibilities=[],
            key_components=[],
            dependencies=[]
        )

    def _empty_project_analysis(self) -> ProjectAnalysis:
        return ProjectAnalysis(
            project_purpose="Analysis failed",
            architecture_overview="",
            entry_points=[],
            module_relationships="",
            design_patterns=[]
        )