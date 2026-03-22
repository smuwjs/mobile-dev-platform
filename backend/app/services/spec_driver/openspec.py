"""OpenSpec 规范驱动实现"""

import uuid
from datetime import datetime
from typing import Any

from app.services.spec_driver.base import (
    SpecDriver,
    DecompositionResult,
    ValidationResult,
    ProjectReport,
    TaskStatus,
    ValidationStatus,
    SubRequirement,
    TaskSpec,
    ReportSection,
)


class OpenSpecDriver(SpecDriver):
    """OpenSpec 规范驱动"""

    name = "openspec"
    description = "基于 OpenSpec 规范框架进行需求分解和任务生成"

    async def decompose_requirement(
        self,
        requirement_text: str,
        project_context: dict[str, Any]
    ) -> DecompositionResult:
        """使用 OpenSpec 进行需求分解"""
        
        tech_stack = project_context.get("tech_stack", {})
        platform = project_context.get("platform", "")
        
        # 构建 OpenSpec 风格的 prompt
        prompt = self._build_decompose_prompt(requirement_text, project_context)
        
        # 调用 AI 分析（这里应该调用实际的 AI 服务）
        analysis = await self._call_ai_analysis(prompt)
        
        # 解析 AI 返回的结果
        return self._parse_decomposition_result(
            requirement_text,
            analysis,
            project_context
        )

    async def validate_tasks(
        self,
        tasks: list[dict[str, Any]],
        project_context: dict[str, Any]
    ) -> ValidationResult:
        """验证任务可行性"""
        
        conflicts = []
        warnings = []
        suggestions = []
        
        # 检查循环依赖
        task_ids = {t["id"] for t in tasks}
        for task in tasks:
            deps = task.get("dependencies", [])
            for dep in deps:
                if dep not in task_ids:
                    conflicts.append(f"Task {task['id']} depends on unknown task {dep}")
        
        # 检查任务粒度
        for task in tasks:
            if not task.get("description"):
                warnings.append(f"Task {task['id']} lacks description")
            if not task.get("estimated_hours") or task.get("estimated_hours", 0) > 8:
                suggestions.append(
                    f"Task {task['id']} may be too large, consider splitting"
                )
        
        status = ValidationStatus.INVALID if conflicts else (
            ValidationStatus.WARNING if warnings else ValidationStatus.VALID
        )
        
        return ValidationResult(
            status=status,
            conflicts=conflicts,
            warnings=warnings,
            suggestions=suggestions,
        )

    async def generate_report(
        self,
        project_id: str,
        requirement_id: str,
        execution_data: dict[str, Any]
    ) -> ProjectReport:
        """生成 OpenSpec 格式的报告"""
        
        tasks = execution_data.get("tasks", [])
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        failed = sum(1 for t in tasks if t.get("status") == "failed")
        
        # 汇总 token 消耗
        total_token_usage = {"input": 0, "output": 0, "total": 0}
        for task in tasks:
            token_usage = task.get("token_usage", {})
            total_token_usage["input"] += token_usage.get("input", 0)
            total_token_usage["output"] += token_usage.get("output", 0)
        total_token_usage["total"] = (
            total_token_usage["input"] + total_token_usage["output"]
        )
        
        # 生成报告章节
        sections = [
            ReportSection(
                title="执行摘要",
                content=self._generate_execution_summary(execution_data),
            ),
            ReportSection(
                title="任务完成情况",
                content=self._generate_task_completion_section(tasks),
            ),
            ReportSection(
                title="Token 消耗统计",
                content=self._generate_token_section(total_token_usage),
            ),
            ReportSection(
                title="产物清单",
                content=self._generate_artifacts_section(tasks),
            ),
        ]
        
        return ProjectReport(
            project_id=project_id,
            requirement_id=requirement_id,
            generated_at=datetime.now().isoformat(),
            summary=self._generate_summary(len(tasks), completed, failed, total_token_usage),
            total_tasks=len(tasks),
            completed_tasks=completed,
            failed_tasks=failed,
            total_token_usage=total_token_usage,
            sections=sections,
        )

    async def get_task_prompt(
        self,
        task: dict[str, Any],
        project_context: dict[str, Any]
    ) -> str:
        """生成任务执行的 prompt"""
        
        local_path = project_context.get("local_path", "")
        tech_stack = project_context.get("tech_stack", {})
        
        prompt = f"""## 任务执行

### 任务描述
{task.get('description', '')}

### 任务类型
{task.get('task_type', 'development')}

### 验收标准
"""
        for i, criteria in enumerate(task.get("acceptance_criteria", []), 1):
            prompt += f"{i}. {criteria}\n"
        
        if task.get("technical_notes"):
            prompt += f"\n### 技术说明\n{task['technical_notes']}\n"
        
        prompt += f"""

### 项目路径
{local_path}

### 技术栈
"""
        for key, value in tech_stack.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += """

请按照以上要求完成开发任务，完成后报告执行结果和产物。
"""
        
        return prompt

    def _build_decompose_prompt(
        self,
        requirement_text: str,
        project_context: dict[str, Any]
    ) -> str:
        """构建需求分解的 prompt"""
        
        platform = project_context.get("platform", "")
        tech_stack = project_context.get("tech_stack", {})
        
        prompt = f"""请根据以下需求进行 AI 辅助分解。

## 需求描述
{requirement_text}

## 项目信息
- 平台: {platform}
- 技术栈: {tech_stack}

## 分解要求

请将需求分解为:
1. **子需求** - 独立的功能模块
2. **开发任务** - 具体可执行的任务项

对于每个任务，请提供:
- 任务标题和描述
- 任务类型（development/testing/documentation）
- 优先级 (1=高, 2=中, 3=低)
- 预估工时
- 依赖关系
- 验收标准
- 技术说明

请以 JSON 格式返回结果。
"""
        return prompt

    async def _call_ai_analysis(self, prompt: str) -> dict[str, Any]:
        """调用 AI 进行分析"""
        # TODO: 实现实际的 AI 调用
        # 这里返回模拟数据
        return {
            "complexity": 3,
            "estimated_hours": 8.0,
            "sub_requirements": [],
            "tasks": [],
        }

    def _parse_decomposition_result(
        self,
        requirement_text: str,
        analysis: dict[str, Any],
        project_context: dict[str, Any]
    ) -> DecompositionResult:
        """解析 AI 返回的分解结果"""
        
        req_id = str(uuid.uuid4())
        
        sub_requirements = [
            SubRequirement(
                id=str(uuid.uuid4()),
                title=sr["title"],
                description=sr.get("description", ""),
                priority=sr.get("priority", 3),
                complexity=sr.get("complexity", 1),
                estimated_hours=sr.get("estimated_hours", 0.0),
                dependencies=sr.get("dependencies", []),
            )
            for sr in analysis.get("sub_requirements", [])
        ]
        
        tasks = [
            TaskSpec(
                id=str(uuid.uuid4()),
                title=t["title"],
                description=t.get("description", ""),
                task_type=t.get("task_type", "development"),
                priority=t.get("priority", 3),
                estimated_hours=t.get("estimated_hours", 0.0),
                dependencies=t.get("dependencies", []),
                acceptance_criteria=t.get("acceptance_criteria", []),
                technical_notes=t.get("technical_notes", ""),
            )
            for t in analysis.get("tasks", [])
        ]
        
        return DecompositionResult(
            requirement_id=req_id,
            complexity=analysis.get("complexity", 1),
            estimated_total_hours=analysis.get("estimated_hours", 0.0),
            sub_requirements=sub_requirements,
            tasks=tasks,
            validation_status=ValidationStatus.VALID,
        )

    def _generate_execution_summary(self, execution_data: dict) -> str:
        """生成执行摘要"""
        return "执行摘要内容..."

    def _generate_task_completion_section(self, tasks: list) -> str:
        """生成任务完成情况"""
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        return f"完成 {completed}/{len(tasks)} 个任务"

    def _generate_token_section(self, token_usage: dict) -> str:
        """生成 Token 消耗统计"""
        return f"""输入 Token: {token_usage.get('input', 0):,}
输出 Token: {token_usage.get('output', 0):,}
总计: {token_usage.get('total', 0):,}"""

    def _generate_artifacts_section(self, tasks: list) -> str:
        """生成产物清单"""
        artifacts = []
        for task in tasks:
            if task.get("artifacts"):
                artifacts.extend(task.get("artifacts", []))
        
        if not artifacts:
            return "无产物"
        
        return "\n".join(f"- {a}" for a in artifacts)

    def _generate_summary(
        self,
        total: int,
        completed: int,
        failed: int,
        token_usage: dict
    ) -> str:
        """生成总结"""
        return f"""项目完成情况:
- 总任务数: {total}
- 已完成: {completed}
- 失败: {failed}
- Token 消耗: {token_usage.get('total', 0):,}"""
