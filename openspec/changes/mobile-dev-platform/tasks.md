# Phase 1: 基础架构 - 实现任务清单

**阶段周期**: 2 周
**交付物**: 项目管理 API + 前端框架

---

## 后端任务 (Backend Tasks)

### 1. 项目初始化与配置

| 属性 | 值 |
|------|-----|
| **任务名称** | `backend-setup` |
| **描述** | 初始化 Python FastAPI 项目，创建 pyproject.toml，安装依赖（FastAPI, SQLAlchemy 2.0, asyncpg, Celery, Redis, python-jose, pydantic, uvicorn），配置 uv.lock |
| **预估时间** | 2 小时 |
| **预估 Token** | 500 |

---

### 2. 数据库配置与 Session 管理

| 属性 | 值 |
|------|-----|
| **任务名称** | `db-session-setup` |
| **描述** | 配置 PostgreSQL 数据库连接，创建 `app/db/session.py` 管理异步 Session，实现数据库连接池配置 |
| **预估时间** | 1 小时 |
| **预估 Token** | 300 |

---

### 3. SQLAlchemy 模型定义

| 属性 | 值 |
|------|-----|
| **任务名称** | `db-models` |
| **描述** | 创建所有数据库模型：`Base`, `User`, `Project`, `Requirement`, `Task`, `CostRecord`, `ProjectMembership`。定义所有字段、主键、外键、索引、CHECK 约束 |
| **预估时间** | 3 小时 |
| **预估 Token** | 800 |

---

### 4. Alembic 数据库迁移

| 属性 | 值 |
|------|-----|
| **任务名称** | `alembic-migrations` |
| **描述** | 初始化 Alembic，生成初始迁移脚本，创建 projects, requirements, tasks, cost_records, users, project_memberships 表。添加索引 |
| **预估时间** | 2 小时 |
| **预估 Token** | 500 |

---

### 5. Pydantic Schema 定义

| 属性 | 值 |
|------|-----|
| **任务名称** | `pydantic-schemas` |
| **描述** | 创建所有 Pydantic 请求/响应 Schema：`base.py`, `project.py`, `requirement.py`, `task.py`, `cost.py`, `auth.py`。包含验证器和序列化逻辑 |
| **预估时间** | 2 小时 |
| **预估 Token** | 600 |

---

### 6. 配置管理模块

| 属性 | 值 |
|------|-----|
| **任务名称** | `config-module` |
| **描述** | 创建 `app/config.py`，实现环境变量加载、配置类（Pydantic Settings）、JWT 配置、数据库配置、Redis 配置、外部工具路径配置 |
| **预估时间** | 1 小时 |
| **预估 Token** | 300 |

---

### 7. 安全模块 (JWT + 密码)

| 属性 | 值 |
|------|-----|
| **任务名称** | `security-module` |
| **描述** | 创建 `app/core/security.py`：JWT token 生成/验证、密码哈希（bcrypt）、access_token/refresh_token 逻辑、Token 类型定义 |
| **预估时间** | 2 小时 |
| **预估 Token** | 500 |

---

### 8. 异常处理模块

| 属性 | 值 |
|------|-----|
| **任务名称** | `exceptions-module` |
| **描述** | 创建 `app/core/exceptions.py`：自定义异常类（HTTPException 包装）、错误码枚举（VALIDATION_ERROR, UNAUTHORIZED, PROJECT_NOT_FOUND 等）、统一错误响应格式 |
| **预估时间** | 1 小时 |
| **预估 Token** | 300 |

---

### 9. 依赖注入模块

| 属性 | 值 |
|------|-----|
| **任务名称** | `dependencies-module` |
| **描述** | 创建 `app/dependencies.py`：数据库 Session 依赖、当前用户依赖、JWT 验证依赖、项目权限检查依赖 |
| **预估时间** | 1 小时 |
| **预估 Token** | 300 |

---

### 10. 服务层 (Service Layer)

| 属性 | 值 |
|------|-----|
| **任务名称** | `service-layer` |
| **描述** | 创建服务类：`ProjectService`（项目 CRUD、成员管理）、`RequirementService`（需求 CRUD、树管理）、`TaskService`（任务生命周期）、`CostService`（成本统计） |
| **预估时间** | 4 小时 |
| **预估 Token** | 1000 |

---

### 11. API v1 路由聚合

| 属性 | 值 |
|------|-----|
| **任务名称** | `api-router` |
| **描述** | 创建 `app/api/v1/router.py`，聚合所有子路由（projects, requirements, tasks, costs, auth），设置 API 前缀 `/api/v1` |
| **预估时间** | 0.5 小时 |
| **预估 Token** | 200 |

---

### 12. Auth API 端点

| 属性 | 值 |
|------|-----|
| **任务名称** | `auth-endpoints` |
| **描述** | 实现 `app/api/v1/auth.py`：POST `/login`（登录，返回 JWT）、POST `/register`（注册）、POST `/refresh`（刷新 token）、GET `/me`（获取当前用户） |
| **预估时间** | 2 小时 |
| **预估 Token** | 500 |

---

### 13. Projects API 端点

| 属性 | 值 |
|------|-----|
| **任务名称** | `projects-endpoints` |
| **描述** | 实现 `app/api/v1/projects.py`：GET `/`（列表，分页）、POST `/`（创建项目）、GET `/{project_id}`（详情）、PUT `/{project_id}`（更新）、DELETE `/{project_id}`（删除）、GET `/{project_id}/members`、POST `/{project_id}/members`、DELETE `/{project_id}/members/{user_id}` |
| **预估时间** | 3 小时 |
| **预估 Token** | 800 |

---

### 14. Requirements API 端点 (基础 CRUD)

| 属性 | 值 |
|------|-----|
| **任务名称** | `requirements-endpoints` |
| **描述** | 实现 `app/api/v1/requirements.py`：GET `/`（列表）、POST `/`（创建）、GET `/{requirement_id}`（详情）、PUT `/{requirement_id}`（更新）、DELETE `/{requirement_id}`（删除）、GET `/{requirement_id}/tree` |
| **预估时间** | 2 小时 |
| **预估 Token** | 600 |

---

### 15. Tasks API 端点 (基础 CRUD)

| 属性 | 值 |
|------|-----|
| **任务名称** | `tasks-endpoints` |
| **描述** | 实现 `app/api/v1/tasks.py`：GET `/`（列表）、POST `/`（创建）、GET `/{task_id}`（详情）、PUT `/{task_id}`（更新）、GET `/{task_id}/logs`、`GET /{task_id}/costs` |
| **预估时间** | 2 小时 |
| **预估 Token** | 600 |

---

### 16. Costs API 端点

| 属性 | 值 |
|------|-----|
| **任务名称** | `costs-endpoints` |
| **描述** | 实现 `app/api/v1/costs.py`：GET `/summary`（全局成本汇总）、GET `/projects/{project_id}`（项目成本汇总）、GET `/export`（报表导出 CSV/Excel） |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 17. WebSocket 端点 (基础)

| 属性 | 值 |
|------|-----|
| **任务名称** | `websocket-endpoints` |
| **描述** | 创建 `app/api/ws.py`：WS `/ws/progress` 端点，基础连接管理、认证、心跳机制 |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 18. FastAPI 应用入口

| 属性 | 值 |
|------|-----|
| **任务名称** | `main-app` |
| **描述** | 创建 `app/main.py`：FastAPI 应用初始化、CORS 配置、中间件注册、事件处理器（startup/shutdown）、健康检查端点 `/health`, `/health/ready`, `/health/live` |
| **预估时间** | 1 小时 |
| **预估 Token** | 300 |

---

### 19. 数据库初始化脚本

| 属性 | 值 |
|------|-----|
| **任务名称** | `db-init-script` |
| **描述** | 创建 `app/db/init_db.py`：初始超级用户创建、默认数据初始化、数据库连接测试 |
| **预估时间** | 0.5 小时 |
| **预估 Token** | 150 |

---

## 前端任务 (Frontend Tasks)

### 20. 前端项目初始化

| 属性 | 值 |
|------|-----|
| **任务名称** | `frontend-setup` |
| **描述** | 使用 Vite 初始化 React + TypeScript 项目，安装依赖（React 18, TypeScript 5, Vite 5, axios, react-router-dom, zustand, recharts, tailwindcss, shadcn/ui） |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 21. TailwindCSS + shadcn/ui 配置

| 属性 | 值 |
|------|-----|
| **任务名称** | `tailwind-shadcn-setup` |
| **描述** | 配置 TailwindCSS、PostCSS、创建 `components.json` 用于 shadcn/ui、添加基础组件（button, card, input, select, table, tabs, badge, dialog, dropdown-menu） |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 22. TypeScript 类型定义

| 属性 | 值 |
|------|-----|
| **任务名称** | `typescript-types` |
| **描述** | 创建所有 TypeScript 类型定义：`api.ts`（API 响应类型）、`project.ts`、`requirement.ts`、`task.ts`、`cost.ts`、`user.ts` |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 500 |

---

### 23. API 客户端层

| 属性 | 值 |
|------|-----|
| **任务名称** | `api-client` |
| **描述** | 创建 `src/api/client.ts`（Axios 实例、拦截器）、`src/api/auth.ts`、`src/api/projects.ts`、`src/api/requirements.ts`、`src/api/tasks.ts`、`src/api/costs.ts` |
| **预估时间** | 2 小时 |
| **预估 Token** | 600 |

---

### 24. Zustand Store 状态管理

| 属性 | 值 |
|------|-----|
| **任务名称** | `zustand-stores` |
| **描述** | 创建 Zustand stores：`authStore.ts`（认证状态、JWT 管理）、`projectStore.ts`（项目列表、当前项目）、`requirementStore.ts`（需求状态）、`taskStore.ts`（任务状态、日志管理） |
| **预估时间** | 2.5 小时 |
| **预估 Token** | 700 |

---

### 25. 自定义 Hooks

| 属性 | 值 |
|------|-----|
| **任务名称** | `custom-hooks` |
| **描述** | 创建自定义 React Hooks：`useAuth.ts`（认证逻辑）、`useProjects.ts`（项目数据获取）、`useRequirements.ts`（需求数据获取）、`useTasks.ts`（任务数据获取） |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 26. 布局组件

| 属性 | 值 |
|------|-----|
| **任务名称** | `layout-components` |
| **描述** | 创建布局组件：`Header.tsx`（顶部导航）、`Sidebar.tsx`（侧边栏菜单）、`PageContainer.tsx`（页面容器） |
| **预估时间** | 2 小时 |
| **预估 Token** | 600 |

---

### 27. UI 组件（项目相关）

| 属性 | 值 |
|------|-----|
| **任务名称** | `project-ui-components` |
| **描述** | 创建项目相关组件：`ProjectCard.tsx`（项目卡片）、`ProjectForm.tsx`（项目表单）、`PlatformBadge.tsx`（平台标签：Android/iOS/鸿蒙） |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 28. UI 组件（通用）

| 属性 | 值 |
|------|-----|
| **任务名称** | `shared-ui-components` |
| **描述** | 创建通用组件：`LoadingSpinner.tsx`、`EmptyState.tsx`、`ErrorMessage.tsx`、`ConfirmDialog.tsx`、`DataTable.tsx` |
| **预估时间** | 1 小时 |
| **预估 Token** | 300 |

---

### 29. 路由配置

| 属性 | 值 |
|------|-----|
| **任务名称** | `routing` |
| **描述** | 配置 React Router：`App.tsx`、路由结构（/login, /register, /dashboard, /projects, /projects/:projectId, /projects/:projectId/requirements, /projects/:projectId/tasks, /projects/:projectId/costs）、ProtectedRoute 组件 |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 30. Dashboard 页面

| 属性 | 值 |
|------|-----|
| **任务名称** | `dashboard-page` |
| **描述** | 创建 `/dashboard` 页面：项目统计卡片（总数/活跃/已完成）、最近活动列表、成本趋势图表（Recharts）、任务状态分布饼图、快速操作按钮 |
| **预估时间** | 3 小时 |
| **预估 Token** | 800 |

---

### 31. Projects 列表页面

| 属性 | 值 |
|------|-----|
| **任务名称** | `projects-page` |
| **描述** | 创建 `/projects` 页面：项目列表展示（表格或卡片视图）、筛选/搜索功能、创建项目按钮、分页 |
| **预估时间** | 2 小时 |
| **预估 Token** | 600 |

---

### 32. Project Detail 页面

| 属性 | 值 |
|------|-----|
| **任务名称** | `project-detail-page` |
| **描述** | 创建 `/projects/:projectId` 页面：项目头部（名称、平台 badge、状态）、Tab 导航（Overview/Requirements/Tasks/Costs/Settings）、Overview 显示仓库链接、环境变量、团队成员 |
| **预估时间** | 3 小时 |
| **预估 Token** | 800 |

---

### 33. Login/Register 页面

| 属性 | 值 |
|------|-----|
| **任务名称** | `auth-pages` |
| **描述** | 创建 `/login` 和 `/register` 页面：表单验证、错误提示、登录后重定向到 dashboard |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

### 34. 工具函数库

| 属性 | 值 |
|------|-----|
| **任务名称** | `utils-library` |
| **描述** | 创建 `src/lib/utils.ts`（className 合并、日期格式化）、`src/lib/formatters.ts`（日期、货币格式化）、`src/lib/validators.ts`（表单验证规则） |
| **预估时间** | 1 小时 |
| **预估 Token** | 300 |

---

### 35. WebSocket Hook

| 属性 | 值 |
|------|-----|
| **任务名称** | `websocket-hook` |
| **描述** | 创建 `useWebSocket.ts` hook：连接管理、消息处理（task_progress, task_log, task_completed, task_failed）、自动重连、心跳检测 |
| **预估时间** | 1.5 小时 |
| **预估 Token** | 400 |

---

## 任务汇总

### 按模块分组

| 模块 | 任务数 | 总预估时间 | 总预估 Token |
|------|--------|-----------|-------------|
| 后端 - 项目初始化与配置 | 1 | 2h | 500 |
| 后端 - 数据库层 | 4 | 8h | 2100 |
| 后端 - 核心模块 | 4 | 5h | 1400 |
| 后端 - 服务层 | 1 | 4h | 1000 |
| 后端 - API 端点 | 8 | 15.5h | 4000 |
| **后端小计** | **18** | **34.5h** | **9000** |
| 前端 - 项目初始化 | 2 | 3h | 800 |
| 前端 - 核心基础设施 | 4 | 6.5h | 1700 |
| 前端 - 页面与组件 | 9 | 16.5h | 4500 |
| **前端小计** | **15** | **26h** | **7000** |
| **总计** | **33** | **60.5h** | **16000** |

### 阶段验收标准

- [x] 后端所有 API 端点返回正确状态码
- [x] 数据库迁移成功执行，所有表创建
- [x] JWT 认证流程完整（登录/注册/刷新/获取用户）
- [x] 前端路由正常工作，所有页面可访问
- [x] 项目 CRUD 操作从前端完整调用后端
- [x] 状态管理（Zustand）正常工作
- [x] 前端 TypeScript 无编译错误
- [x] 基础 UI 组件样式一致
- [x] 单元测试覆盖核心服务层（>70%）- 注：API层测试覆盖57%，服务层在 Phase 2 重构后增加
