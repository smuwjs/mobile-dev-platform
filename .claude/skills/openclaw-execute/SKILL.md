---
name: openclaw-execute
description: Execute mobile development tasks in the OpenClaw platform. Use when the user wants to run, pause, resume, or terminate development tasks managed by the Mobile Dev Platform.
license: MIT
compatibility: Requires OpenClaw platform API running at localhost:8000
metadata:
  author: openclaw
  version: "1.0"
  generatedBy: "1.0"
---

Execute and manage development tasks in the OpenClaw Mobile Dev Platform.

This skill allows Claude Code to interact with the platform's task execution system through tmux sessions.

---

**Prerequisites**

1. The OpenClaw backend must be running at `http://localhost:8000`
2. tmux must be installed on the system
3. Valid API key must be configured for authentication

**API Base URL**: `http://localhost:8000/api/v1`

---

**Available Operations**

1. **Start Task Execution** - Create a tmux session and execute a development task
2. **Pause Execution** - Suspend a running task (sends SIGSTOP)
3. **Resume Execution** - Continue a paused task (sends SIGCONT)
4. **Terminate Execution** - Kill a tmux session and stop execution
5. **Get Execution Status** - Check current status and progress of an execution
6. **Get Execution Output** - Capture real-time output from tmux session

---

**Step-by-Step Instructions**

### 1. Starting Task Execution

```bash
# Create execution session
curl -X POST http://localhost:8000/api/v1/exec/sessions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{
    "task_id": "<task-id>",
    "working_dir": "/path/to/project"
  }'

# Execute task steps
curl -X POST http://localhost:8000/api/v1/exec/execute/<execution-id> \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{
    "steps": [
      {"title": "Setup", "command": "npm install"},
      {"title": "Build", "command": "npm run build"},
      {"title": "Test", "command": "npm test"}
    ]
  }'
```

### 2. Monitoring Execution

```bash
# Get execution status
curl http://localhost:8000/api/v1/exec/status/<execution-id> \
  -H "X-API-Key: <your-api-key>"

# Get real-time output
curl http://localhost:8000/api/v1/exec/output/<execution-id> \
  -H "X-API-Key: <your-api-key>"
```

### 3. Controlling Execution

```bash
# Pause execution
curl -X POST http://localhost:8000/api/v1/exec/pause/<execution-id> \
  -H "X-API-Key: <your-api-key>"

# Resume execution
curl -X POST http://localhost:8000/api/v1/exec/resume/<execution-id> \
  -H "X-API-Key: <your-api-key>"

# Terminate execution
curl -X POST http://localhost:8000/api/v1/exec/terminate/<execution-id> \
  -H "X-API-Key: <your-api-key>"
```

### 4. Using WebSocket for Real-time Updates

```javascript
// Connect to WebSocket for real-time execution updates
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: "subscribe",
    execution_id: "<execution-id>"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Execution update:", data);
};
```

---

**Execution States**

| State | Description |
|-------|-------------|
| `pending` | Execution created, not yet started |
| `running` | Task is actively executing |
| `paused` | Execution suspended (SIGSTOP) |
| `completed` | All steps completed successfully |
| `failed` | Execution failed (error in steps) |
| `terminated` | Execution manually stopped |

---

**Error Handling**

- **No output timeout (5 min)**: Task is marked as failed if no output detected for 5 minutes
- **Compilation failure**: Detected by parsing error patterns in output
- **API rate limiting**: Automatic retry with exponential backoff

---

**Environment Variables**

| Variable | Description |
|----------|-------------|
| `OPENCLAW_API_URL` | Backend API URL (default: http://localhost:8000) |
| `OPENCLAW_API_KEY` | API key for authentication |
| `OPENCLAW_TMUX_SESSION_PREFIX` | tmux session name prefix (default: claude_exec_) |

---

**Implementation Details**

- tmux sessions are named with prefix `claude_exec_` followed by first 8 chars of task_id
- Output is captured using `tmux capture-pane` with 1000 line buffer
- Pause/Resume use SIGSTOP/SIGCONT signals to the tmux pane process
- All executions are logged to database via TaskLog model
