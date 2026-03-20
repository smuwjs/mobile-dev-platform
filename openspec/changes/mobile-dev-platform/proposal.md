# Mobile Dev Platform - Proposal

## Why

移动应用开发正面临前所未有的复杂性：多平台支持（Android/iOS/鸿蒙）、需求频繁变更、团队协作效率低下、人工成本持续上升。传统开发管理模式已无法满足快速迭代的需求。

当前痛点：
- **平台碎片化**：三个主流移动平台需要独立管理，技术栈不统一
- **需求传递损耗**：产品需求到技术实现之间存在大量信息丢失和误解
- **开发效率低下**：人工协调、任务分配、进度跟踪消耗大量精力
- **成本不可控**：Claude Code 调用成本、Token 消耗、开发者时间难以量化

我们需要一个统一的管理平台，将 AI 能力（OpenSpec 拆解 + Claude Code 执行）与项目管理深度融合，实现需求到代码的自动化流转。

## What Changes

构建 **Mobile Dev Platform**（移动端开发管理平台），一个基于 AI 的移动应用开发管理平台，实现从需求输入到代码产出的全链路自动化管理。

核心变更：
1. **新建后端服务**（Python FastAPI + PostgreSQL）
   - 项目管理 API（CRUD、平台类型、多环境配置）
   - 需求拆解引擎（调用 OpenSpec 规范进行需求分解）
   - 任务执行器（调用 Claude Code CLI 执行开发任务）
   - 进度监控服务（WebSocket 实时推送、异常检测）
   - 成本计算服务（Token 统计、时间追踪、费用汇总）

2. **新建前端应用**（React + TypeScript）
   - 项目概览仪表盘
   - 需求管理与拆解可视化
   - 任务执行监控面板
   - 成本分析图表
   - 实时进度追踪

3. **集成外部工具**
   - OpenSpec CLI：需求语义拆解
   - Claude Code CLI：代码生成与修改
   - Git：代码版本控制

## Capabilities

### New Capabilities

- **project-management**: 管理 Android/iOS/鸿蒙三大平台项目，支持项目创建、配置、成员管理和环境变量管理

- **requirement-decomposition**: 调用 OpenSpec 引擎将自然语言需求拆解为结构化的需求树，支持需求版本管理和变更追踪

- **task-execution**: 将需求任务分配给 Claude Code 执行，支持任务队列、并行执行、失败重试和执行日志记录

- **progress-monitoring**: 通过 WebSocket 提供实时任务状态推送，支持异常检测（如任务超时、Claude Code 错误）和告警通知

- **cost-calculation**: 追踪每次 Claude Code 调用的 Token 消耗、响应时间、估算费用，提供多维度成本分析和报表导出

- **dashboard-display**: 聚合展示项目总览、任务进度、成本趋势、技术栈分布等关键指标，支持自定义时间范围和筛选条件

### Modified Capabilities

- 无（全新项目，无现有能力修改）

## Impact

### 后端服务（Backend）

| 模块 | 技术栈 | 说明 |
|------|--------|------|
| API Gateway | FastAPI + Uvicorn | RESTful API + WebSocket |
| Database | PostgreSQL 15+ | 项目、任务、成本数据存储 |
| ORM | SQLAlchemy 2.0 + asyncpg | 异步数据库操作 |
| Task Queue | Celery + Redis | 异步任务执行 |
| Auth | JWT + Python-JOSE | API 认证授权 |

**关键 API 端点**：
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 获取项目详情
- `POST /api/v1/projects/{id}/requirements` - 提交需求
- `POST /api/v1/requirements/{id}/decompose` - 触发需求拆解
- `POST /api/v1/tasks` - 创建任务
- `POST /api/v1/tasks/{id}/execute` - 执行任务（调用 Claude Code）
- `GET /api/v1/ws/progress` - WebSocket 进度推送
- `GET /api/v1/costs/summary` - 成本汇总

### 前端应用（Frontend）

| 模块 | 技术栈 | 说明 |
|------|--------|------|
| Framework | React 18 + TypeScript 5 | 核心框架 |
| Build Tool | Vite 5 | 快速构建 |
| State | Zustand | 轻量状态管理 |
| UI Library | TailwindCSS + shadcn/ui | 美观组件库 |
| Charts | Recharts | 数据可视化 |
| WebSocket | Native WebSocket API | 实时通信 |

**关键页面**：
- `/dashboard` - 仪表盘首页
- `/projects` - 项目列表
- `/projects/:id` - 项目详情
- `/projects/:id/requirements` - 需求管理
- `/projects/:id/tasks` - 任务执行监控
- `/projects/:id/costs` - 成本分析

### 数据模型

```
Project
├── id: UUID
├── name: string
├── platform: enum(android, ios, harmony)
├── repository_url: string?
├── environment_vars: jsonb
├── created_at: timestamp
└── updated_at: timestamp

Requirement
├── id: UUID
├── project_id: UUID (FK)
├── content: text
├── decomposed_tree: jsonb
├── status: enum(pending, decomposing, decomposed, failed)
├── parent_id: UUID? (FK self)
├── created_at: timestamp
└── updated_at: timestamp

Task
├── id: UUID
├── project_id: UUID (FK)
├── requirement_id: UUID (FK)
├── content: text
├── status: enum(queued, running, completed, failed)
├── claude_session_id: string?
├── logs: text[]
├── created_at: timestamp
├── started_at: timestamp?
└── completed_at: timestamp?

CostRecord
├── id: UUID
├── task_id: UUID (FK)
├── input_tokens: integer
├── output_tokens: integer
├── duration_ms: integer
├── estimated_cost: decimal
├── created_at: timestamp
```

### 外部集成

| 集成 | 方式 | 用途 |
|------|------|------|
| OpenSpec CLI | subprocess 调用 | 需求语义拆解 |
| Claude Code CLI | subprocess 调用 + IPC | 代码生成与修改 |
| Git | GitPython / subprocess | 代码版本控制 |

### 配置项（环境变量）

```
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mobile_dev_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# Claude Code
CLAUDE_CODE_PATH=/usr/local/bin/claude
CLAUDE_API_KEY=sk-... (如需直接 API 调用)

# OpenSpec
OPENSPEC_PATH=/usr/local/bin/openspec

# Auth
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
CORS_ORIGINS=http://localhost:3000
```

## Timeline & Milestones

| 阶段 | 周期 | 交付物 |
|------|------|--------|
| Phase 1: 基础架构 | 2 周 | 项目管理 API + 前端框架 |
| Phase 2: 需求引擎 | 2 周 | OpenSpec 集成 + 需求拆解 |
| Phase 3: 任务执行 | 3 周 | Claude Code 集成 + 任务队列 |
| Phase 4: 监控告警 | 2 周 | WebSocket 实时推送 + 异常检测 |
| Phase 5: 成本分析 | 1 周 | Token 统计 + 费用计算 |
| Phase 6: 仪表盘 | 2 周 | 数据可视化 + 报表导出 |

**预计总工期**：12 周
