import { useEffect, useState } from 'react'
import { Play, Square, RefreshCw, ChevronRight, Clock, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import type { Task, ExecutionStatus } from '@/types'

interface TaskExecutionPanelProps {
  tasks: Task[]
  projectId: string
  onExecute: (taskIds: string[]) => void
  onRefresh: () => void
}

const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-700',
  running: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

export function TaskExecutionPanel({
  tasks,
  projectId,
  onExecute,
  onRefresh,
}: TaskExecutionPanelProps) {
  const [selectedTasks, setSelectedTasks] = useState<Set<string>>(new Set())
  const [executingTasks, setExecutingTasks] = useState<Map<string, ExecutionStatus>>(new Map())

  // 模拟实时更新
  useEffect(() => {
    const interval = setInterval(() => {
      // 实际应该从 API 获取
    }, 2000)
    return () => clearInterval(interval)
  }, [projectId])

  const toggleTask = (taskId: string) => {
    const newSelected = new Set(selectedTasks)
    if (newSelected.has(taskId)) {
      newSelected.delete(taskId)
    } else {
      newSelected.add(taskId)
    }
    setSelectedTasks(newSelected)
  }

  const handleExecute = () => {
    if (selectedTasks.size > 0) {
      onExecute(Array.from(selectedTasks))
    }
  }

  // 计算总 token 消耗
  const totalTokens = tasks.reduce(
    (acc, task) => {
      if (task.token_usage) {
        acc.input += task.token_usage.input || 0
        acc.output += task.token_usage.output || 0
      }
      return acc
    },
    { input: 0, output: 0 }
  )
  totalTokens.total = totalTokens.input + totalTokens.output

  // 统计状态
  const statusCounts = tasks.reduce(
    (acc, task) => {
      acc[task.status] = (acc[task.status] || 0) + 1
      return acc
    },
    {} as Record<string, number>
  )

  return (
    <div className="space-y-4">
      {/* Token 消耗统计 */}
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Token 消耗统计
          </CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-muted-foreground">输入</p>
              <p className="text-lg font-semibold">{totalTokens.input.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">输出</p>
              <p className="text-lg font-semibold">{totalTokens.output.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">总计</p>
              <p className="text-lg font-semibold">{totalTokens.total.toLocaleString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 任务状态统计 */}
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Clock className="h-4 w-4" />
            任务执行状态
          </CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <div className="flex gap-4">
            <Badge variant="outline" className="bg-gray-50">
              待开始: {statusCounts.pending || 0}
            </Badge>
            <Badge variant="outline" className="bg-blue-50">
              进行中: {statusCounts.running || 0}
            </Badge>
            <Badge variant="outline" className="bg-green-50">
              已完成: {statusCounts.completed || 0}
            </Badge>
            <Badge variant="outline" className="bg-red-50">
              失败: {statusCounts.failed || 0}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* 任务列表 */}
      <Card>
        <CardHeader className="py-3 flex flex-row items-center justify-between">
          <CardTitle className="text-sm">
            任务列表 ({tasks.length})
          </CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onRefresh}>
              <RefreshCw className="h-3 w-3 mr-1" />
              刷新
            </Button>
            <Button
              size="sm"
              onClick={handleExecute}
              disabled={selectedTasks.size === 0}
            >
              <Play className="h-3 w-3 mr-1" />
              执行选中 ({selectedTasks.size})
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[400px]">
            <div className="divide-y">
              {tasks.map((task) => (
                <TaskExecutionRow
                  key={task.id}
                  task={task}
                  selected={selectedTasks.has(task.id)}
                  executing={executingTasks.get(task.id)}
                  onSelect={() => toggleTask(task.id)}
                />
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}

interface TaskExecutionRowProps {
  task: Task
  selected: boolean
  executing?: ExecutionStatus
  onSelect: () => void
}

function TaskExecutionRow({ task, selected, executing, onSelect }: TaskExecutionRowProps) {
  const statusInfo = {
    pending: { label: '待开始', color: 'bg-gray-100 text-gray-700' },
    running: { label: '进行中', color: 'bg-blue-100 text-blue-700' },
    completed: { label: '已完成', color: 'bg-green-100 text-green-700' },
    failed: { label: '失败', color: 'bg-red-100 text-red-700' },
  }

  const info = statusInfo[task.status] || statusInfo.pending
  const progress = executing?.progress || (task.status === 'completed' ? 100 : task.progress || 0)

  return (
    <div
      className={cn(
        'flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-accent',
        selected && 'bg-blue-50'
      )}
      onClick={onSelect}
    >
      {/* Checkbox */}
      <div
        className={cn(
          'w-4 h-4 rounded border-2 flex items-center justify-center',
          selected ? 'bg-blue-500 border-blue-500' : 'border-gray-300'
        )}
      >
        {selected && <div className="w-2 h-2 bg-white rounded-sm" />}
      </div>

      {/* Status Indicator */}
      <div className={cn('w-2 h-2 rounded-full', task.status === 'completed' ? 'bg-green-500' : task.status === 'running' ? 'bg-blue-500 animate-pulse' : task.status === 'failed' ? 'bg-red-500' : 'bg-gray-300')} />

      {/* Task Info */}
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{task.title}</p>
        {task.description && (
          <p className="text-xs text-muted-foreground truncate">{task.description}</p>
        )}
      </div>

      {/* Progress Bar (for running tasks) */}
      {task.status === 'running' && (
        <div className="w-20">
          <Progress value={progress} className="h-1" />
        </div>
      )}

      {/* Status Badge */}
      <Badge className={cn('text-xs', info.color)} variant="secondary">
        {info.label}
      </Badge>

      {/* Token Usage */}
      {task.token_usage && (
        <div className="text-xs text-muted-foreground w-16 text-right">
          {task.token_usage.total.toLocaleString()}
        </div>
      )}

      <ChevronRight className="h-4 w-4 text-muted-foreground" />
    </div>
  )
}
