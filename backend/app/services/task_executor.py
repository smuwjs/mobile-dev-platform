"""Task executor service for running development tasks."""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from app.celery.config import celery_app


class ExecutorTaskType(str, Enum):
    """Types of tasks that can be executed."""

    CODE_GENERATION = "code_generation"
    TEST_GENERATION = "test_generation"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"


class ExecutorStatus(str, Enum):
    """Executor task status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """Result of a task execution."""

    task_id: str
    executor_task_id: str
    status: ExecutorStatus
    returncode: int | None
    stdout: str
    stderr: str
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ExecutorTask:
    """A task to be executed by the executor."""

    id: str
    task_type: ExecutorTaskType
    project_id: str
    requirement_id: str | None = None
    command: str | None = None
    working_dir: str | None = None
    timeout: int = 300
    priority: int = 3
    dependencies: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    celery_task_id: str | None = None


class TaskExecutorService:
    """Service for executing development tasks.

    Provides:
    - Task queuing and execution
    - Progress tracking
    - Result storage
    - Dependency management
    """

    def __init__(self):
        """Initialize the task executor service."""
        self._tasks: dict[str, ExecutorTask] = {}
        self._results: dict[str, ExecutionResult] = {}
        self._progress_callbacks: list[Callable] = []

    def submit_task(
        self,
        task_type: ExecutorTaskType,
        project_id: str,
        requirement_id: str | None = None,
        command: str | None = None,
        working_dir: str | None = None,
        timeout: int = 300,
        priority: int = 3,
        dependencies: list[str] | None = None,
        metadata: dict | None = None,
    ) -> str:
        """Submit a task for execution.

        Args:
            task_type: Type of task to execute
            project_id: Project ID
            requirement_id: Optional requirement ID
            command: Command to execute (if None, uses default for task_type)
            working_dir: Working directory
            timeout: Timeout in seconds
            priority: Task priority (1=highest, 5=lowest)
            dependencies: List of task IDs this task depends on
            metadata: Additional metadata

        Returns:
            Task ID for tracking
        """
        task_id = str(uuid.uuid4())

        # Determine command based on task type if not provided
        if command is None:
            command = self._get_default_command(task_type)

        task = ExecutorTask(
            id=task_id,
            task_type=task_type,
            project_id=project_id,
            requirement_id=requirement_id,
            command=command,
            working_dir=working_dir,
            timeout=timeout,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        self._tasks[task_id] = task

        # Create initial result
        self._results[task_id] = ExecutionResult(
            task_id=task_id,
            executor_task_id="",
            status=ExecutorStatus.PENDING,
            returncode=None,
            stdout="",
            stderr="",
            started_at=None,
            completed_at=None,
        )

        # Queue the task for execution
        self._queue_task(task_id)

        return task_id

    def _get_default_command(self, task_type: ExecutorTaskType) -> str:
        """Get the default command for a task type."""
        commands = {
            ExecutorTaskType.CODE_GENERATION: "claude-code --generate-code",
            ExecutorTaskType.TEST_GENERATION: "claude-code --generate-tests",
            ExecutorTaskType.REFACTORING: "claude-code --refactor",
            ExecutorTaskType.DOCUMENTATION: "claude-code --document",
            ExecutorTaskType.DEPLOYMENT: "claude-code --deploy",
        }
        return commands.get(task_type, "claude-code")

    def _queue_task(self, task_id: str):
        """Queue a task for execution via Celery."""
        task = self._tasks.get(task_id)
        if not task:
            return

        # Determine Celery queue based on task type
        queue_map = {
            ExecutorTaskType.CODE_GENERATION: "code_generation",
            ExecutorTaskType.TEST_GENERATION: "test_generation",
        }
        queue = queue_map.get(task.task_type, "default")

        # Import and call Celery task
        if task.task_type == ExecutorTaskType.CODE_GENERATION:
            from app.celery.tasks.execution import execute_code_generation
            celery_task = execute_code_generation.apply_async(
                args=[task_id, task.project_id, task.requirement_id],
                kwargs={"code_generation_type": task.task_type.value},
                queue=queue,
            )
        elif task.task_type == ExecutorTaskType.TEST_GENERATION:
            from app.celery.tasks.execution import execute_test_generation
            celery_task = execute_test_generation.apply_async(
                args=[task_id, task.project_id, task.requirement_id],
                kwargs={"test_type": "unit"},
                queue=queue,
            )
        else:
            # Generic execution
            from app.celery.tasks.execution import execute_code_generation
            celery_task = execute_code_generation.apply_async(
                args=[task_id, task.project_id, task.requirement_id],
                queue=queue,
            )

        task.celery_task_id = celery_task.id
        self._results[task_id].executor_task_id = celery_task.id
        self._results[task_id].status = ExecutorStatus.QUEUED

    def get_task_status(self, task_id: str) -> ExecutionResult | None:
        """Get the status and result of a task.

        Args:
            task_id: Task ID

        Returns:
            ExecutionResult or None if not found
        """
        return self._results.get(task_id)

    def get_task(self, task_id: str) -> ExecutorTask | None:
        """Get task details.

        Args:
            task_id: Task ID

        Returns:
            ExecutorTask or None if not found
        """
        return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task.

        Args:
            task_id: Task ID

        Returns:
            True if cancelled, False if not found or already completed
        """
        task = self._tasks.get(task_id)
        result = self._results.get(task_id)

        if not task or not result:
            return False

        if result.status in (ExecutorStatus.COMPLETED, ExecutorStatus.FAILED, ExecutorStatus.CANCELLED):
            return False

        # Revoke Celery task if running
        if task.celery_task_id:
            celery_app.control.revoke(task.celery_task_id, terminate=True)

        result.status = ExecutorStatus.CANCELLED
        result.completed_at = datetime.now(timezone.utc)

        return True

    def update_progress(
        self,
        task_id: str,
        progress: int,
        status: str | None = None,
    ):
        """Update task progress.

        Args:
            task_id: Task ID
            progress: Progress percentage (0-100)
            status: Optional status update
        """
        if task_id in self._results:
            result = self._results[task_id]
            result.metadata["progress"] = progress
            if status:
                result.status = ExecutorStatus(status)

            # Notify callbacks
            for callback in self._progress_callbacks:
                try:
                    callback(task_id, progress, status)
                except Exception:
                    pass

    def on_progress(self, callback: Callable):
        """Register a progress callback.

        Args:
            callback: Function(task_id, progress, status)
        """
        self._progress_callbacks.append(callback)

    async def execute_task_async(
        self,
        task_id: str,
        command: str,
        working_dir: str | None = None,
        timeout: int = 300,
    ) -> ExecutionResult:
        """Execute a task asynchronously.

        Args:
            task_id: Task ID
            command: Command to execute
            working_dir: Working directory
            timeout: Timeout in seconds

        Returns:
            ExecutionResult with execution details
        """
        result = self._results.get(task_id)
        if not result:
            raise ValueError(f"Task {task_id} not found")

        result.status = ExecutorStatus.RUNNING
        result.started_at = datetime.now(timezone.utc)

        try:
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )

                result.returncode = process.returncode
                result.stdout = stdout.decode() if stdout else ""
                result.stderr = stderr.decode() if stderr else ""

                if process.returncode == 0:
                    result.status = ExecutorStatus.COMPLETED
                else:
                    result.status = ExecutorStatus.FAILED
                    result.error = f"Command failed with return code {process.returncode}"

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                result.status = ExecutorStatus.FAILED
                result.error = f"Command timed out after {timeout} seconds"

        except Exception as e:
            result.status = ExecutorStatus.FAILED
            result.error = str(e)

        result.completed_at = datetime.now(timezone.utc)
        return result

    def list_tasks(
        self,
        project_id: str | None = None,
        status: ExecutorStatus | None = None,
    ) -> list[ExecutorTask]:
        """List tasks with optional filters.

        Args:
            project_id: Filter by project
            status: Filter by status

        Returns:
            List of ExecutorTask
        """
        tasks = list(self._tasks.values())

        if project_id:
            tasks = [t for t in tasks if t.project_id == project_id]

        if status:
            results = [r for r in self._results.values() if r.status == status]
            task_ids = {r.task_id for r in results}
            tasks = [t for t in tasks if t.id in task_ids]

        return sorted(tasks, key=lambda t: t.priority)


# Singleton instance
task_executor_service = TaskExecutorService()
