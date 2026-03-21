"""Requirement analysis service for LLM-based requirement decomposition."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from app.db.models import Requirement, Task


class RequirementComplexity(int, Enum):
    """Requirement complexity levels."""

    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    VERY_COMPLEX = 5


class ValidationStatus(str, Enum):
    """Requirement validation status."""

    VALID = "valid"
    HAS_WARNINGS = "has_warnings"
    INVALID = "invalid"


@dataclass
class SubRequirement:
    """A sub-requirement derived from analysis."""

    id: str
    title: str
    description: str
    priority: int
    complexity: RequirementComplexity
    estimated_hours: float
    dependencies: list[str] = field(default_factory=list)


@dataclass
class DecompositionResult:
    """Result of requirement decomposition."""

    requirement_id: str
    original_requirement: str
    complexity: RequirementComplexity
    estimated_total_hours: float
    sub_requirements: list[SubRequirement]
    tasks: list[dict]
    validation_result: "ValidationResult"


@dataclass
class ValidationResult:
    """Result of requirement validation."""

    status: ValidationStatus
    conflicts: list[dict]
    warnings: list[str]
    suggestions: list[str]


@dataclass
class DependencyInfo:
    """Information about task dependencies."""

    task_id: str
    depends_on: list[str]
    blocked_by: list[str]
    can_start: bool


class RequirementAnalysisService:
    """Service for analyzing and decomposing requirements using LLM.

    This service provides:
    - Requirement complexity analysis
    - Automatic decomposition into sub-requirements
    - Task dependency management
    - Requirement validation and conflict detection
    """

    def __init__(self):
        """Initialize the requirement analysis service."""
        self._complexity_keywords = {
            RequirementComplexity.TRIVIAL: ["simple", "basic", "small"],
            RequirementComplexity.SIMPLE: ["create", "add", "implement"],
            RequirementComplexity.MODERATE: ["modify", "enhance", "improve"],
            RequirementComplexity.COMPLEX: ["redesign", "refactor", "integrate"],
            RequirementComplexity.VERY_COMPLEX: ["rebuild", "migrate", "transform"],
        }

    async def analyze_requirement(
        self,
        requirement_text: str,
        project_id: str,
        parent_id: str | None = None,
    ) -> DecompositionResult:
        """Analyze a requirement and decompose it into actionable tasks.

        Args:
            requirement_text: The requirement description
            project_id: Project this requirement belongs to
            parent_id: Parent requirement ID if this is a sub-requirement

        Returns:
            DecompositionResult with analysis and generated tasks
        """
        # Analyze complexity
        complexity = self._analyze_complexity(requirement_text)

        # Generate sub-requirements
        sub_requirements = await self._generate_sub_requirements(
            requirement_text,
            complexity,
            project_id,
        )

        # Generate tasks from sub-requirements
        tasks = self._generate_tasks_from_sub_requirements(
            sub_requirements,
            project_id,
            parent_id,
        )

        # Validate the decomposition
        validation_result = self._validate_requirement(requirement_text, sub_requirements)

        # Calculate total estimated hours
        total_hours = sum(sub_req.estimated_hours for sub_req in sub_requirements)

        return DecompositionResult(
            requirement_id=str(uuid.uuid4()),
            original_requirement=requirement_text,
            complexity=complexity,
            estimated_total_hours=total_hours,
            sub_requirements=sub_requirements,
            tasks=tasks,
            validation_result=validation_result,
        )

    def _analyze_complexity(self, text: str) -> RequirementComplexity:
        """Analyze requirement complexity based on text content.

        In production, this would use an LLM API for more accurate analysis.
        """
        text_lower = text.lower()
        word_count = len(text.split())
        sentence_count = len([s for s in text.split(".") if s.strip()])

        # Base complexity on word count
        if word_count < 20:
            base_complexity = RequirementComplexity.TRIVIAL
        elif word_count < 50:
            base_complexity = RequirementComplexity.SIMPLE
        elif word_count < 100:
            base_complexity = RequirementComplexity.MODERATE
        elif word_count < 200:
            base_complexity = RequirementComplexity.COMPLEX
        else:
            base_complexity = RequirementComplexity.VERY_COMPLEX

        # Adjust based on keywords
        keyword_boost = 0
        for complexity, keywords in self._complexity_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    keyword_boost = max(keyword_boost, int(complexity) - int(base_complexity))

        final_complexity = min(
            RequirementComplexity.VERY_COMPLEX,
            RequirementComplexity(max(1, int(base_complexity) + keyword_boost)),
        )

        return final_complexity

    async def _generate_sub_requirements(
        self,
        requirement_text: str,
        complexity: RequirementComplexity,
        project_id: str,
    ) -> list[SubRequirement]:
        """Generate sub-requirements based on complexity.

        In production, this would call an LLM API.
        """
        sub_requirements = []
        base_id = str(uuid.uuid4())[:8]

        if complexity >= RequirementComplexity.MODERATE:
            # Add analysis sub-requirement
            sub_requirements.append(
                SubRequirement(
                    id=f"{base_id}-analysis",
                    title="Requirements Analysis and Documentation",
                    description=f"Thoroughly analyze and document the requirements: {requirement_text[:100]}...",
                    priority=1,
                    complexity=RequirementComplexity.SIMPLE,
                    estimated_hours=self._estimate_hours(RequirementComplexity.SIMPLE),
                    dependencies=[],
                )
            )

        if complexity >= RequirementComplexity.MODERATE:
            sub_requirements.append(
                SubRequirement(
                    id=f"{base_id}-design",
                    title="Technical Design and Architecture",
                    description="Create technical design, API specifications, and architecture diagrams",
                    priority=2,
                    complexity=RequirementComplexity.MODERATE,
                    estimated_hours=self._estimate_hours(RequirementComplexity.MODERATE),
                    dependencies=[f"{base_id}-analysis"],
                )
            )

        sub_requirements.append(
            SubRequirement(
                id=f"{base_id}-implementation",
                title="Core Implementation",
                description=f"Implement the main functionality for: {requirement_text[:80]}...",
                priority=3,
                complexity=complexity,
                estimated_hours=self._estimate_hours(complexity),
                dependencies=[f"{base_id}-design"] if complexity >= RequirementComplexity.MODERATE else [],
            )
        )

        sub_requirements.append(
            SubRequirement(
                id=f"{base_id}-testing",
                title="Testing and Quality Assurance",
                description="Write unit tests, integration tests, and perform QA",
                priority=4,
                complexity=RequirementComplexity.MODERATE,
                estimated_hours=self._estimate_hours(RequirementComplexity.MODERATE),
                dependencies=[f"{base_id}-implementation"],
            )
        )

        if complexity >= RequirementComplexity.COMPLEX:
            sub_requirements.append(
                SubRequirement(
                    id=f"{base_id}-review",
                    title="Code Review and Refinement",
                    description="Code review, performance optimization, and final refinements",
                    priority=5,
                    complexity=RequirementComplexity.COMPLEX,
                    estimated_hours=self._estimate_hours(RequirementComplexity.COMPLEX),
                    dependencies=[f"{base_id}-testing"],
                )
            )

        return sub_requirements

    def _estimate_hours(self, complexity: RequirementComplexity) -> float:
        """Estimate hours needed based on complexity."""
        hours_map = {
            RequirementComplexity.TRIVIAL: 1.0,
            RequirementComplexity.SIMPLE: 2.0,
            RequirementComplexity.MODERATE: 4.0,
            RequirementComplexity.COMPLEX: 8.0,
            RequirementComplexity.VERY_COMPLEX: 16.0,
        }
        return hours_map.get(complexity, 4.0)

    def _generate_tasks_from_sub_requirements(
        self,
        sub_requirements: list[SubRequirement],
        project_id: str,
        parent_requirement_id: str | None,
    ) -> list[dict]:
        """Generate actionable tasks from sub-requirements."""
        tasks = []
        for i, sub_req in enumerate(sub_requirements):
            task = {
                "id": str(uuid.uuid4()),
                "title": sub_req.title,
                "description": sub_req.description,
                "requirement_id": parent_requirement_id,
                "project_id": project_id,
                "priority": sub_req.priority,
                "task_type": "development",
                "estimated_hours": sub_req.estimated_hours,
                "sort_order": i * 10,
                "dependencies": sub_req.dependencies,
                "complexity": int(sub_req.complexity),
            }
            tasks.append(task)
        return tasks

    def _validate_requirement(
        self,
        requirement_text: str,
        sub_requirements: list[SubRequirement],
    ) -> ValidationResult:
        """Validate requirement and check for conflicts."""
        conflicts = []
        warnings = []
        suggestions = []

        text_lower = requirement_text.lower()

        # Check for contradictory terms
        if "shall not" in text_lower and "must" in text_lower:
            conflicts.append({
                "type": "contradiction",
                "severity": "high",
                "message": "Contains both restrictive ('shall not') and permissive ('must') language",
            })

        # Check for vague terms
        vague_terms = ["etc", "and so on", "possibly", "maybe", "might", "could"]
        found_vague = [t for t in vague_terms if t in text_lower]
        if found_vague:
            warnings.append(f"Contains vague terms: {', '.join(found_vague)}")

        # Check for ambiguity
        if len(requirement_text.split()) < 10:
            warnings.append("Requirement text is very short and may lack detail")

        # Check sub-requirement dependencies
        all_ids = {sub_req.id for sub_req in sub_requirements}
        for sub_req in sub_requirements:
            for dep in sub_req.dependencies:
                if dep not in all_ids:
                    conflicts.append({
                        "type": "missing_dependency",
                        "severity": "high",
                        "message": f"Sub-requirement '{sub_req.id}' depends on unknown '{dep}'",
                    })

        # Generate suggestions
        if len(sub_requirements) == 0:
            suggestions.append("Consider breaking down the requirement into smaller parts")
        if not any(sub_req.priority == 1 for sub_req in sub_requirements):
            suggestions.append("Consider adding an analysis phase as the first priority")

        # Determine status
        if conflicts:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.HAS_WARNINGS
        else:
            status = ValidationStatus.VALID

        return ValidationResult(
            status=status,
            conflicts=conflicts,
            warnings=warnings,
            suggestions=suggestions,
        )

    def analyze_dependencies(
        self,
        tasks: list[dict],
    ) -> list[DependencyInfo]:
        """Analyze dependencies between tasks and determine execution order.

        Args:
            tasks: List of task dictionaries with 'id' and 'dependencies' fields

        Returns:
            List of DependencyInfo with dependency analysis
        """
        task_ids = {task["id"] for task in tasks}
        dependency_map: dict[str, set[str]] = {}

        for task in tasks:
            deps = set(task.get("dependencies", []))
            dependency_map[task["id"]] = deps

        # Calculate blocked_by for each task
        blocked_by_map: dict[str, set[str]] = {}
        for task_id, deps in dependency_map.items():
            for other_id, other_deps in dependency_map.items():
                if task_id in other_deps:
                    if other_id not in blocked_by_map:
                        blocked_by_map[other_id] = set()
                    blocked_by_map[other_id].add(task_id)

        results = []
        for task in tasks:
            task_id = task["id"]
            deps = dependency_map.get(task_id, set())
            blocked = blocked_by_map.get(task_id, set())

            # Task can start if all its dependencies are not blocked
            can_start = not any(
                dep in blocked_by_map.get(d, set())
                for d in deps
            )

            results.append(DependencyInfo(
                task_id=task_id,
                depends_on=list(deps),
                blocked_by=list(blocked),
                can_start=can_start,
            ))

        return results


# Singleton instance
requirement_analysis_service = RequirementAnalysisService()
