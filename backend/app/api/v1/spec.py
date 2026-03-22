"""规范驱动 API - 处理需求分解和任务生成"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any


router = APIRouter(prefix="/spec", tags=["spec"])


class DecomposeRequest(BaseModel):
    """需求分解请求"""
    requirement_text: str = Field(..., min_length=1, description="需求描述")
    project_id: str = Field(..., description="项目ID")
    requirement_id: str | None = Field(None, description="现有需求ID")


class DecomposeResponse(BaseModel):
    """需求分解响应"""
    requirement_id: str
    complexity: int
    estimated_total_hours: float
    sub_requirements: list[dict]
    tasks: list[dict]
    validation: dict


class ExecuteRequest(BaseModel):
    """任务执行请求"""
    task_ids: list[str] = Field(..., description="任务ID列表")
    project_id: str = Field(..., description="项目ID")
    parallel: bool = Field(default=True, description="是否并行执行")


class ExecuteResponse(BaseModel):
    """任务执行响应"""
    executions: list[dict]
    total_token_usage: dict


class ReportRequest(BaseModel):
    """报告生成请求"""
    project_id: str = Field(..., description="项目ID")
    requirement_id: str = Field(..., description="需求ID")


class ReportResponse(BaseModel):
    """报告响应"""
    project_id: str
    requirement_id: str
    generated_at: str
    summary: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_token_usage: dict
    sections: list[dict]


@router.post("/decompose", response_model=DecomposeResponse)
async def decompose_requirement(request: DecomposeRequest):
    """使用规范框架分解需求"""
    
    from app.services.spec_driver import SpecDriver
    from app.services.project import project_service
    
    # 获取项目信息
    project = project_service.get_project(request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {request.project_id} not found",
        )
    
    # 获取规范驱动
    spec_framework = project.get("spec_framework", "openspec")
    spec_config = project.get("spec_config", {})
    
    driver = SpecDriver.get_driver(spec_framework, spec_config)
    
    # 构建项目上下文
    project_context = {
        "platform": project.get("platform"),
        "tech_stack": project.get("tech_stack", {}),
        "local_path": project.get("local_path"),
    }
    
    # 分解需求
    result = await driver.decompose_requirement(
        request.requirement_text,
        project_context,
    )
    
    return DecomposeResponse(
        requirement_id=result.requirement_id,
        complexity=result.complexity,
        estimated_total_hours=result.estimated_total_hours,
        sub_requirements=[
            {
                "id": sr.id,
                "title": sr.title,
                "description": sr.description,
                "priority": sr.priority,
                "complexity": sr.complexity,
                "estimated_hours": sr.estimated_hours,
                "dependencies": sr.dependencies,
            }
            for sr in result.sub_requirements
        ],
        tasks=[
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "task_type": t.task_type,
                "priority": t.priority,
                "estimated_hours": t.estimated_hours,
                "dependencies": t.dependencies,
                "acceptance_criteria": t.acceptance_criteria,
                "technical_notes": t.technical_notes,
            }
            for t in result.tasks
        ],
        validation={
            "status": result.validation_status.value,
            "conflicts": result.conflicts,
            "warnings": result.warnings,
            "suggestions": result.suggestions,
        },
    )


@router.post("/validate")
async def validate_tasks(
    project_id: str,
    tasks: list[dict[str, Any]],
):
    """验证任务列表"""
    
    from app.services.spec_driver import SpecDriver
    from app.services.project import project_service
    
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    spec_framework = project.get("spec_framework", "openspec")
    driver = SpecDriver.get_driver(spec_framework)
    
    project_context = {
        "platform": project.get("platform"),
        "tech_stack": project.get("tech_stack", {}),
        "local_path": project.get("local_path"),
    }
    
    result = await driver.validate_tasks(tasks, project_context)
    
    return {
        "status": result.status.value,
        "conflicts": result.conflicts,
        "warnings": result.warnings,
        "suggestions": result.suggestions,
    }


@router.post("/execute", response_model=ExecuteResponse)
async def execute_tasks(request: ExecuteRequest):
    """执行任务（使用 Claude Code）"""
    
    from app.services.execution import TaskExecutorManager
    from app.services.task import task_service
    from app.services.project import project_service
    
    # 获取项目信息
    project = project_service.get_project(request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {request.project_id} not found",
        )
    
    local_path = project.get("local_path")
    if not local_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project has no local_path configured",
        )
    
    # 获取执行器
    executor = TaskExecutorManager.get_executor(request.project_id, local_path)
    
    # 获取任务信息
    executions = []
    for task_id in request.task_ids:
        task = task_service.get_task(task_id)
        if not task:
            continue
        
        # 获取任务的 prompt
        from app.services.spec_driver import SpecDriver
        spec_framework = project.get("spec_framework", "openspec")
        driver = SpecDriver.get_driver(spec_framework)
        
        project_context = {
            "platform": project.get("platform"),
            "tech_stack": project.get("tech_stack", {}),
            "local_path": local_path,
        }
        
        task_prompt = await driver.get_task_prompt(task, project_context)
        
        # 执行任务
        status = await executor.execute_task(task_id, task_prompt, project_context)
        
        # 更新任务状态
        task_service.update_task(
            task_id,
            status=status.status,
            progress=status.progress,
            token_usage=status.token_usage.to_dict(),
            artifacts=status.artifacts,
            execution_log={"output": status.output, "error": status.error},
        )
        
        executions.append({
            "task_id": task_id,
            "status": status.status,
            "progress": status.progress,
            "token_usage": status.token_usage.to_dict(),
        })
    
    return ExecuteResponse(
        executions=executions,
        total_token_usage=executor.get_total_token_usage(),
    )


@router.get("/execution/{task_id}")
async def get_execution_status(task_id: str):
    """获取任务执行状态"""
    
    # 需要找到对应的执行器
    from app.services.execution import TaskExecutorManager
    
    # 遍历所有执行器查找任务
    # 这里应该从任务关联的项目找到执行器
    # 暂时返回空
    return {
        "task_id": task_id,
        "status": "unknown",
    }


@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """生成项目完成报告"""
    
    from app.services.spec_driver import SpecDriver
    from app.services.project import project_service
    from app.services.task import task_service
    
    project = project_service.get_project(request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {request.project_id} not found",
        )
    
    # 获取项目的所有任务
    tasks_data = task_service.get_tasks_by_requirement(request.requirement_id)
    
    execution_data = {
        "tasks": [
            {
                "id": t["id"],
                "title": t["title"],
                "status": t.get("status"),
                "token_usage": t.get("token_usage"),
                "artifacts": t.get("artifacts"),
            }
            for t in tasks_data
        ]
    }
    
    spec_framework = project.get("spec_framework", "openspec")
    driver = SpecDriver.get_driver(spec_framework)
    
    report = await driver.generate_report(
        request.project_id,
        request.requirement_id,
        execution_data,
    )
    
    return ReportResponse(
        project_id=report.project_id,
        requirement_id=report.requirement_id,
        generated_at=report.generated_at,
        summary=report.summary,
        total_tasks=report.total_tasks,
        completed_tasks=report.completed_tasks,
        failed_tasks=report.failed_tasks,
        total_token_usage=report.total_token_usage,
        sections=[
            {
                "title": s.title,
                "content": s.content,
            }
            for s in report.sections
        ],
    )


@router.get("/frameworks")
async def get_frameworks():
    """获取支持的规范框架列表"""
    return {
        "frameworks": [
            {
                "id": "openspec",
                "name": "OpenSpec",
                "description": "基于 OpenSpec 规范框架进行需求分解和任务生成",
                "url": "https://github.com/Fission-AI/OpenSpec",
            },
            {
                "id": "speckit",
                "name": "SpecKit",
                "description": "基于 GitHub's Pull Request 规范",
                "url": "https://github.com/github/spec-kit",
            },
            {
                "id": "superpowers",
                "name": "SuperPowers",
                "description": "基于 WordPress SuperPowers 规范",
                "url": "https://github.com/obra/superpowers",
            },
        ]
    }
}
