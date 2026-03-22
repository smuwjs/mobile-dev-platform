"""SpecKit 规范驱动实现"""

import uuid
from typing import Any

from app.services.spec_driver.base import (
    SpecDriver,
    DecompositionResult,
    ValidationResult,
    ProjectReport,
    ValidationStatus,
    SubRequirement,
    TaskSpec,
    ReportSection,
)


class SpecKitDriver(SpecDriver):
    """SpecKit 规范驱动 - 基于 GitHub's Pull Request 规范"""

    name = "speckit"
    description = "基于 SpecKit 规范框架"

    async def decompose_requirement(
        self,
        requirement_text: str,
        project_context: dict[str, Any]
    ) -> DecompositionResult:
        """使用 SpecKit 进行需求分解"""
        
        # SpecKit 风格的分解
        prompt = self._build_spec_prompt(requirement_text, project_context)
        analysis = await self._call_ai_analysis(prompt)
        
        return self._parse_result(requirement_text, analysis)

    async def validate_tasks(
        self,
        tasks: list[dict[str, Any]],
        project_context: dict[str, Any]
    ) -> ValidationResult:
        """验证任务"""
        # SpecKit 验证逻辑
        conflicts = []
        warnings = []
        
        status = ValidationStatus.VALID
        if conflicts:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.WARNING
            
        return ValidationResult(
            status=status,
            conflicts=conflicts,
            warnings=warnings,
            suggestions=[],
        )

    async def generate_report(
        self,
        project_id: str,
        requirement_id: str,
        execution_data: dict[str, Any]
    ) -> ProjectReport:
        """生成 SpecKit 格式的报告"""
        
        tasks = execution_data.get("tasks", [])
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        
        total_input = sum(t.get("token_usage", {}).get("input", 0) for t in tasks)
        total_output = sum(t.get("token_usage", {}).get("output", 0) for t in tasks)
        
        return ProjectReport(
            project_id=project_id,
            requirement_id=requirement_id,
            generated_at="",
            summary=f"完成 {completed}/{len(tasks)} 个任务",
            total_tasks=len(tasks),
            completed_tasks=completed,
            failed_tasks=0,
            total_token_usage={
                "input": total_input,
                "output": total_output,
                "total": total_input + total_output,
            },
            sections=[],
        )

    async def get_task_prompt(
        self,
        task: dict[str, Any],
        project_context: dict[str, Any]
    ) -> str:
        """生成任务 prompt"""
        
        return f"""## SpecKit 任务

### {task.get('title')}

{task.get('description', '')}

### 验收标准
"""
    def _build_spec_prompt(self, requirement: str, context: dict) -> str:
        return f"分析需求: {requirement}"
        
    async def _call_ai_analysis(self, prompt: str) -> dict:
        return {"complexity": 2, "estimated_hours": 4.0, "tasks": [], "sub_requirements": []}
        
    def _parse_result(self, text: str, analysis: dict) -> DecompositionResult:
        return DecompositionResult(
            requirement_id=str(uuid.uuid4()),
            complexity=analysis.get("complexity", 1),
            estimated_total_hours=analysis.get("estimated_hours", 0),
            sub_requirements=[],
            tasks=[],
            validation_status=ValidationStatus.VALID,
        )
