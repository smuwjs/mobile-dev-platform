"""Unit tests for Claude Code executor service."""

import pytest
from datetime import datetime, timezone

from app.services.claude_executor import (
    ClaudeExecutor,
    TmuxManager,
    ExecutionStatus,
    TaskStepStatus,
    ExecutionResult,
    TaskStep,
    TmuxSession,
)


class TestExecutionResult:
    """Test cases for ExecutionResult dataclass."""

    def test_execution_result_creation(self):
        """Test creating an ExecutionResult."""
        result = ExecutionResult(
            execution_id="exec-123",
            task_id="task-456",
            session_name="claude_exec_task-456",
            status=ExecutionStatus.PENDING,
        )

        assert result.execution_id == "exec-123"
        assert result.task_id == "task-456"
        assert result.session_name == "claude_exec_task-456"
        assert result.status == ExecutionStatus.PENDING
        assert result.progress == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_execution_result_with_values(self):
        """Test ExecutionResult with various fields populated."""
        now = datetime.now(timezone.utc)
        result = ExecutionResult(
            execution_id="exec-123",
            task_id="task-456",
            session_name="claude_exec_task-456",
            status=ExecutionStatus.COMPLETED,
            returncode=0,
            stdout="Build successful",
            stderr="",
            started_at=now,
            completed_at=now,
            progress=100,
            steps_completed=3,
            steps_total=3,
        )

        assert result.returncode == 0
        assert result.stdout == "Build successful"
        assert result.progress == 100
        assert result.steps_completed == 3
        assert result.steps_total == 3


class TestTaskStep:
    """Test cases for TaskStep dataclass."""

    def test_task_step_creation(self):
        """Test creating a TaskStep."""
        step = TaskStep(
            step_id="step-1",
            title="Build Project",
            command="npm run build",
        )

        assert step.step_id == "step-1"
        assert step.title == "Build Project"
        assert step.command == "npm run build"
        assert step.status == TaskStepStatus.PENDING
        assert step.output == ""

    def test_task_step_default_values(self):
        """Test TaskStep with default values."""
        step = TaskStep(step_id="step-1", title="Test")

        assert step.command is None
        assert step.description is None
        assert step.status == TaskStepStatus.PENDING
        assert step.output == ""
        assert step.returncode is None


class TestTmuxSession:
    """Test cases for TmuxSession dataclass."""

    def test_tmux_session_creation(self):
        """Test creating a TmuxSession."""
        now = datetime.now(timezone.utc)
        session = TmuxSession(
            session_name="claude_exec_12345678",
            task_id="task-12345678",
            execution_id="exec-123",
            created_at=now,
            status=ExecutionStatus.PENDING,
        )

        assert session.session_name == "claude_exec_12345678"
        assert session.task_id == "task-12345678"
        assert session.execution_id == "exec-123"
        assert session.status == ExecutionStatus.PENDING
        assert session.working_dir is None


class TestTmuxManager:
    """Test cases for TmuxManager class."""

    def test_get_session_name(self):
        """Test session name generation."""
        manager = TmuxManager()
        task_id = "abcdefghijklmnop"
        name = manager._get_session_name(task_id)

        assert name == "claude_exec_abcdefgh"

    def test_session_name_prefix(self):
        """Test that session names have correct prefix."""
        manager = TmuxManager()
        name = manager._get_session_name("test-task-id")

        assert name.startswith("claude_exec_")


class TestClaudeExecutor:
    """Test cases for ClaudeExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create a fresh ClaudeExecutor instance for each test."""
        return ClaudeExecutor()

    def test_executor_initialization(self, executor):
        """Test that executor initializes correctly."""
        assert executor._tmux is not None
        assert isinstance(executor._executions, dict)
        assert isinstance(executor._steps, dict)

    def test_parse_output_for_errors_basic(self, executor):
        """Test parsing basic errors from output."""
        output = """
        Building project...
        error: file not found
        Failed to compile
        """
        errors = executor.parse_output_for_errors(output)

        assert len(errors) >= 2
        error_types = [e["type"] for e in errors]
        assert "error" in error_types
        assert "failed" in error_types

    def test_parse_output_for_errors_empty(self, executor):
        """Test parsing empty output."""
        output = ""
        errors = executor.parse_output_for_errors(output)

        assert len(errors) == 0

    def test_parse_output_for_errors_with_line_numbers(self, executor):
        """Test parsing errors with traceback line numbers."""
        output = """
        Traceback (most recent call last):
          File "main.py", line 10, in <module>
            main()
        """
        errors = executor.parse_output_for_errors(output)

        assert len(errors) >= 1
        traceback_errors = [e for e in errors if e["type"] == "traceback"]
        assert len(traceback_errors) >= 1

    def test_parse_progress_from_output_percent(self, executor):
        """Test parsing progress from percentage format."""
        output = "Downloading... progress: 75%"
        progress = executor.parse_progress_from_output(output)

        assert progress == 75

    def test_parse_progress_from_output_fraction(self, executor):
        """Test parsing progress from fraction format."""
        output = "Step 3 of 5 completed"
        progress = executor.parse_progress_from_output(output)

        assert progress == 60  # 3/5 = 60%

    def test_parse_progress_from_output_bracket(self, executor):
        """Test parsing progress from bracket format."""
        output = "[50/100] Processing..."
        progress = executor.parse_progress_from_output(output)

        assert progress == 50

    def test_parse_progress_from_output_no_progress(self, executor):
        """Test parsing when no progress indicator is present."""
        output = "Just some output text"
        progress = executor.parse_progress_from_output(output)

        assert progress is None

    def test_parse_output_for_errors_syntax(self, executor):
        """Test parsing Python SyntaxError."""
        output = """
        def foo(
            ^
        SyntaxError: unexpected EOF while parsing
        """
        errors = executor.parse_output_for_errors(output)

        syntax_errors = [e for e in errors if e["type"] == "syntax_error"]
        assert len(syntax_errors) >= 1

    def test_parse_output_for_errors_import(self, executor):
        """Test parsing ImportError."""
        output = """
        ImportError: No module named 'requests'
        """
        errors = executor.parse_output_for_errors(output)

        import_errors = [e for e in errors if e["type"] == "import_error"]
        assert len(import_errors) >= 1


class TestExecutionStatusEnum:
    """Test cases for ExecutionStatus enum."""

    def test_all_status_values(self):
        """Test that all expected status values exist."""
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.PAUSED.value == "paused"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.TERMINATED.value == "terminated"


class TestTaskStepStatusEnum:
    """Test cases for TaskStepStatus enum."""

    def test_all_status_values(self):
        """Test that all expected status values exist."""
        assert TaskStepStatus.PENDING.value == "pending"
        assert TaskStepStatus.RUNNING.value == "running"
        assert TaskStepStatus.COMPLETED.value == "completed"
        assert TaskStepStatus.FAILED.value == "failed"
        assert TaskStepStatus.SKIPPED.value == "skipped"
