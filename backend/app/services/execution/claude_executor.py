"""Claude Code 执行器 - 负责调用 Claude Code 执行开发任务"""

import asyncio
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp


@dataclass
class TokenUsage:
    """Token 使用统计"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    def to_dict(self) -> dict[str, int]:
        return {
            "input": self.input_tokens,
            "output": self.output_tokens,
            "total": self.total_tokens,
        }


@dataclass
class ExecutionStatus:
    """执行状态"""
    task_id: str
    status: str = "pending"  # pending, running, completed, failed
    progress: int = 0
    current_step: str = ""
    output: str = ""
    error: str = ""
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    artifacts: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ClaudeExecutor:
    """Claude Code 执行器"""
    
    def __init__(
        self,
        project_local_path: str,
        claude_bin: str = "~/.npm-global/bin/claude",
        model: str = "minimax/MiniMax-M2.5"
    ):
        self.project_path = Path(project_local_path).expanduser().resolve()
        self.claude_bin = os.path.expanduser(claude_bin)
        self.model = model
        
        # 执行状态存储
        self._executions: dict[str, ExecutionStatus] = {}
        
    async def execute_task(
        self,
        task_id: str,
        task_prompt: str,
        context: dict[str, Any] | None = None
    ) -> ExecutionStatus:
        """执行单个任务"""
        
        status = ExecutionStatus(
            task_id=task_id,
            status="running",
            started_at=datetime.now(),
        )
        self._executions[task_id] = status
        
        try:
            # 构建完整的 prompt
            full_prompt = self._build_prompt(task_prompt, context or {})
            
            # 执行 Claude Code
            result = await self._run_claude(full_prompt)
            
            status.status = "completed"
            status.progress = 100
            status.output = result.get("output", "")
            status.token_usage = TokenUsage(
                input_tokens=result.get("input_tokens", 0),
                output_tokens=result.get("output_tokens", 0),
                total_tokens=result.get("total_tokens", 0),
            )
            status.artifacts = result.get("artifacts", {})
            
        except Exception as e:
            status.status = "failed"
            status.error = str(e)
            
        status.completed_at = datetime.now()
        return status
    
    async def execute_task_streaming(
        self,
        task_id: str,
        task_prompt: str,
        context: dict[str, Any] | None = None,
        on_progress: callable | None = None
    ) -> ExecutionStatus:
        """流式执行任务，实时更新进度"""
        
        status = ExecutionStatus(
            task_id=task_id,
            status="running",
            started_at=datetime.now(),
        )
        self._executions[task_id] = status
        
        try:
            full_prompt = self._build_prompt(task_prompt, context or {})
            
            # 使用流式执行
            async for update in self._run_claude_streaming(full_prompt):
                status.progress = update.get("progress", status.progress)
                status.current_step = update.get("step", "")
                status.output = update.get("output", "")
                
                tokens = update.get("token_usage", {})
                status.token_usage = TokenUsage(
                    input_tokens=tokens.get("input", 0),
                    output_tokens=tokens.get("output", 0),
                )
                
                if on_progress:
                    await on_progress(status)
            
            status.status = "completed"
            
        except Exception as e:
            status.status = "failed"
            status.error = str(e)
            
        status.completed_at = datetime.now()
        return status
    
    def get_execution_status(self, task_id: str) -> ExecutionStatus | None:
        """获取任务执行状态"""
        return self._executions.get(task_id)
    
    def get_all_executions(self) -> dict[str, ExecutionStatus]:
        """获取所有执行状态"""
        return self._executions.copy()
    
    def get_total_token_usage(self) -> dict[str, int]:
        """获取总 token 消耗"""
        total = TokenUsage()
        for status in self._executions.values():
            total.input_tokens += status.token_usage.input_tokens
            total.output_tokens += status.token_usage.output_tokens
        total.total_tokens = total.input_tokens + total.output_tokens
        return total.to_dict()
    
    def _build_prompt(self, task_prompt: str, context: dict) -> str:
        """构建完整的 prompt"""
        
        project_info = f"""## 项目路径
{self.project_path}

## 项目信息
"""
        for key, value in context.items():
            project_info += f"- {key}: {value}\n"
        
        return f"""{project_info}

{task_prompt}

## 输出要求
完成后请:
1. 列出所有创建/修改的文件
2. 总结执行结果
3. 报告 token 消耗情况
"""
    
    async def _run_claude(self, prompt: str) -> dict[str, Any]:
        """运行 Claude Code（同步方式）"""
        
        # 实际应该调用 Claude Code CLI
        # 这里返回模拟结果
        
        # 检查项目路径是否存在
        if not self.project_path.exists():
            self.project_path.mkdir(parents=True, exist_ok=True)
        
        # 模拟执行
        await asyncio.sleep(1)
        
        return {
            "output": "任务执行完成",
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
            "artifacts": {
                "files_created": [],
                "files_modified": [],
            }
        }
    
    async def _run_claude_streaming(self, prompt: str):
        """流式运行 Claude Code"""
        
        if not self.project_path.exists():
            self.project_path.mkdir(parents=True, exist_ok=True)
        
        # 模拟流式输出
        steps = [
            {"progress": 20, "step": "分析任务要求", "output": "正在分析...", "token_usage": {"input": 500}},
            {"progress": 40, "step": "编写代码", "output": "正在编写代码...", "token_usage": {"input": 300}},
            {"progress": 60, "step": "运行测试", "output": "正在测试...", "token_usage": {"input": 200}},
            {"progress": 80, "step": "整理产物", "output": "整理中...", "token_usage": {"input": 100}},
            {"progress": 100, "step": "完成", "output": "执行完成", "token_usage": {"input": 50}},
        ]
        
        for step in steps:
            await asyncio.sleep(0.5)
            yield step


class TaskExecutorManager:
    """任务执行管理器 - 管理多个项目的执行器"""
    
    _executors: dict[str, ClaudeExecutor] = {}
    
    @classmethod
    def get_executor(cls, project_id: str, local_path: str) -> ClaudeExecutor:
        """获取项目的执行器"""
        if project_id not in cls._executors:
            cls._executors[project_id] = ClaudeExecutor(local_path)
        return cls._executors[project_id]
    
    @classmethod
    def get_all_token_usage(cls) -> dict[str, int]:
        """获取所有项目的总 token 消耗"""
        total = {"input": 0, "output": 0, "total": 0}
        for executor in cls._executors.values():
            usage = executor.get_total_token_usage()
            total["input"] += usage.get("input", 0)
            total["output"] += usage.get("output", 0)
        total["total"] = total["input"] + total["output"]
        return total
    
    @classmethod
    def clear_executor(cls, project_id: str):
        """清除项目的执行器"""
        if project_id in cls._executors:
            del cls._executors[project_id]
