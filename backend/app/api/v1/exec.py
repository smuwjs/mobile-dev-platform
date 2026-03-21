"""Execution API endpoints for Claude Code task execution.

Provides endpoints for:
- Starting task execution
- Pausing/resuming/terminating execution
- Getting execution output and status
"""

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.claude_executor import (
    ExecutionStatus,
    TaskStepStatus,
    claude_executor,
)

router = APIRouter(prefix="/exec", tags=["execution"])


# Pydantic Schemas

class TaskStepInput(BaseModel):
    """Input schema for a task step."""

    title: str = Field(..., description="Step title")
    command: str | None = Field(None, description="Command to execute")
    description: str | None = Field(None, description="Step description")


class StartExecutionRequest(BaseModel):
    """Request schema for starting an execution."""

    task_id: str = Field(..., description="Task identifier")
    execution_id: str = Field(..., description="Execution identifier")
    working_dir: str | None = Field(None, description="Working directory")
    steps: list[TaskStepInput] = Field(default_factory=list, description="Task steps to execute")


class StartExecutionResponse(BaseModel):
    """Response schema for start execution."""

    execution_id: str
    session_name: str
    status: str
    message: str


class PauseExecutionRequest(BaseModel):
    """Request schema for pausing an execution."""

    execution_id: str = Field(..., description="Execution identifier")


class ResumeExecutionRequest(BaseModel):
    """Request schema for resuming an execution."""

    execution_id: str = Field(..., description="Execution identifier")


class TerminateExecutionRequest(BaseModel):
    """Request schema for terminating an execution."""

    execution_id: str = Field(..., description="Execution identifier")


class ExecutionStatusResponse(BaseModel):
    """Response schema for execution status."""

    execution_id: str
    task_id: str
    session_name: str
    status: str
    progress: int
    steps_completed: int
    steps_total: int
    stdout: str
    stderr: str
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    metadata: dict


class ExecutionOutputResponse(BaseModel):
    """Response schema for execution output."""

    execution_id: str
    output: str
    parsed_progress: int | None
    errors: list[dict]


class StepStatusResponse(BaseModel):
    """Response schema for individual step status."""

    step_id: str
    title: str
    status: str
    output: str
    returncode: int | None
    started_at: datetime | None
    completed_at: datetime | None


class ExecutionStepsResponse(BaseModel):
    """Response schema for all steps of an execution."""

    execution_id: str
    steps: list[StepStatusResponse]


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True


# API Endpoints

@router.post("/start", response_model=StartExecutionResponse, status_code=status.HTTP_201_CREATED)
async def start_execution(request: StartExecutionRequest):
    """Start a new task execution.

    Creates a tmux session and begins executing the task steps.
    """
    try:
        session_name = await claude_executor.create_session(
            task_id=request.task_id,
            execution_id=request.execution_id,
            working_dir=request.working_dir,
        )

        # If steps are provided, start execution immediately
        if request.steps:
            steps_data = [step.model_dump() for step in request.steps]
            asyncio.create_task(
                claude_executor.execute_task(request.execution_id, steps_data)
            )

        return StartExecutionResponse(
            execution_id=request.execution_id,
            session_name=session_name,
            status=ExecutionStatus.PENDING.value,
            message="Execution started successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start execution: {str(e)}",
        )


@router.post("/pause", response_model=MessageResponse)
async def pause_execution(request: PauseExecutionRequest):
    """Pause a running execution.

    Sends SIGSTOP to the tmux session process.
    """
    success = await claude_executor.pause_session(request.execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {request.execution_id} not found or cannot be paused",
        )

    return MessageResponse(message="Execution paused successfully")


@router.post("/resume", response_model=MessageResponse)
async def resume_execution(request: ResumeExecutionRequest):
    """Resume a paused execution.

    Sends SIGCONT to the tmux session process.
    """
    success = await claude_executor.resume_session(request.execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {request.execution_id} not found or cannot be resumed",
        )

    return MessageResponse(message="Execution resumed successfully")


@router.post("/terminate", response_model=MessageResponse)
async def terminate_execution(request: TerminateExecutionRequest):
    """Terminate an execution session.

    Kills the tmux session and cleans up resources.
    """
    success = await claude_executor.terminate_session(request.execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {request.execution_id} not found",
        )

    return MessageResponse(message="Execution terminated successfully")


@router.get("/status/{execution_id}", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: str):
    """Get the current status of an execution."""
    result = claude_executor.get_execution_status(execution_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )

    return ExecutionStatusResponse(
        execution_id=result.execution_id,
        task_id=result.task_id,
        session_name=result.session_name,
        status=result.status.value,
        progress=result.progress,
        steps_completed=result.steps_completed,
        steps_total=result.steps_total,
        stdout=result.stdout,
        stderr=result.stderr,
        error=result.error,
        started_at=result.started_at,
        completed_at=result.completed_at,
        metadata=result.metadata,
    )


@router.get("/output/{execution_id}", response_model=ExecutionOutputResponse)
async def get_execution_output(execution_id: str):
    """Get the current output from an execution.

    Captures tmux pane output and parses for progress and errors.
    """
    output = await claude_executor.get_output(execution_id)
    if output is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )

    parsed_progress = claude_executor.parse_progress_from_output(output)
    errors = claude_executor.parse_output_for_errors(output)

    return ExecutionOutputResponse(
        execution_id=execution_id,
        output=output,
        parsed_progress=parsed_progress,
        errors=errors,
    )


@router.get("/steps/{execution_id}", response_model=ExecutionStepsResponse)
async def get_execution_steps(execution_id: str):
    """Get all steps for an execution."""
    steps = claude_executor.get_steps(execution_id)
    if steps is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found",
        )

    return ExecutionStepsResponse(
        execution_id=execution_id,
        steps=[
            StepStatusResponse(
                step_id=step.step_id,
                title=step.title,
                status=step.status.value,
                output=step.output,
                returncode=step.returncode,
                started_at=step.started_at,
                completed_at=step.completed_at,
            )
            for step in steps
        ],
    )


@router.get("/list", response_model=list[ExecutionStatusResponse])
async def list_executions(task_id: str | None = None):
    """List all executions, optionally filtered by task_id."""
    executions = claude_executor.list_executions(task_id)

    return [
        ExecutionStatusResponse(
            execution_id=r.execution_id,
            task_id=r.task_id,
            session_name=r.session_name,
            status=r.status.value,
            progress=r.progress,
            steps_completed=r.steps_completed,
            steps_total=r.steps_total,
            stdout=r.stdout,
            stderr=r.stderr,
            error=r.error,
            started_at=r.started_at,
            completed_at=r.completed_at,
            metadata=r.metadata,
        )
        for r in executions
    ]
