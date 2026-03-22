"""规范驱动服务"""

from app.services.spec_driver.base import (
    SpecDriver,
    DecompositionResult,
    ValidationResult,
    ProjectReport,
    TaskStatus,
    ValidationStatus,
    SubRequirement,
    TaskSpec,
    ExecutionResult,
    ReportSection,
)

from app.services.spec_driver.openspec import OpenSpecDriver
from app.services.spec_driver.speckit import SpecKitDriver
from app.services.spec_driver.superpowers import SuperPowersDriver

__all__ = [
    "SpecDriver",
    "DecompositionResult",
    "ValidationResult",
    "ProjectReport",
    "TaskStatus",
    "ValidationStatus",
    "SubRequirement",
    "TaskSpec",
    "ExecutionResult",
    "ReportSection",
    "OpenSpecDriver",
    "SpecKitDriver",
    "SuperPowersDriver",
]
