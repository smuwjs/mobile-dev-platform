# Phase 3 设计文档

## 架构设计

### 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web 前端 (React)                          │
│  需求输入 → 拆解展示 → 执行控制 → 成本统计                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP / WebSocket
┌───────────────────────────────▼─────────────────────────────────┐
│                      FastAPI 后端                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ OpenSpec    │ │ Claude      │ │ Cost        │              │
│  │ Service     │ │ Executor    │ │ Calculator  │              │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘              │
│          │               │               │                      │
│  ┌──────▼───────────────▼───────────────▼──────┐              │
│  │              业务服务层                      │              │
│  └─────────────────────┬───────────────────────┘              │
│                        │                                         │
│  ┌────────────────────▼───────────────────────┐              │
│  │              数据访问层 (SQLAlchemy)        │              │
│  └─────────────────────┬───────────────────────┘              │
└────────────────────────┼────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    PostgreSQL 数据库                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code (外部)                           │
│  tmux 会话管理 → 代码生成 → 编译验证                           │
└─────────────────────────────────────────────────────────────────┘
```

## 核心模块设计

### 1. OpenSpec 服务

**职责**：调用 OpenSpec CLI 生成需求文档

**接口**：
```python
class OpenSpecService:
    async def generate_proposal(project_id: str, requirement: RequirementInput) -> Proposal
    async def generate_design(project_id: str, proposal: Proposal) -> Design
    async def generate_specs(design: Design) -> List[Spec]
    async def generate_tasks(specs: List[Spec]) -> List[Task]
```

### 2. Claude Code 执行器

**职责**：管理 tmux 会话，执行开发任务

**接口**：
```python
class ClaudeExecutor:
    async def create_session(task_id: str) -> str  # tmux session name
    async def execute_task(session: str, task: Task) -> ExecutionResult
    async def pause_session(session: str) -> bool
    async def resume_session(session: str) -> bool
    async def terminate_session(session: str) -> bool
    async def get_output(session: str) -> str
```

### 3. 异常检测服务

**职责**：监控执行状态，检测异常

**检测规则**：
- 无输出超时：5分钟无日志输出
- 编译失败：检测 error、failed、exception 关键字
- API 限流：检测 429 状态码

### 4. 成本计算器

**职责**：计算时间、Token、成本预估

**算法**：
```
预估时间 = 历史平均时间 × 复杂度系数
预估 Token = 代码行数预估 × 复杂度系数 / 100
预估成本 = 预估 Token × 单价
```

## 数据模型

### Projects 表扩展

```python
class Project(Base):
    id: UUID
    name: str
    platform: Enum  # android/ios/harmony
    repo_url: str | None
    tech_stack: JSON  # ["Kotlin", "Jetpack Compose"]
    architecture: str | None
    docs: JSON
    status: Enum  # active/archived
    created_at: DateTime
    updated_at: DateTime
```

### Tasks 表扩展

```python
class Task(Base):
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    task_type: Enum  # feature/refactor/ui_optimize
    status: Enum  # pending/running/paused/completed/failed/terminated
    progress: int
    
    # OpenSpec 输出
    proposal: JSON | None
    design: JSON | None
    specs: JSON | None
    task_list: JSON | None
    
    # 预估
    estimate_minutes: int | None
    estimate_tokens: int | None
    
    # 实际
    actual_minutes: int | None
    actual_tokens: int | None
    
    created_at: DateTime
    started_at: DateTime | None
    completed_at: DateTime | None
```

### TaskLogs 表

```python
class TaskLog(Base):
    id: UUID
    task_id: UUID
    timestamp: DateTime
    level: Enum  # info/warn/error
    message: str
```

### Metrics 表

```python
class Metric(Base):
    id: UUID
    project_id: UUID
    task_type: Enum
    specs_count: int
    tasks_count: int
    code_lines: int
    minutes: int
    tokens: int
    completed_at: DateTime
```

## API 端点设计

### OpenSpec API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/openspec/proposal | 生成需求提案 |
| POST | /api/v1/openspec/design | 生成技术设计 |
| POST | /api/v1/openspec/specs | 生成功规规范 |
| POST | /api/v1/openspec/tasks | 生成任务清单 |
| POST | /api/v1/openspec/full | 完整流程 |

### 执行 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/exec/start | 开始执行 |
| POST | /api/v1/exec/pause | 暂停执行 |
| POST | /api/v1/exec/resume | 恢复执行 |
| POST | /api/v1/exec/terminate | 终止执行 |
| GET | /api/v1/exec/output | 获取输出 |
| GET | /api/v1/exec/status | 获取状态 |

### 成本 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/costs/estimate | 获取预估 |
| GET | /api/v1/costs/history | 历史记录 |
| POST | /api/v1/costs/record | 记录实际消耗 |

## WebSocket 事件

| 事件 | 说明 |
|------|------|
| task:started | 任务开始 |
| task:progress | 进度更新 |
| task:output | 日志输出 |
| task:completed | 任务完成 |
| task:failed | 任务失败 |
| task:alert | 告警通知 |
