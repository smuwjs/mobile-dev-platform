"""SuperPowers 规范驱动实现"""

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


class SuperPowersDriver(SpecDriver):
    """SuperPowers 规范驱动 - 基于 WordPress SuperPowers 规范"""

    name = "superpowers"
    description = "基于 SuperPowers 规范框架"

    async def decompose_requirement(
        self,
        requirement_text: str,
        project_context: dict[str, Any]
    ) -> DecompositionResult:
        """使用 SuperPowers 进行需求分解"""
        
        prompt = self._build_superpowers_prompt(requirement_text, project_context)
        analysis = await self._call_ai_analysis(prompt)
        
        return self._parse_result(requirement_text, analysis)

    async def validate_tasks(
        self,
        tasks: list[dict[str, Any]],
        project_context: dict[str, Any]
    ) -> ValidationResult:
        """验证任务"""
        
        conflicts = []
        warnings = []
        
        # SuperPowers 特定验证
        for task in tasks:
            if task.get("task_type") == "development":
                if not task.get("acceptance_criteria"):
                    warnings.append(f"Task {task['id']} 缺少验收标准")
        
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
        """生成 SuperPowers 格式的报告"""
        
        tasks = execution_data.get("tasks", [])
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        
        total_input = sum(t.get("token_usage", {}).get("input", 0) for t in tasks)
        total_output = sum(t.get("token_usage", {}).get("output", 0) for t in tasks)
        
        return ProjectReport(
            project_id=project_id,
            requirement_id=requirement_id,
            generated_at="",
            summary=f"SuperPowers 模式完成 {completed}/{len(tasks)} 任务",
            total_tasks=len(tasks),
            completed_tasks=completed,
            failed_tasks=0,
            total_token_usage={
                "input": total_input,
                "output": total_output,
                "total": total_input + total_output,
            },
            sections=[
                ReportSection(
                    title="SuperPowers 执行报告",
                    content=self._generate_superpowers_section(tasks),
                )
            ],
        )

    async def get_task_prompt(
        self,
        task: dict[str, Any],
        project_context: dict[str, Any]
    ) -> str:
        """生成 SuperPowers 任务 prompt"""
        
        return f"""## SuperPowers 任务: {task.get('title')}

{task.get('description', '')}

### Power 验收标准
"""
        
    def _build_superpowers_prompt(self, requirement: str, context: dict) -> str:
        return f"SuperPowers 分析: {requirement}"
        
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
        
    def _generate_superpowers_section(self, tasks: list) -> str:
        lines = []
        for task in tasks:
            status = task.get("status", "pending")
            title = task.get("title", "Unknown")
            lines.append(f"- [{'x' if status == 'completed' else ' '}] {title}")
        return "\n".join(lines)
