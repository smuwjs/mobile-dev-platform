import { useEffect, useState, useCallback } from 'react'
import {
  Plus,
  RefreshCw,
  Play,
  Eye,
  CheckCircle2,
  AlertCircle,
  Circle,
  Loader2,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useTaskStore, useExecutionLogStore, type CeleryTaskState, type ExecutionLog } from '@/stores'
import type { Task } from '@/types'
import { getWebSocketClient, type WebSocketMessage } from '@/lib/websocket'

type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'

interface KanbanColumn {
  status: TaskStatus
  label: string
  color: string
  icon: React.ElementType
}

const columns: KanbanColumn[] = [
  { status: 'pending', label: '待开始', color: 'bg-gray-100', icon: Circle },
  { status: 'running', label: '进行中', color: 'bg-blue-100', icon: Loader2 },
  { status: 'completed', label: '已完成', color: 'bg-green-100', icon: CheckCircle2 },
  { status: 'failed', label: '失败', color: 'bg-red-100', icon: AlertCircle },
]

const priorityColors: Record<Task['priority'], string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-red-100 text-red-700',
}

function TaskCard({
  task,
  onViewLogs,
  onExecute,
}: {
  task: Task
  onViewLogs: (task: Task) => void
  onExecute: (task: Task) => void
}) {
  const Icon = {
    pending: Circle,
    running: Loader2,
    completed: CheckCircle2,
    failed: AlertCircle,
  }[task.status] as React.ElementType

  return (
    <Card className="mb-3 cursor-pointer hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Icon
                className={`h-4 w-4 ${
                  task.status === 'running'
                    ? 'animate-spin text-blue-500'
                    : task.status === 'completed'
                    ? 'text-green-500'
                    : task.status === 'failed'
                    ? 'text-red-500'
                    : 'text-gray-400'
                }`}
              />
              <h4 className="font-medium text-sm line-clamp-1">{task.title}</h4>
            </div>
            <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
              {task.description}
            </p>
            <div className="flex items-center gap-2">
              <Badge className={priorityColors[task.priority]} variant="secondary" style={{ fontSize: '10px' }}>
                {task.priority === 'low' ? '低' : task.priority === 'medium' ? '中' : '高'}
              </Badge>
              {task.status === 'running' && (
                <span className="text-xs text-blue-600">执行中...</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 mt-3">
          {task.status === 'pending' && (
            <Button variant="ghost" size="sm" className="h-7" onClick={() => onExecute(task)}>
              <Play className="h-3 w-3 mr-1" />
              执行
            </Button>
          )}
          <Button variant="ghost" size="sm" className="h-7" onClick={() => onViewLogs(task)}>
            <Eye className="h-3 w-3 mr-1" />
            日志
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function ExecutionLogViewer({
  task,
  logs,
  onClose,
}: {
  task: Task
  logs: ExecutionLog[]
  onClose: () => void
}) {
  return (
    <div className="space-y-4">
      <DialogHeader>
        <DialogTitle>任务日志: {task.title}</DialogTitle>
        <DialogDescription>实时任务执行日志</DialogDescription>
      </DialogHeader>

      <Card className="bg-black text-green-400 font-mono text-xs">
        <ScrollArea className="h-[400px] p-4">
          {logs.length === 0 ? (
            <p className="text-gray-500">暂无日志</p>
          ) : (
            logs.map((log) => (
              <div key={log.id} className="flex gap-2 mb-1">
                <span className="text-gray-500 shrink-0">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span
                  className={
                    log.level === 'error'
                      ? 'text-red-400'
                      : log.level === 'warning'
                      ? 'text-yellow-400'
                      : ''
                  }
                >
                  [{log.level.toUpperCase()}] {log.message}
                </span>
              </div>
            ))
          )}
        </ScrollArea>
      </Card>

      <div className="flex justify-end">
        <Button variant="outline" onClick={onClose}>
          关闭
        </Button>
      </div>
    </div>
  )
}

export default function TaskBoardPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [logDialogOpen, setLogDialogOpen] = useState(false)

  const { updateCeleryTaskState } = useTaskStore()
  const { addLog, getLogs } = useExecutionLogStore()

  // Mock initial tasks
  useEffect(() => {
    async function fetchTasks() {
      try {
        const mockTasks: Task[] = [
          {
            id: '1',
            project_id: '1',
            title: '设计登录界面原型',
            description: '完成登录注册页面的 UI 设计',
            status: 'completed',
            assignee: '张三',
            priority: 'high',
            created_at: '2024-01-15T08:00:00Z',
            updated_at: '2024-01-20T10:00:00Z',
            completed_at: '2024-01-20T10:00:00Z',
          },
          {
            id: '2',
            project_id: '1',
            title: '实现用户登录 API',
            description: '对接后端登录接口',
            status: 'running',
            assignee: '李四',
            priority: 'high',
            created_at: '2024-01-20T08:00:00Z',
            updated_at: '2024-03-18T10:00:00Z',
            started_at: '2024-03-15T08:00:00Z',
          },
          {
            id: '3',
            project_id: '1',
            title: '商品列表页面开发',
            description: '完成商品展示列表页面',
            status: 'pending',
            assignee: '王五',
            priority: 'medium',
            created_at: '2024-02-01T08:00:00Z',
            updated_at: '2024-02-01T08:00:00Z',
          },
          {
            id: '4',
            project_id: '2',
            title: '社交 Feed 流开发',
            description: '实现朋友圈动态展示',
            status: 'running',
            assignee: '赵六',
            priority: 'high',
            created_at: '2024-02-05T08:00:00Z',
            updated_at: '2024-03-17T14:00:00Z',
            started_at: '2024-03-10T08:00:00Z',
          },
          {
            id: '5',
            project_id: '2',
            title: '聊天功能开发',
            description: '实现即时通讯功能',
            status: 'pending',
            assignee: '钱七',
            priority: 'high',
            created_at: '2024-02-10T08:00:00Z',
            updated_at: '2024-02-10T08:00:00Z',
          },
          {
            id: '6',
            project_id: '3',
            title: '数据库优化',
            description: '优化查询性能',
            status: 'failed',
            assignee: '孙八',
            priority: 'medium',
            created_at: '2024-02-15T08:00:00Z',
            updated_at: '2024-03-15T16:00:00Z',
          },
        ]
        setTasks(mockTasks)
      } finally {
        setLoading(false)
      }
    }
    fetchTasks()
  }, [])

  // WebSocket real-time updates
  useEffect(() => {
    const client = getWebSocketClient()

    const handleMessage = (message: WebSocketMessage) => {
      const type = message.type

      if (type === 'celery_task_update' || type === 'task_progress') {
        const taskId = message.task_id
        if (!taskId) return

        const taskData = message.data

        if (taskData) {
          setTasks((prev) =>
            prev.map((t) => (t.id === taskId ? { ...t, ...taskData } : t))
          )
        }

        // Update Celery task state
        updateCeleryTaskState(taskId, {
          id: taskId,
          state: (message.state as CeleryTaskState['state']) || 'PENDING',
          progress: message.progress || 0,
          result: message.result || null,
          error: message.error || null,
        })

        // Add log entry
        if (message.state) {
          addLog(taskId, {
            level: message.state === 'FAILURE' ? 'error' : 'info',
            message: `Task state changed to ${message.state}`,
          })
        }
      }
    }

    client.onMessage(handleMessage)

    // Connect if not connected
    if (!client.isConnected) {
      client.connect().catch(console.error)
    }

    return () => {
      // Note: We can't easily unsubscribe without storing the handler reference
    }
  }, [updateCeleryTaskState, addLog])

  const handleViewLogs = (task: Task) => {
    setSelectedTask(task)
    setLogDialogOpen(true)
  }

  const handleExecute = async (task: Task) => {
    // Update task status to running
    setTasks((prev) =>
      prev.map((t) =>
        t.id === task.id
          ? { ...t, status: 'running' as const, started_at: new Date().toISOString() }
          : t
      )
    )

    // Add initial log
    addLog(task.id, {
      level: 'info',
      message: 'Task execution started',
    })

    // In production, this would call the API to start the Celery task
    try {
      const response = await fetch(`/api/v1/tasks/${task.id}/execute`, {
        method: 'POST',
      })

      if (!response.ok) throw new Error('Failed to start task')
    } catch (error) {
      addLog(task.id, {
        level: 'error',
        message: `Failed to start task: ${error instanceof Error ? error.message : 'Unknown error'}`,
      })
      setTasks((prev) =>
        prev.map((t) =>
          t.id === task.id ? { ...t, status: 'failed' as const } : t
        )
      )
    }
  }

  const getTasksByStatus = useCallback(
    (status: TaskStatus) => tasks.filter((t) => t.status === status),
    [tasks]
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">任务看板</h1>
          <p className="text-muted-foreground mt-1">实时任务执行状态</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            刷新
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            新建任务
          </Button>
        </div>
      </div>

      {/* Kanban Board */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          {columns.map((column) => (
            <div key={column.status} className="flex flex-col">
              {/* Column Header */}
              <div
                className={`${column.color} rounded-t-lg p-3 flex items-center justify-between`}
              >
                <div className="flex items-center gap-2">
                  <column.icon className="h-4 w-4" />
                  <span className="font-medium">{column.label}</span>
                </div>
                <Badge variant="secondary" className="ml-2">
                  {getTasksByStatus(column.status).length}
                </Badge>
              </div>

              {/* Column Content */}
              <div className="flex-1 bg-gray-50 rounded-b-lg p-3 min-h-[400px]">
                <ScrollArea className="h-[500px]">
                  {getTasksByStatus(column.status).map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onViewLogs={handleViewLogs}
                      onExecute={handleExecute}
                    />
                  ))}
                  {getTasksByStatus(column.status).length === 0 && (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                      暂无任务
                    </div>
                  )}
                </ScrollArea>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Log Dialog */}
      <Dialog open={logDialogOpen} onOpenChange={setLogDialogOpen}>
        <DialogContent className="max-w-2xl">
          {selectedTask && (
            <ExecutionLogViewer
              task={selectedTask}
              logs={getLogs(selectedTask.id)}
              onClose={() => setLogDialogOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
