"""Requirement analysis and decomposition tasks."""

from celery import chord, group
from celery.canvas import signature

from app.celery.config import celery_app
from app.celery.tasks.base import (
    CallbackTask,
    create_task_record,
    update_task_state,
    TaskState,
)


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.celery.tasks.requirement.analyze_requirement",
)
def analyze_requirement(
    self,
    requirement_id: str,
    requirement_text: str,
    project_id: str,
    parent_id: str | None = None,
):
    """Analyze a requirement and break it down into sub-requirements.

    Args:
        requirement_id: Unique identifier for this requirement
        requirement_text: The requirement description
        project_id: Project this requirement belongs to
        parent_id: Parent requirement ID if this is a sub-requirement

    Returns:
        dict with analysis results including sub-requirements
    """
    # Create task record
    task_record = create_task_record(
        task_id=self.request.id,
        task_name="analyze_requirement",
        task_type="requirement_analysis",
        project_id=project_id,
        requirement_id=requirement_id,
        parent_id=parent_id,
        metadata={"requirement_text": requirement_text},
    )

    update_task_state(task_record["id"], state=TaskState.STARTED.value)

    # Simulate LLM-based requirement analysis
    # In production, this would call an LLM API
    result = {
        "requirement_id": requirement_id,
        "analysis": {
            "complexity": _estimate_complexity(requirement_text),
            "estimated_hours": _estimate_hours(requirement_text),
            "sub_requirements": _generate_sub_requirements(requirement_text),
        },
    }

    update_task_state(task_record["id"], progress=100, result=result)

    return result


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.celery.tasks.requirement.decompose_requirement",
)
def decompose_requirement(
    self,
    requirement_id: str,
    requirement_text: str,
    project_id: str,
) -> dict:
    """Decompose a requirement into actionable tasks.

    This task coordinates the analysis and creates sub-tasks in parallel.

    Args:
        requirement_id: Unique identifier for this requirement
        requirement_text: The requirement description
        project_id: Project this requirement belongs to

    Returns:
        dict with decomposition results including task definitions
    """
    task_record = create_task_record(
        task_id=self.request.id,
        task_name="decompose_requirement",
        task_type="requirement_decomposition",
        project_id=project_id,
        requirement_id=requirement_id,
        metadata={"requirement_text": requirement_text},
    )

    update_task_state(task_record["id"], state=TaskState.STARTED.value, progress=10)

    # Step 1: Analyze the requirement
    analysis_result = analyze_requirement(
        requirement_id,
        requirement_text,
        project_id,
    )

    update_task_state(task_record["id"], progress=50)

    # Step 2: Generate actionable tasks based on analysis
    sub_reqs = analysis_result.get("analysis", {}).get("sub_requirements", [])
    tasks = _generate_tasks_from_sub_requirements(sub_reqs, project_id, requirement_id)

    update_task_state(task_record["id"], progress=90)

    result = {
        "requirement_id": requirement_id,
        "tasks": tasks,
        "sub_requirements": sub_reqs,
    }

    update_task_state(task_record["id"], progress=100, result=result)

    return result


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.celery.tasks.requirement.validate_requirement",
)
def validate_requirement(
    self,
    requirement_id: str,
    requirement_text: str,
    project_id: str,
) -> dict:
    """Validate a requirement for conflicts and consistency.

    Args:
        requirement_id: Unique identifier for this requirement
        requirement_text: The requirement description
        project_id: Project this requirement belongs to

    Returns:
        dict with validation results including any detected conflicts
    """
    task_record = create_task_record(
        task_id=self.request.id,
        task_name="validate_requirement",
        task_type="requirement_validation",
        project_id=project_id,
        requirement_id=requirement_id,
        metadata={"requirement_text": requirement_text},
    )

    update_task_state(task_record["id"], state=TaskState.STARTED.value)

    # Check for potential conflicts
    conflicts = _detect_conflicts(requirement_text)

    result = {
        "requirement_id": requirement_id,
        "valid": len(conflicts) == 0,
        "conflicts": conflicts,
    }

    update_task_state(task_record["id"], progress=100, result=result)

    return result


@celery_app.task(
    name="app.celery.tasks.requirement.batch_decompose",
)
def batch_decompose(requirement_ids: list[str], project_id: str) -> dict:
    """Decompose multiple requirements in parallel.

    Args:
        requirement_ids: List of requirement IDs to decompose
        project_id: Project these requirements belong to

    Returns:
        dict with results for all decomposed requirements
    """
    # Create a group of decompose tasks
    tasks = [
        signature(
            "app.celery.tasks.requirement.decompose_requirement",
            args=[req_id, "", project_id],
        )
        for req_id in requirement_ids
    ]

    job = group(tasks)
    results = job.apply_async()

    return {
        "group_id": str(results.id),
        "task_count": len(requirement_ids),
    }


# Helper functions for LLM-based decomposition (simulated for now)
def _estimate_complexity(text: str) -> int:
    """Estimate requirement complexity (1-5)."""
    words = len(text.split())
    if words < 20:
        return 1
    elif words < 50:
        return 2
    elif words < 100:
        return 3
    elif words < 200:
        return 4
    return 5


def _estimate_hours(text: str) -> float:
    """Estimate hours needed for requirement."""
    complexity = _estimate_complexity(text)
    base_hours = {1: 2, 2: 4, 3: 8, 4: 16, 5: 32}
    return base_hours.get(complexity, 8)


def _generate_sub_requirements(text: str) -> list[dict]:
    """Generate sub-requirements from main requirement (simulated LLM)."""
    # In production, this would call an LLM API
    complexity = _estimate_complexity(text)

    sub_reqs = []
    if complexity >= 2:
        sub_reqs.append({
            "id": f"{text[:8]}-sub1",
            "title": "Requirements Analysis",
            "description": "Analyze and document detailed requirements",
            "priority": 1,
        })
    if complexity >= 3:
        sub_reqs.append({
            "id": f"{text[:8]}-sub2",
            "title": "Design Phase",
            "description": "Create technical design and architecture",
            "priority": 2,
        })
    if complexity >= 4:
        sub_reqs.append({
            "id": f"{text[:8]}-sub3",
            "title": "Implementation",
            "description": "Implement the core functionality",
            "priority": 3,
        })
        sub_reqs.append({
            "id": f"{text[:8]}-sub4",
            "title": "Testing",
            "description": "Write and run tests",
            "priority": 3,
        })

    return sub_reqs


def _generate_tasks_from_sub_requirements(
    sub_reqs: list[dict],
    project_id: str,
    parent_requirement_id: str,
) -> list[dict]:
    """Generate actionable tasks from sub-requirements."""
    tasks = []
    for i, sub_req in enumerate(sub_reqs):
        tasks.append({
            "id": f"{sub_req['id']}-task",
            "title": sub_req["title"],
            "description": sub_req["description"],
            "requirement_id": parent_requirement_id,
            "project_id": project_id,
            "priority": sub_req.get("priority", 3),
            "task_type": "development",
            "estimated_hours": _estimate_hours(sub_req["description"]),
            "sort_order": i * 10,
        })
    return tasks


def _detect_conflicts(text: str) -> list[dict]:
    """Detect potential conflicts in requirement text (simplified)."""
    conflicts = []
    text_lower = text.lower()

    # Check for contradictory terms
    if "shall not" in text_lower and "must" in text_lower:
        conflicts.append({
            "type": "contradiction",
            "severity": "high",
            "message": "Mix of restrictive and permissive language",
        })

    # Check for vague terms
    vague_terms = ["etc", "and so on", "possibly", "maybe"]
    for term in vague_terms:
        if term in text_lower:
            conflicts.append({
                "type": "vagueness",
                "severity": "low",
                "message": f"Contains vague term: '{term}'",
            })

    return conflicts
