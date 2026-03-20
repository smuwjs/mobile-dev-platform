# Mobile Dev Platform - Architecture Design

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend (React + TS + Vite)                 │
│  ┌──────────┐  ┌─────────────┐  ┌───────────┐  ┌──────────┐  ┌─────────┐ │
│  │Dashboard│  │Requirements │  │Task Runner│  │ Cost     │  │Settings │ │
│  │         │  │ Manager     │  │ Monitor   │  │ Analyzer │  │         │ │
│  └────┬─────┘  └──────┬──────┘  └─────┬─────┘  └────┬────┘  └────┬────┘ │
│       └───────────────┼───────────────┼─────────────┼───────────┘       │
│                       │    WebSocket / REST API    │                     │
└───────────────────────┼────────────────┼────────────┼────────────────────┘
                        │                │            │
┌───────────────────────┼────────────────┼────────────┼────────────────────┐
│                       │   API Gateway (FastAPI + Uvicorn)                 │
│  ┌────────────────────┴────────────────┴────────────┴────────────────┐  │
│  │                    Authentication (JWT)                             │  │
│  └────────────────────┬────────────────┬────────────┬────────────────┘  │
│                      │                │            │                     │
│  ┌───────────────────┴───┐  ┌─────────┴─────────┐  ┌────────────────┐ │
│  │     REST API Layer   │  │  WebSocket Handler  │  │  Celery Workers│ │
│  │  ┌─────┐ ┌─────────┐ │  │                     │  │  ┌────────────┐ │ │
│  │  │Proj │ │Require- │ │  │  /ws/progress       │  │  │Requirement│ │ │
│  │  │ects │ │ments    │ │  │  /ws/tasks          │  │  │ Decomposer│ │ │
│  │  └─────┘ └─────────┘ │  │                     │  │  ├────────────┤ │ │
│  │  ┌─────┐ ┌─────────┐ │  │                     │  │  │Task        │ │ │
│  │  │Tasks│ │ Costs   │ │  │                     │  │  │Executor    │ │ │
│  │  └─────┘ └─────────┘ │  │                     │  │  └────────────┘ │ │
│  └──────────────────────┘  └─────────────────────┘  └────────────────┘ │
│                                    │                      │            │
└────────────────────────────────────┼──────────────────────┼────────────┘
                                     │                      │
              ┌───────────────────────┼──────────────────────┘
              │                      │
        ┌─────┴─────┐          ┌─────┴─────┐
        │ PostgreSQL│          │   Redis   │
        │  (Primary)│          │  (Broker) │
        └───────────┘          └───────────┘
              │
    ┌─────────┴─────────┐
    │   External APIs   │
    │ ┌───────────────┐ │
    │ │ OpenSpec CLI  │ │
    │ ├───────────────┤ │
    │ │ Claude Code   │ │
    │ │ CLI + MCP     │ │
    │ └───────────────┘ │
    └───────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Backend Framework** | FastAPI | 0.109+ | High-performance async API framework |
| **WSGI Server** | Uvicorn | 0.27+ | ASGI server with uvloop |
| **Database** | PostgreSQL | 15+ | Primary data store |
| **ORM** | SQLAlchemy | 2.0+ | Async ORM with type safety |
| **Async Driver** | asyncpg | 0.29+ | PostgreSQL async driver |
| **Task Queue** | Celery | 5.3+ | Distributed task queue |
| **Message Broker** | Redis | 7+ | Celery broker & caching |
| **Auth** | python-jose | 3.3+ | JWT token handling |
| **Frontend Framework** | React | 18+ | UI framework |
| **Language** | TypeScript | 5.3+ | Type safety |
| **Build Tool** | Vite | 5+ | Fast bundling |
| **Styling** | TailwindCSS | 3.4+ | Utility-first CSS |
| **UI Components** | shadcn/ui | latest | Accessible components |
| **State Management** | Zustand | 4.5+ | Lightweight state |
| **Charts** | Recharts | 2.12+ | Data visualization |

---

## 2. Backend Architecture

### 2.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # API v1 router aggregation
│   │   │   ├── projects.py         # Project endpoints
│   │   │   ├── requirements.py     # Requirement endpoints
│   │   │   ├── tasks.py            # Task endpoints
│   │   │   ├── costs.py            # Cost endpoints
│   │   │   └── auth.py             # Auth endpoints
│   │   └── ws.py                   # WebSocket endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # JWT, password hashing
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── events.py              # Startup/shutdown events
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy base
│   │   ├── project.py             # Project model
│   │   ├── requirement.py         # Requirement model
│   │   ├── task.py                # Task model
│   │   ├── cost_record.py         # CostRecord model
│   │   └── user.py                # User model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py                # Pydantic base schemas
│   │   ├── project.py             # Project schemas
│   │   ├── requirement.py         # Requirement schemas
│   │   ├── task.py                # Task schemas
│   │   └── cost.py                # Cost schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── project_service.py     # Project business logic
│   │   ├── requirement_service.py  # Requirement business logic
│   │   ├── task_service.py         # Task business logic
│   │   ├── cost_service.py        # Cost calculation
│   │   ├── openspec_service.py    # OpenSpec CLI wrapper
│   │   └── claude_service.py      # Claude Code CLI wrapper
│   │
│   ├── celery/
│   │   ├── __init__.py
│   │   ├── app.py                 # Celery app configuration
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── decompose.py       # Requirement decomposition task
│   │       └── execute.py         # Task execution task
│   │
│   └── db/
│       ├── __init__.py
│       ├── session.py             # Database session management
│       └── init_db.py             # Database initialization
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── api/
│   ├── services/
│   └── factories/                 # Factory fixtures for testing
│
├── alembic/                       # Database migrations
│   ├── env.py
│   └── versions/
│
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

### 2.2 API Layer Design

#### 2.2.1 REST API Endpoints

```
/api/v1/auth
├── POST   /login                  # User login
├── POST   /register               # User registration
├── POST   /refresh                # Refresh access token
└── GET    /me                     # Get current user

/api/v1/projects
├── GET    /                       # List projects (paginated)
├── POST   /                       # Create project
├── GET    /{project_id}           # Get project details
├── PUT    /{project_id}           # Update project
├── DELETE /{project_id}           # Delete project
├── GET    /{project_id}/members   # List project members
├── POST   /{project_id}/members   # Add project member
└── DELETE /{project_id}/members/{user_id}  # Remove member

/api/v1/projects/{project_id}/requirements
├── GET    /                       # List requirements
├── POST   /                       # Create requirement
├── GET    /{requirement_id}        # Get requirement details
├── PUT    /{requirement_id}        # Update requirement
├── DELETE /{requirement_id}        # Delete requirement
├── POST   /{requirement_id}/decompose  # Trigger decomposition
└── GET    /{requirement_id}/tree  # Get decomposed tree

/api/v1/projects/{project_id}/tasks
├── GET    /                       # List tasks
├── POST   /                       # Create task
├── GET    /{task_id}              # Get task details
├── PUT    /{task_id}              # Update task
├── POST   /{task_id}/execute      # Execute task (Claude Code)
├── POST   /{task_id}/cancel       # Cancel running task
├── GET    /{task_id}/logs         # Get task logs
└── GET    /{task_id}/costs        # Get task cost records

/api/v1/costs
├── GET    /summary                # Cost summary (global)
├── GET    /projects/{project_id}  # Project cost summary
└── GET    /export                 # Export cost report (CSV/Excel)

/api/v1/ws
└── WS     /progress               # WebSocket for real-time progress
```

#### 2.2.2 Request/Response Schemas

**Create Project Request**
```json
{
  "name": "My Mobile App",
  "platform": "android",
  "repository_url": "https://github.com/org/app",
  "environment_vars": {
    "API_BASE_URL": "https://api.example.com",
    "DEBUG": "false"
  }
}
```

**Create Requirement Request**
```json
{
  "content": "用户需要能够通过手机号注册账号，并接收验证码完成验证",
  "parent_id": null
}
```

**Task Execution Response**
```json
{
  "task_id": "uuid",
  "status": "queued",
  "celery_task_id": "uuid",
  "estimated_duration_seconds": 120
}
```

### 2.3 Database Schema

#### 2.3.1 Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    User      │       │     Project      │       │   Requirement│
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │◄──┐   │ id (PK)          │◄──┐   │ id (PK)      │
│ email        │   │   │ name             │   │   │ project_id(FK)│
│ password_hash│   └──►│ platform         │   └──►│ content      │
│ is_active    │       │ repository_url   │       │ decomposed_  │
│ created_at   │       │ environment_vars │       │   tree       │
└──────────────┘       │ created_at       │       │ status       │
       │               │ updated_at       │       │ parent_id(FK)│
       │               └──────────────────┘       │ created_at   │
       │                      │                    │ updated_at   │
       │                      │                    └──────────────┘
       │                      │                           │
       │                      │                     ┌──────┴──────┐
       ▼                      ▼                     │             │
┌──────────────────┐   ┌──────────────────┐          │             │
│ ProjectMembership│   │      Task        │◄────────┘             │
├──────────────────┤   ├──────────────────┤                        │
│ id (PK)          │   │ id (PK)          │                        │
│ project_id (FK)  │───┤ project_id (FK) │                        │
│ user_id (FK)     │───┤ requirement_id  │                        │
│ role             │   │   (FK)          │                        │
│ joined_at        │   │ content         │                        │
└──────────────────┘   │ status          │                        │
                      │ claude_session_id│                        │
                      │ logs             │                        │
                      │ created_at       │                        │
                      │ started_at       │                        │
                      │ completed_at     │                        │
                      └──────────────────┘                        │
                             │                                    │
                             ▼                                    │
                      ┌──────────────────┐                        │
                      │   CostRecord     │                        │
                      ├──────────────────┤                        │
                      │ id (PK)          │                        │
                      │ task_id (FK)     │────────────────────────┘
                      │ input_tokens     │
                      │ output_tokens    │
                      │ duration_ms      │
                      │ estimated_cost   │
                      │ created_at       │
                      └──────────────────┘
```

#### 2.3.2 Table Definitions

**projects**
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('android', 'ios', 'harmony')),
    repository_url TEXT,
    environment_vars JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_projects_platform ON projects(platform);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
```

**requirements**
```sql
CREATE TABLE requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    decomposed_tree JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'decomposing', 'decomposed', 'failed')),
    parent_id UUID REFERENCES requirements(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_requirements_project_id ON requirements(project_id);
CREATE INDEX idx_requirements_status ON requirements(status);
CREATE INDEX idx_requirements_parent_id ON requirements(parent_id);
```

**tasks**
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    requirement_id UUID REFERENCES requirements(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    claude_session_id VARCHAR(255),
    logs TEXT[] DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**cost_records**
```sql
CREATE TABLE cost_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    estimated_cost DECIMAL(10, 6) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cost_records_task_id ON cost_records(task_id);
CREATE INDEX idx_cost_records_created_at ON cost_records(created_at DESC);
```

### 2.4 Service Layer Design

#### 2.4.1 Service Responsibilities

| Service | Responsibility | Public API |
|---------|---------------|------------|
| `ProjectService` | Project CRUD, member management | `create()`, `get()`, `update()`, `delete()`, `add_member()` |
| `RequirementService` | Requirement CRUD, tree management | `create()`, `get()`, `decompose()`, `get_tree()` |
| `TaskService` | Task lifecycle, execution queue | `create()`, `execute()`, `cancel()`, `get_logs()` |
| `CostService` | Cost calculation, reporting | `calculate()`, `get_summary()`, `export_report()` |
| `OpenSpecService` | OpenSpec CLI integration | `decompose(content)` |
| `ClaudeService` | Claude Code CLI integration | `execute_task()`, `cancel_task()`, `get_session_logs()` |

#### 2.4.2 Service Interaction Flow

```
Client Request
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                         │
│   POST /projects/{id}/requirements/{req_id}/decompose           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RequirementService                         │
│              requirement_service.decompose(req_id)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Task Queue                            │
│          celery_app.send_task('decompose_requirement')           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Worker                               │
│   1. OpenSpecService.decompose(content)                          │
│   2. Parse output to requirement tree                            │
│   3. Create child requirements                                    │
│   4. Update parent requirement status                            │
│   5. Emit WebSocket event                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.5 Celery Task Design

#### 2.5.1 Task Definitions

**decompose_requirement**
```python
@celery_app.task(bind=True, max_retries=3)
def decompose_requirement(self, requirement_id: UUID):
    """Decompose a requirement using OpenSpec CLI."""
    # 1. Fetch requirement from DB
    # 2. Update status to 'decomposing'
    # 3. Call OpenSpecService.decompose()
    # 4. Parse result and create child requirements
    # 5. Update parent status to 'decomposed'
    # 6. Publish WebSocket event
    # 7. Return decomposed tree
```

**execute_claude_task**
```python
@celery_app.task(bind=True, max_retries=3)
def execute_claude_task(self, task_id: UUID, project_path: str):
    """Execute a development task using Claude Code."""
    # 1. Fetch task and project from DB
    # 2. Update status to 'running'
    # 3. Start Claude Code CLI process
    # 4. Stream logs via WebSocket
    # 5. Record cost on completion
    # 6. Update status to 'completed' or 'failed'
```

#### 2.5.2 Celery Beat Schedule

```python
CELERY_BEAT_SCHEDULE = {
    'cleanup-failed-tasks': {
        'task': 'celery.tasks.maintenance.cleanup_failed_tasks',
        'schedule': crontab(minute='*/30'),
    },
    'sync-project-status': {
        'task': 'celery.tasks.maintenance.sync_project_status',
        'schedule': crontab(minute='*/5'),
    },
}
```

### 2.6 Authentication & Authorization

#### 2.6.1 JWT Token Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Login Flow                               │
│                                                                  │
│  Client                    Server                    DB           │
│    │                         │                         │        │
│    │──── POST /auth/login ───►│                         │        │
│    │   {email, password}      │                         │        │
│    │                         │──── SELECT user ───────►│        │
│    │                         │◄──── user record ───────│        │
│    │                         │                         │        │
│    │                         │ Verify password hash     │        │
│    │                         │                         │        │
│    │                         │ Generate JWT access      │        │
│    │                         │ + refresh tokens         │        │
│    │◄─── {access_token, ────│                         │        │
│    │      refresh_token}     │                         │        │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.6.2 Token Structure

```json
{
  "access_token": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "exp": 1710000000,
    "iat": 1709996400,
    "type": "access"
  },
  "refresh_token": {
    "sub": "user-uuid",
    "exp": 1710090000,
    "iat": 1709996400,
    "type": "refresh"
  }
}
```

---

## 3. Frontend Architecture

### 3.1 Project Structure

```
frontend/
├── public/
│   └── favicon.ico
│
├── src/
│   ├── __init__.py
│   ├── main.tsx                     # Application entry point
│   ├── App.tsx                      # Root component
│   ├── index.css                    # Global styles + Tailwind
│   │
│   ├── api/                         # API client layer
│   │   ├── __init__.py
│   │   ├── client.ts               # Axios instance
│   │   ├── projects.ts             # Project API calls
│   │   ├── requirements.ts         # Requirement API calls
│   │   ├── tasks.ts                # Task API calls
│   │   ├── costs.ts                # Cost API calls
│   │   └── auth.ts                 # Auth API calls
│   │
│   ├── components/                  # Shared components
│   │   ├── __init__.py
│   │   ├── ui/                     # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── badge.tsx
│   │   │
│   │   ├── layout/                 # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── PageContainer.tsx
│   │   │
│   │   ├── projects/               # Project-related components
│   │   │   ├── ProjectCard.tsx
│   │   │   ├── ProjectForm.tsx
│   │   │   └── PlatformBadge.tsx
│   │   │
│   │   ├── requirements/          # Requirement components
│   │   │   ├── RequirementTree.tsx
│   │   │   ├── RequirementItem.tsx
│   │   │   └── DecomposeButton.tsx
│   │   │
│   │   ├── tasks/                  # Task components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskLogViewer.tsx
│   │   │   └── ExecuteButton.tsx
│   │   │
│   │   └── costs/                  # Cost components
│   │       ├── CostSummaryCard.tsx
│   │       ├── CostChart.tsx
│   │       └── CostTable.tsx
│   │
│   ├── hooks/                      # Custom React hooks
│   │   ├── __init__.py
│   │   ├── useAuth.ts             # Authentication hook
│   │   ├── useWebSocket.ts        # WebSocket hook
│   │   ├── useProjects.ts         # Projects data hook
│   │   ├── useRequirements.ts     # Requirements data hook
│   │   └── useTasks.ts            # Tasks data hook
│   │
│   ├── stores/                     # Zustand stores
│   │   ├── __init__.py
│   │   ├── authStore.ts           # Auth state
│   │   ├── projectStore.ts        # Project state
│   │   ├── requirementStore.ts    # Requirement state
│   │   └── taskStore.ts           # Task state
│   │
│   ├── pages/                      # Page components (routes)
│   │   ├── __init__.py
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ProjectsPage.tsx
│   │   ├── ProjectDetailPage.tsx
│   │   ├── RequirementsPage.tsx
│   │   ├── TasksPage.tsx
│   │   └── CostsPage.tsx
│   │
│   ├── lib/                        # Utilities
│   │   ├── __init__.py
│   │   ├── utils.ts               # Utility functions
│   │   ├── formatters.ts          # Date, currency formatters
│   │   └── validators.ts          # Form validation
│   │
│   └── types/                      # TypeScript types
│       ├── __init__.py
│       ├── api.ts                 # API response types
│       ├── project.ts             # Project types
│       ├── requirement.ts         # Requirement types
│       ├── task.ts                # Task types
│       └── cost.ts                # Cost types
│
├── components.json                 # shadcn/ui config
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
├── index.html
├── package.json
└── Dockerfile
```

### 3.2 State Management

#### 3.2.1 Zustand Store Design

**authStore**
```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}
```

**projectStore**
```typescript
interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: CreateProjectInput) => Promise<Project>;
  updateProject: (id: string, data: UpdateProjectInput) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
}
```

**taskStore**
```typescript
interface TaskState {
  tasks: Task[];
  currentTask: Task | null;
  taskLogs: Map<string, string[]>;
  executeTask: (taskId: string) => Promise<void>;
  cancelTask: (taskId: string) => Promise<void>;
  subscribeToLogs: (taskId: string) => void;
}
```

### 3.3 WebSocket Integration

```typescript
// useWebSocket.ts
export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://${API_BASE}${url}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);

      // Handle different message types
      switch (data.type) {
        case 'task_progress':
          taskStore.updateTaskProgress(data.task_id, data.progress);
          break;
        case 'task_log':
          taskStore.appendLog(data.task_id, data.log);
          break;
        case 'task_completed':
          taskStore.setTaskCompleted(data.task_id, data.result);
          break;
        case 'task_failed':
          taskStore.setTaskFailed(data.task_id, data.error);
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [url]);

  return { messages, sendMessage: wsRef.current?.send };
}
```

### 3.4 Component Architecture

#### 3.4.1 Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                         Header                                   │
│  [Logo]  [Projects ▼]  [Dashboard]  [Costs]      [User Avatar ▼] │
├────────────┬────────────────────────────────────────────────────┤
│            │                                                      │
│  Sidebar   │                    Main Content                     │
│            │                                                      │
│  Project   │   ┌─────────────────────────────────────────────┐   │
│  Navigation│   │                                             │   │
│            │   │              Page Content                   │   │
│  - Overview│   │                                             │   │
│  - Require │   │                                             │   │
│  - Tasks   │   │                                             │   │
│  - Costs   │   │                                             │   │
│            │   └─────────────────────────────────────────────┘   │
│            │                                                      │
└────────────┴────────────────────────────────────────────────────┘
```

#### 3.4.2 Key Page Specifications

**Dashboard Page** (`/dashboard`)
- Project statistics cards (total, active, completed)
- Recent activity feed
- Cost trend chart (last 7/30 days)
- Task status distribution pie chart
- Quick actions (new project, new requirement)

**Project Detail Page** (`/projects/:id`)
- Project header with platform badge and status
- Tab navigation: Overview | Requirements | Tasks | Costs | Settings
- Overview: Repository link, environment variables, team members
- Requirements: Tree view with decompose actions
- Tasks: Kanban-style board (Queued | Running | Completed | Failed)
- Costs: Per-task cost breakdown table

### 3.5 Routing

```typescript
// App.tsx
const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'projects',
        element: <ProjectsPage />,
      },
      {
        path: 'projects/:projectId',
        element: <ProjectDetailPage />,
        children: [
          {
            index: true,
            element: <ProjectOverview />,
          },
          {
            path: 'requirements',
            element: <RequirementsPage />,
          },
          {
            path: 'tasks',
            element: <TasksPage />,
          },
          {
            path: 'costs',
            element: <CostsPage />,
          },
        ],
      },
    ],
  },
]);
```

---

## 4. External Integrations

### 4.1 OpenSpec Integration

```python
# openspec_service.py
import subprocess
import json
from pathlib import Path

class OpenSpecService:
    def __init__(self, openspec_path: str = "/usr/local/bin/openspec"):
        self.openspec_path = openspec_path

    def decompose(self, content: str) -> dict:
        """
        Call OpenSpec CLI to decompose requirement content.
        Returns structured requirement tree.
        """
        result = subprocess.run(
            [self.openspec_path, "decompose", "--format", "json"],
            input=content,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise OpenSpecError(result.stderr)

        return json.loads(result.stdout)
```

### 4.2 Claude Code Integration

```python
# claude_service.py
import subprocess
import json
import uuid
from pathlib import Path

class ClaudeService:
    def __init__(self, claude_path: str = "/usr/local/bin/claude"):
        self.claude_path = claude_path

    def execute_task(
        self,
        task_id: uuid.UUID,
        project_path: str,
        instruction: str,
        on_log: Callable[[str], None],
        on_cost: Callable[[dict], None]
    ) -> dict:
        """
        Execute development task using Claude Code CLI.
        Streams logs and cost updates via callbacks.
        """
        session_id = f"task-{task_id}"

        process = subprocess.Popen(
            [
                self.claude_path,
                "--session", session_id,
                "--no-input",
                "dev",
                instruction
            ],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        total_input_tokens = 0
        total_output_tokens = 0

        for line in process.stdout:
            # Parse log line
            on_log(line.strip())

            # Parse usage line (Claude Code outputs usage metrics)
            if line.startswith("[USAGE]"):
                usage = json.loads(line[8:])
                total_input_tokens = usage.get("input_tokens", 0)
                total_output_tokens = usage.get("output_tokens", 0)
                on_cost({
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "estimated_cost": self.calculate_cost(total_input_tokens, total_output_tokens)
                })

        process.wait()

        if process.returncode != 0:
            raise ClaudeExecutionError(f"Claude Code exited with {process.returncode}")

        return {"session_id": session_id, "status": "completed"}

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate estimated cost based on token usage."""
        # Claude Opus 4 pricing (example)
        INPUT_COST_PER_1K = Decimal("0.015")
        OUTPUT_COST_PER_1K = Decimal("0.075")

        return (
            Decimal(input_tokens) / 1000 * INPUT_COST_PER_1K +
            Decimal(output_tokens) / 1000 * OUTPUT_COST_PER_1K
        )
```

---

## 5. Deployment Architecture

### 5.1 Container Structure

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://backend:8000

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/mobile_dev_platform
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - OPENSPEC_PATH=/usr/local/bin/openspec
      - CLAUDE_CODE_PATH=/usr/local/bin/claude
    depends_on:
      - db
      - redis

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery.app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/mobile_dev_platform
      - REDIS_URL=redis://redis:6379/0
      - OPENSPEC_PATH=/usr/local/bin/openspec
      - CLAUDE_CODE_PATH=/usr/local/bin/claude
    depends_on:
      - db
      - redis
      - backend

  # Celery Beat (Scheduler)
  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery.app beat --loglevel=info
    depends_on:
      - redis

  # PostgreSQL
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mobile_dev_platform

  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 5.2 Environment Configuration

**Backend (.env)**
```env
# Application
APP_NAME=Mobile Dev Platform
DEBUG=false
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mobile_dev_platform
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Auth
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# External Tools
OPENSPEC_PATH=/usr/local/bin/openspec
CLAUDE_CODE_PATH=/usr/local/bin/claude
CLAUDE_API_KEY=sk-ant-...  # Optional: for direct API access

# CORS
CORS_ORIGINS=http://localhost:3000,https://app.example.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Cost Calculation
CLAUDE_MODEL=claude-opus-4-5
INPUT_TOKEN_COST_PER_1K=0.015
OUTPUT_TOKEN_COST_PER_1K=0.075
```

**Frontend (.env)**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

---

## 6. Security Considerations

### 6.1 Authentication
- JWT tokens with short expiration (30 min access, 7 day refresh)
- Password hashing with bcrypt (cost factor 12)
- Rate limiting on auth endpoints (5 attempts/minute)

### 6.2 API Security
- CORS configured for allowed origins only
- Request validation with Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- Input sanitization for command execution

### 6.3 External Tool Execution
- Claude Code runs in isolated project directories
- Environment variables scoped per project
- Command injection prevention via strict input validation
- Execution timeout (max 30 minutes per task)

---

## 7. Error Handling

### 7.1 Backend Error Responses

```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project with ID 'uuid' not found",
    "details": {
      "project_id": "uuid"
    }
  }
}
```

### 7.2 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Invalid or expired token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `PROJECT_NOT_FOUND` | 404 | Project does not exist |
| `REQUIREMENT_NOT_FOUND` | 404 | Requirement does not exist |
| `TASK_NOT_FOUND` | 404 | Task does not exist |
| `TASK_ALREADY_RUNNING` | 409 | Task is already executing |
| `OPENSPEC_ERROR` | 500 | OpenSpec CLI execution failed |
| `CLAUDE_ERROR` | 500 | Claude Code execution failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 8. Monitoring & Observability

### 8.1 Logging Strategy
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request ID tracking
- Sensitive data masking

### 8.2 Metrics
- API request latency (p50, p95, p99)
- Task execution duration
- Celery queue depth
- Database query performance
- Claude Code token consumption

### 8.3 Health Checks
- `/health` - Basic health check
- `/health/ready` - Readiness check (DB + Redis)
- `/health/live` - Liveness check
