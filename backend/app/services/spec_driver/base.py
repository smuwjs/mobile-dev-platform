"""规范驱动基类 - 定义规范框架接口"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ValidationStatus(str, Enum):
    """验证状态"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class SubRequirement:
    """子需求"""
    id: str
    title: str
    description: str
    priority: int = 3
    complexity: int = 1
    estimated_hours: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"


@dataclass
class TaskSpec:
    """任务规格"""
    id: str
    title: str
    description: str
    task_type: str = "development"
    priority: int = 3
    estimated_hours: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    technical_notes: str = ""


@dataclass
class DecompositionResult:
    """需求分解结果"""
    requirement_id: str
    complexity: int
    estimated_total_hours: float
    sub_requirements: list[SubRequirement]
    tasks: list[TaskSpec]
    validation_status: ValidationStatus
    conflicts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """验证结果"""
    status: ValidationStatus
    conflicts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ExecutionResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    output: str = ""
    artifacts: dict[str, Any] = field(default_factory=dict)
    token_usage: dict[str, int] = field(default_factory=dict)
    error: str = ""
    duration_seconds: float = 0.0


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    subsections: list["ReportSection"] = field(default_factory=list)


@dataclass
class ProjectReport:
    """项目完成报告"""
    project_id: str
    requirement_id: str
    generated_at: str
    summary: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_token_usage: dict[str, int]
    sections: list[ReportSection] = field(default_factory=list)


class SpecDriver(ABC):
    """规范驱动基类"""

    name: str = ""
    description: str = ""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    async def decompose_requirement(
        self,
        requirement_text: str,
        project_context: dict[str, Any]
    ) -> DecompositionResult:
        """
        AI 拆解需求为子需求和任务
        
        Args:
            requirement_text: 需求描述
            project_context: 项目上下文（技术栈、架构等）
            
        Returns:
            分解结果包含子需求和任务列表
        """
        pass

    @abstractmethod
    async def validate_tasks(
        self,
        tasks: list[dict[str, Any]],
        project_context: dict[str, Any]
    ) -> ValidationResult:
        """
        验证任务可行性和完整性
        
        Args:
            tasks: 任务列表
            project_context: 项目上下文
            
        Returns:
            验证结果
        """
        pass

    @abstractmethod
    async def generate_report(
        self,
        project_id: str,
        requirement_id: str,
        execution_data: dict[str, Any]
    ) -> ProjectReport:
        """
        生成项目完成报告
        
        Args:
            project_id: 项目ID
            requirement_id: 需求ID
            execution_data: 执行数据
            
        Returns:
            项目报告
        """
        pass

    @abstractmethod
    async def get_task_prompt(
        self,
        task: dict[str, Any],
        project_context: dict[str, Any]
    ) -> str:
        """
        获取任务执行的 prompt
        
        Args:
            task: 任务信息
            project_context: 项目上下文
            
        Returns:
            任务执行的 prompt
        """
        pass

    @classmethod
    def get_driver(cls, framework: str, config: dict[str, Any] | None = None) -> "SpecDriver":
        """获取指定框架的驱动实例"""
        drivers = {
            "openspec": OpenSpecDriver,
            "speckit": SpecKitDriver,
            "superpowers": SuperPowersDriver,
        }
        
        driver_class = drivers.get(framework.lower())
        if not driver_class:
            raise ValueError(f"Unknown framework: {framework}")
        
        return driver_class(config)


# 延迟导入避免循环依赖
from app.services.spec_driver.openspec import OpenSpecDriver
from app.services.spec_driver.speckit import SpecKitDriver
from app.services.spec_driver.superpowers import SuperPowersDriver
