"""Claude Code executor service with tmux session management.

This service manages Claude Code execution through tmux sessions, providing:
- tmux session lifecycle management (create, pause, resume, terminate)
- Task step execution within tmux sessions
- Output capture and parsing
- Execution state management
"""

import asyncio
import re
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ExecutionStatus(str, Enum):
    """Execution status constants."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class TaskStepStatus(str, Enum):
    """Individual task step status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """Result of a task execution."""

    execution_id: str
    task_id: str
    session_name: str
    status: ExecutionStatus
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    progress: int = 0
    steps_completed: int = 0
    steps_total: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class TaskStep:
    """A single step within a task."""

    step_id: str
    title: str
    command: str | None = None
    description: str | None = None
    status: TaskStepStatus = TaskStepStatus.PENDING
    output: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    returncode: int | None = None


@dataclass
class TmuxSession:
    """Represents a tmux session for Claude Code execution."""

    session_name: str
    task_id: str
    execution_id: str
    working_dir: str | None = None
    created_at: datetime | None = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    pane_id: str | None = None


class TmuxManager:
    """Manages tmux sessions for Claude Code execution.

    Provides methods to create, control, and monitor tmux sessions.
    """

    SESSION_PREFIX = "claude_exec_"

    def __init__(self):
        """Initialize the tmux manager."""
        self._sessions: dict[str, TmuxSession] = {}

    def _get_session_name(self, task_id: str) -> str:
        """Generate a tmux session name for a task."""
        return f"{self.SESSION_PREFIX}{task_id[:8]}"

    def session_exists(self, session_name: str) -> bool:
        """Check if a tmux session exists."""
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
        )
        return result.returncode == 0

    def create_session(
        self,
        task_id: str,
        execution_id: str,
        working_dir: str | None = None,
    ) -> TmuxSession:
        """Create a new tmux session for a task.

        Args:
            task_id: The task identifier
            execution_id: The execution identifier
            working_dir: Optional working directory

        Returns:
            TmuxSession object with session details

        Raises:
            RuntimeError: If session creation fails
        """
        session_name = self._get_session_name(task_id)

        if self.session_exists(session_name):
            self.terminate_session(session_name)

        cmd = ["tmux", "new-session", "-d", "-s", session_name]
        if working_dir:
            cmd.extend(["-c", working_dir])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create tmux session: {result.stderr}")

        pane_id = self._get_pane_id(session_name)
        now = datetime.now(timezone.utc)

        session = TmuxSession(
            session_name=session_name,
            task_id=task_id,
            execution_id=execution_id,
            working_dir=working_dir,
            created_at=now,
            status=ExecutionStatus.PENDING,
            pane_id=pane_id,
        )

        self._sessions[session_name] = session
        return session

    def _get_pane_id(self, session_name: str) -> str | None:
        """Get the pane ID for a tmux session."""
        result = subprocess.run(
            ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
        return None

    def send_command(
        self,
        session_name: str,
        command: str,
        wait_for_response: bool = False,
        timeout: int = 30,
    ) -> tuple[int, str, str]:
        """Send a command to a tmux session.

        Args:
            session_name: The tmux session name
            command: The command to send
            wait_for_response: Whether to wait for command completion
            timeout: Timeout in seconds for waiting

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        # Escape special characters in the command
        escaped_cmd = command.replace("'", "'\\''")

        if wait_for_response:
            # Use tmux send-keys and wait for output
            proc = subprocess.Popen(
                ["tmux", "send-keys", "-t", session_name, command, "C-m"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proc.wait()

            # Capture output from the pane
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", session_name, "-p"],
                capture_output=True,
                text=True,
            )
            return (0, result.stdout, "")
        else:
            proc = subprocess.run(
                ["tmux", "send-keys", "-t", session_name, command, "C-m"],
                capture_output=True,
                text=True,
            )
            return (proc.returncode, "", "")

    def get_output(self, session_name: str, since_lines: int = 1000) -> str:
        """Capture output from a tmux session.

        Args:
            session_name: The tmux session name
            since_lines: Number of lines to capture from end

        Returns:
            The captured output as a string
        """
        result = subprocess.run(
            [
                "tmux", "capture-pane", "-t", session_name,
                "-p", "-S", f"-{since_lines}"
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout
        return ""

    def pause_session(self, session_name: str) -> bool:
        """Pause a tmux session by sending pause signal.

        Args:
            session_name: The tmux session name

        Returns:
            True if successful, False otherwise
        """
        if not self.session_exists(session_name):
            return False

        # Send SIGSTOP to the process in the tmux session
        pane_pid = self._get_pane_pid(session_name)
        if pane_pid:
            subprocess.run(["kill", "-STOP", str(pane_pid)], capture_output=True)
            if session_name in self._sessions:
                self._sessions[session_name].status = ExecutionStatus.PAUSED
            return True
        return False

    def resume_session(self, session_name: str) -> bool:
        """Resume a paused tmux session.

        Args:
            session_name: The tmux session name

        Returns:
            True if successful, False otherwise
        """
        if not self.session_exists(session_name):
            return False

        pane_pid = self._get_pane_pid(session_name)
        if pane_pid:
            subprocess.run(["kill", "-CONT", str(pane_pid)], capture_output=True)
            if session_name in self._sessions:
                self._sessions[session_name].status = ExecutionStatus.RUNNING
            return True
        return False

    def _get_pane_pid(self, session_name: str) -> int | None:
        """Get the PID of the process in a tmux pane."""
        result = subprocess.run(
            ["tmux", "display-message", "-t", session_name, "-p", "#{pane_pid}"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            try:
                return int(result.stdout.strip())
            except ValueError:
                pass
        return None

    def terminate_session(self, session_name: str) -> bool:
        """Terminate a tmux session.

        Args:
            session_name: The tmux session name

        Returns:
            True if successful, False otherwise
        """
        if not self.session_exists(session_name):
            return False

        result = subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            capture_output=True,
        )

        if result.returncode == 0:
            if session_name in self._sessions:
                self._sessions[session_name].status = ExecutionStatus.TERMINATED
                del self._sessions[session_name]
            return True
        return False

    def get_session(self, session_name: str) -> TmuxSession | None:
        """Get session info by name."""
        return self._sessions.get(session_name)

    def list_sessions(self) -> list[TmuxSession]:
        """List all managed sessions."""
        return list(self._sessions.values())


class ClaudeExecutor:
    """Service for executing Claude Code tasks via tmux sessions.

    Provides:
    - tmux session management
    - Task step execution
    - Output capture and parsing
    - Execution state management
    """

    def __init__(self):
        """Initialize the Claude executor service."""
        self._tmux = TmuxManager()
        self._executions: dict[str, ExecutionResult] = {}
        self._steps: dict[str, list[TaskStep]] = {}

    async def create_session(
        self,
        task_id: str,
        execution_id: str,
        working_dir: str | None = None,
    ) -> str:
        """Create a new tmux session for task execution.

        Args:
            task_id: The task identifier
            execution_id: The execution identifier
            working_dir: Optional working directory

        Returns:
            The tmux session name
        """
        session = self._tmux.create_session(task_id, execution_id, working_dir)

        result = ExecutionResult(
            execution_id=execution_id,
            task_id=task_id,
            session_name=session.session_name,
            status=ExecutionStatus.PENDING,
        )
        self._executions[execution_id] = result

        return session.session_name

    async def execute_task(
        self,
        execution_id: str,
        task_steps: list[dict],
    ) -> ExecutionResult:
        """Execute a task with multiple steps.

        Args:
            execution_id: The execution identifier
            task_steps: List of task step definitions

        Returns:
            ExecutionResult with execution details
        """
        result = self._executions.get(execution_id)
        if not result:
            raise ValueError(f"Execution {execution_id} not found")

        session = self._tmux.get_session(result.session_name)
        if not session:
            raise RuntimeError(f"Session {result.session_name} not found")

        result.status = ExecutionStatus.RUNNING
        result.started_at = datetime.now(timezone.utc)
        result.steps_total = len(task_steps)

        # Initialize steps
        steps = []
        for i, step_def in enumerate(task_steps):
            step = TaskStep(
                step_id=f"{execution_id}_step_{i}",
                title=step_def.get("title", f"Step {i+1}"),
                command=step_def.get("command"),
                description=step_def.get("description"),
            )
            steps.append(step)
        self._steps[execution_id] = steps

        # Execute each step
        for i, step in enumerate(steps):
            step.status = TaskStepStatus.RUNNING
            step.started_at = datetime.now(timezone.utc)
            result.steps_completed = i

            if step.command:
                returncode, stdout, stderr = self._tmux.send_command(
                    session.session_name,
                    step.command,
                    wait_for_response=True,
                )
                step.output = stdout
                step.returncode = returncode

                if returncode != 0:
                    step.status = TaskStepStatus.FAILED
                    result.status = ExecutionStatus.FAILED
                    result.stderr = stderr
                    result.error = f"Step {i+1} failed: {stderr}"
                    break
                else:
                    step.status = TaskStepStatus.COMPLETED
            else:
                step.status = TaskStepStatus.COMPLETED

            result.progress = int(((i + 1) / len(steps)) * 100)

        if result.status == ExecutionStatus.RUNNING:
            result.status = ExecutionStatus.COMPLETED

        result.completed_at = datetime.now(timezone.utc)
        return result

    async def execute_step(
        self,
        execution_id: str,
        step_index: int,
    ) -> ExecutionResult:
        """Execute a single step of a task.

        Args:
            execution_id: The execution identifier
            step_index: The step index to execute

        Returns:
            Updated ExecutionResult
        """
        result = self._executions.get(execution_id)
        if not result:
            raise ValueError(f"Execution {execution_id} not found")

        steps = self._steps.get(execution_id, [])
        if step_index >= len(steps):
            raise ValueError(f"Step {step_index} not found")

        session = self._tmux.get_session(result.session_name)
        if not session:
            raise RuntimeError(f"Session {result.session_name} not found")

        step = steps[step_index]
        step.status = TaskStepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)

        if step.command:
            returncode, stdout, stderr = self._tmux.send_command(
                session.session_name,
                step.command,
                wait_for_response=True,
            )
            step.output = stdout
            step.returncode = returncode

            if returncode != 0:
                step.status = TaskStepStatus.FAILED
                result.status = ExecutionStatus.FAILED
                result.stderr = stderr
                result.error = f"Step {step_index+1} failed: {stderr}"
            else:
                step.status = TaskStepStatus.COMPLETED
                result.progress = int(((step_index + 1) / len(steps)) * 100)
        else:
            step.status = TaskStepStatus.COMPLETED
            result.progress = int(((step_index + 1) / len(steps)) * 100)

        if result.status == ExecutionStatus.RUNNING:
            result.status = ExecutionStatus.COMPLETED
            result.completed_at = datetime.now(timezone.utc)

        return result

    async def pause_session(self, execution_id: str) -> bool:
        """Pause an execution session.

        Args:
            execution_id: The execution identifier

        Returns:
            True if successful, False otherwise
        """
        result = self._executions.get(execution_id)
        if not result:
            return False

        success = self._tmux.pause_session(result.session_name)
        if success:
            result.status = ExecutionStatus.PAUSED
        return success

    async def resume_session(self, execution_id: str) -> bool:
        """Resume a paused execution session.

        Args:
            execution_id: The execution identifier

        Returns:
            True if successful, False otherwise
        """
        result = self._executions.get(execution_id)
        if not result:
            return False

        success = self._tmux.resume_session(result.session_name)
        if success:
            result.status = ExecutionStatus.RUNNING
        return success

    async def terminate_session(self, execution_id: str) -> bool:
        """Terminate an execution session.

        Args:
            execution_id: The execution identifier

        Returns:
            True if successful, False otherwise
        """
        result = self._executions.get(execution_id)
        if not result:
            return False

        success = self._tmux.terminate_session(result.session_name)
        if success:
            result.status = ExecutionStatus.TERMINATED
            result.completed_at = datetime.now(timezone.utc)
            del self._executions[execution_id]
        return success

    async def get_output(self, execution_id: str) -> str:
        """Get current output from an execution session.

        Args:
            execution_id: The execution identifier

        Returns:
            The captured output as a string
        """
        result = self._executions.get(execution_id)
        if not result:
            return ""

        return self._tmux.get_output(result.session_name)

    def get_execution_status(self, execution_id: str) -> ExecutionResult | None:
        """Get execution status by ID.

        Args:
            execution_id: The execution identifier

        Returns:
            ExecutionResult or None if not found
        """
        return self._executions.get(execution_id)

    def get_steps(self, execution_id: str) -> list[TaskStep] | None:
        """Get steps for an execution.

        Args:
            execution_id: The execution identifier

        Returns:
            List of TaskStep or None if not found
        """
        return self._steps.get(execution_id)

    def list_executions(self, task_id: str | None = None) -> list[ExecutionResult]:
        """List executions, optionally filtered by task_id.

        Args:
            task_id: Optional task ID to filter by

        Returns:
            List of ExecutionResult
        """
        if task_id:
            return [
                r for r in self._executions.values()
                if r.task_id == task_id
            ]
        return list(self._executions.values())

    @staticmethod
    def parse_output_for_errors(output: str) -> list[dict]:
        """Parse output for common error patterns.

        Args:
            output: The output string to parse

        Returns:
            List of detected errors with line numbers and messages
        """
        errors = []
        lines = output.split("\n")

        error_patterns = [
            (re.compile(r"error[:\s]+(.+)", re.IGNORECASE), "error"),
            (re.compile(r"failed[:\s]+(.+)", re.IGNORECASE), "failed"),
            (re.compile(r"exception[:\s]+(.+)", re.IGNORECASE), "exception"),
            (re.compile(r",\s*line\s+(\d+)", re.IGNORECASE), "traceback"),
            (re.compile(r"SyntaxError:"), "syntax_error"),
            (re.compile(r"ImportError:"), "import_error"),
            (re.compile(r"\[(\d+)\]\s*error", re.IGNORECASE), "error"),
        ]

        for i, line in enumerate(lines):
            for pattern, error_type in error_patterns:
                match = pattern.search(line)
                if match:
                    errors.append({
                        "line": i + 1,
                        "type": error_type,
                        "message": line.strip(),
                        "match": match.group(1) if match.groups() else None,
                    })

        return errors

    @staticmethod
    def parse_progress_from_output(output: str) -> int | None:
        """Parse progress indicators from output.

        Args:
            output: The output string to parse

        Returns:
            Progress percentage (0-100) or None if not found
        """
        progress_patterns = [
            r"progress[:\s]+(\d+)%",
            r"(\d+)%\s+complete",
            r"\[(\d+)/(\d+)\]",
            r"step\s+(\d+)\s+of\s+(\d+)",
        ]

        for pattern in progress_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    return int(groups[0])
                elif len(groups) == 2:
                    current, total = int(groups[0]), int(groups[1])
                    if total > 0:
                        return int((current / total) * 100)

        return None


# Global singleton instance
claude_executor = ClaudeExecutor()
