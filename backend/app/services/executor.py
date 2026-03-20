"""Task executor service for running Claude Code tasks."""

import asyncio
import subprocess
import uuid
from datetime import datetime, timezone
from typing import Any

# In-memory task storage
_tasks_db: dict[str, dict] = {}


class TaskStatus:
    """Task execution status constants."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def create_task(
    task_id: str,
    command: str,
    project_id: str | None = None,
    requirement_id: str | None = None,
) -> dict:
    """Create a new task record."""
    now = datetime.now(timezone.utc)

    task = {
        "id": task_id,
        "project_id": project_id,
        "requirement_id": requirement_id,
        "command": command,
        "status": TaskStatus.PENDING,
        "result": None,
        "error": None,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
    }

    _tasks_db[task_id] = task
    return task


def get_task(task_id: str) -> dict | None:
    """Get task by ID."""
    return _tasks_db.get(task_id)


def update_task_status(
    task_id: str,
    status: str,
    result: Any = None,
    error: str | None = None,
) -> dict | None:
    """Update task status and result."""
    task = _tasks_db.get(task_id)
    if not task:
        return None

    now = datetime.now(timezone.utc)
    task["status"] = status
    task["result"] = result
    task["error"] = error

    if status == TaskStatus.RUNNING:
        task["started_at"] = now
    elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
        task["completed_at"] = now

    # Broadcast update via WebSocket
    try:
        from app.api.websocket import broadcast_execution_update
        broadcast_execution_update(
            task_id=task.get("project_id", ""),
            execution_id=task_id,
            status=status,
            result=result,
            error=error,
        )
    except Exception:
        pass

    return task


async def execute_task(
    task_id: str,
    command: str,
    working_dir: str | None = None,
    timeout: int = 300,
) -> dict:
    """Execute a Claude Code task using subprocess.

    Args:
        task_id: Unique task identifier
        command: The command/skill to execute (e.g., 'claude-code-clawdbot-skill')
        working_dir: Working directory for the command
        timeout: Timeout in seconds (default 300 = 5 minutes)

    Returns:
        dict with execution result including returncode, stdout, stderr
    """
    # Update task to running
    update_task_status(task_id, TaskStatus.RUNNING)

    try:
        # Build the command to execute
        # The claude-code-clawdbot-skill script is expected to be in PATH
        cmd = ["claude-code-clawdbot-skill"]

        # Run subprocess asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

            returncode = process.returncode

            result = {
                "returncode": returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
            }

            if returncode == 0:
                update_task_status(task_id, TaskStatus.COMPLETED, result=result)
            else:
                update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    result=result,
                    error=f"Command failed with return code {returncode}",
                )

            return result

        except asyncio.TimeoutError:
            # Kill the process on timeout
            process.kill()
            await process.wait()

            update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=f"Command timed out after {timeout} seconds",
            )

            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
            }

    except FileNotFoundError:
        error_msg = f"Command not found: claude-code-clawdbot-skill"
        update_task_status(task_id, TaskStatus.FAILED, error=error_msg)

        return {
            "returncode": -1,
            "stdout": "",
            "stderr": error_msg,
        }

    except Exception as e:
        error_msg = f"Execution error: {str(e)}"
        update_task_status(task_id, TaskStatus.FAILED, error=error_msg)

        return {
            "returncode": -1,
            "stdout": "",
            "stderr": error_msg,
        }


def execute_task_sync(
    task_id: str,
    command: str,
    working_dir: str | None = None,
    timeout: int = 300,
) -> dict:
    """Synchronous wrapper for execute_task."""
    return asyncio.run(execute_task(task_id, command, working_dir, timeout))
