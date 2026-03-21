"""Task execution tasks for code and test generation."""

import asyncio
import subprocess
from datetime import datetime, timezone

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
    name="app.celery.tasks.execution.execute_code_generation",
)
def execute_code_generation(
    self,
    task_id: str,
    project_id: str,
    requirement_id: str | None = None,
    code_generation_type: str = "feature",
) -> dict:
    """Execute code generation for a task.

    Args:
        task_id: Task ID to execute
        project_id: Project ID
        requirement_id: Optional requirement ID
        code_generation_type: Type of code to generate (feature, refactor, etc.)

    Returns:
        dict with execution result
    """
    task_record = create_task_record(
        task_id=self.request.id,
        task_name="execute_code_generation",
        task_type="code_generation",
        project_id=project_id,
        requirement_id=requirement_id,
        metadata={
            "task_id": task_id,
            "code_generation_type": code_generation_type,
        },
    )

    update_task_state(task_record["id"], state=TaskState.STARTED.value, progress=10)

    # Update the main task status
    _update_main_task_status(task_id, "running")

    try:
        # Simulate code generation process
        update_task_state(task_record["id"], progress=30)

        # In production, this would call Claude Code API
        result = _run_code_generation(task_id, project_id, code_generation_type)

        update_task_state(task_record["id"], progress=90, result=result)

        # Update main task to completed
        _update_main_task_status(task_id, "completed", result=result)

        return result

    except Exception as e:
        error_result = {
            "error": str(e),
            "task_id": task_id,
        }
        update_task_state(task_record["id"], state=TaskState.FAILURE.value, error=str(e))
        _update_main_task_status(task_id, "failed", error=str(e))
        return error_result


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.celery.tasks.execution.execute_test_generation",
)
def execute_test_generation(
    self,
    task_id: str,
    project_id: str,
    requirement_id: str | None = None,
    test_type: str = "unit",
) -> dict:
    """Execute test generation for a task.

    Args:
        task_id: Task ID to execute
        project_id: Project ID
        requirement_id: Optional requirement ID
        test_type: Type of tests to generate (unit, integration, e2e)

    Returns:
        dict with execution result
    """
    task_record = create_task_record(
        task_id=self.request.id,
        task_name="execute_test_generation",
        task_type="test_generation",
        project_id=project_id,
        requirement_id=requirement_id,
        metadata={
            "task_id": task_id,
            "test_type": test_type,
        },
    )

    update_task_state(task_record["id"], state=TaskState.STARTED.value, progress=10)

    _update_main_task_status(task_id, "running")

    try:
        update_task_state(task_record["id"], progress=30)

        # Simulate test generation
        result = _run_test_generation(task_id, project_id, test_type)

        update_task_state(task_record["id"], progress=90, result=result)

        _update_main_task_status(task_id, "completed", result=result)

        return result

    except Exception as e:
        error_result = {"error": str(e), "task_id": task_id}
        update_task_state(task_record["id"], state=TaskState.FAILURE.value, error=str(e))
        _update_main_task_status(task_id, "failed", error=str(e))
        return error_result


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.celery.tasks.execution.execute_task_chain",
)
def execute_task_chain(
    self,
    task_ids: list[str],
    project_id: str,
) -> dict:
    """Execute a chain of tasks in sequence.

    Args:
        task_ids: List of task IDs to execute in order
        project_id: Project ID

    Returns:
        dict with execution results for all tasks
    """
    task_record = create_task_record(
        task_id=self.request.id,
        task_name="execute_task_chain",
        task_type="task_chain",
        project_id=project_id,
        metadata={"task_ids": task_ids},
    )

    update_task_state(task_record["id"], state=TaskState.STARTED.value)

    results = []
    for i, task_id in enumerate(task_ids):
        update_task_state(
            task_record["id"],
            progress=int((i / len(task_ids)) * 100),
        )

        # Execute each task in the chain
        result = execute_code_generation(task_id, project_id)
        results.append({
            "task_id": task_id,
            "result": result,
        })

        # Check if any task failed
        if result.get("error"):
            update_task_state(
                task_record["id"],
                state=TaskState.FAILURE.value,
                error=f"Task {task_id} failed",
            )
            break

    update_task_state(task_record["id"], progress=100, result=results)

    return {
        "task_ids": task_ids,
        "results": results,
    }


def _update_main_task_status(
    task_id: str,
    status: str,
    result: dict | None = None,
    error: str | None = None,
):
    """Update the main task status in the tasks store."""
    try:
        from app.api.v1.tasks import _tasks_store

        if task_id in _tasks_store:
            _tasks_store[task_id]["status"] = status
            if status == "running":
                _tasks_store[task_id]["started_at"] = datetime.now(timezone.utc)
            elif status in ("completed", "failed"):
                _tasks_store[task_id]["completed_at"] = datetime.now(timezone.utc)
                _tasks_store[task_id]["progress"] = 100 if status == "completed" else _tasks_store[task_id].get("progress", 0)

            if result:
                _tasks_store[task_id]["last_result"] = result
            if error:
                _tasks_store[task_id]["last_error"] = error

            # Broadcast update
            from app.api.websocket import broadcast_task_update
            broadcast_task_update(task_id, _tasks_store[task_id])
    except Exception:
        pass


def _run_code_generation(task_id: str, project_id: str, generation_type: str) -> dict:
    """Run code generation (simulated)."""
    # Simulate processing time
    import time
    time.sleep(0.1)

    # In production, this would actually call Claude Code
    return {
        "task_id": task_id,
        "project_id": project_id,
        "generation_type": generation_type,
        "files_created": [
            f"/generated/{project_id}/src/features/{task_id}/index.ts",
            f"/generated/{project_id}/src/features/{task_id}/types.ts",
        ],
        "stdout": "Code generation completed successfully",
        "returncode": 0,
    }


def _run_test_generation(task_id: str, project_id: str, test_type: str) -> dict:
    """Run test generation (simulated)."""
    import time
    time.sleep(0.1)

    return {
        "task_id": task_id,
        "project_id": project_id,
        "test_type": test_type,
        "files_created": [
            f"/generated/{project_id}/src/features/{task_id}/__tests__/index.test.ts",
        ],
        "stdout": "Test generation completed successfully",
        "returncode": 0,
    }
