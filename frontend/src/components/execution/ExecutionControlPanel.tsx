import { useState, useEffect } from 'react'
import {
  Play,
  Pause,
  RotateCcw,
  Square,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Clock,
  RefreshCw,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import type { Task } from '@/types'
import { useTaskStore } from '@/stores/taskStore'
import { getWebSocketClient, type WebSocketMessage } from '@/lib/websocket'

type ExecutionStatus = 'idle' | 'starting' | 'running' | 'paused' | 'completing' | 'completed' | 'failed' | 'terminated'

interface ExecutionControlPanelProps {
  task: Task
  onStatusChange?: (status: ExecutionStatus) => void
  onStart?: () => Promise<void>
  onPause?: () => Promise<void>
  onResume?: () => Promise<void>
  onTerminate?: () => Promise<void>
  onRestart?: () => Promise<void>
}

const statusConfig: Record<ExecutionStatus, {
  label: string
  color: string
  bgColor: string
  icon: React.ElementType
  description: string
}> = {
  idle: {
    label: '待启动',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    icon: Clock,
    description: '任务等待启动',
  },
  starting: {
    label: '启动中',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    icon: Loader2,
    description: '正在初始化执行环境',
  },
  running: {
    label: '执行中',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    icon: Play,
    description: '任务正在执行中',
  },
  paused: {
    label: '已暂停',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    icon: Pause,
    description: '任务已暂停',
  },
  completing: {
    label: '完成中',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    icon: Loader2,
    description: '正在清理和保存结果',
  },
  completed: {
    label: '已完成',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    icon: CheckCircle2,
    description: '任务执行成功',
  },
  failed: {
    label: '执行失败',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    icon: AlertCircle,
    description: '任务执行失败',
  },
  terminated: {
    label: '已终止',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    icon: Square,
    description: '任务已被手动终止',
  },
}

export function ExecutionControlPanel({
  task,
  onStatusChange,
  onStart,
  onPause,
  onResume,
  onTerminate,
  onRestart,
}: ExecutionControlPanelProps) {
  const [status, setStatus] = useState<ExecutionStatus>(
    task.status === 'running' ? 'running' :
    task.status === 'completed' ? 'completed' :
    task.status === 'failed' ? 'failed' : 'idle'
  )
  const [progress, setProgress] = useState(0)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [isLoading, setIsLoading] = useState(false)

  const { celeryTaskStates } = useTaskStore()
  const celeryState = celeryTaskStates[task.id]

  // Sync status with task
  useEffect(() => {
    if (task.status === 'running' && status !== 'running') {
      setStatus('running')
    } else if (task.status === 'completed' && status !== 'completed') {
      setStatus('completed')
    } else if (task.status === 'failed' && status !== 'failed') {
      setStatus('failed')
    }
  }, [task.status])

  // WebSocket updates
  useEffect(() => {
    const client = getWebSocketClient()

    const handleMessage = (message: WebSocketMessage) => {
      if (message.type === 'task_progress' && message.task_id === task.id) {
        setProgress(message.progress || 0)
      }
      if (message.type === 'celery_task_update' && message.task_id === task.id) {
        const state = message.state
        if (state === 'STARTED' || state === 'PENDING') {
          setStatus('running')
        } else if (state === 'SUCCESS') {
          setStatus('completed')
          setProgress(100)
        } else if (state === 'FAILURE') {
          setStatus('failed')
        }
      }
    }

    client.onMessage(handleMessage)

    if (!client.isConnected) {
      client.connect().catch(console.error)
    }

    return () => {}
  }, [task.id])

  // Timer for elapsed time
  useEffect(() => {
    if (status !== 'running' && status !== 'paused') return

    const interval = setInterval(() => {
      setElapsedTime((t) => t + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [status])

  // Sync with celery state
  useEffect(() => {
    if (celeryState) {
      setProgress(celeryState.progress)
    }
  }, [celeryState])

  const handleStart = async () => {
    setIsLoading(true)
    setStatus('starting')
    try {
      await onStart?.()
      setStatus('running')
      onStatusChange?.('running')
    } catch {
      setStatus('failed')
      onStatusChange?.('failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePause = async () => {
    setIsLoading(true)
    try {
      await onPause?.()
      setStatus('paused')
      onStatusChange?.('paused')
    } catch {
      // Handle error
    } finally {
      setIsLoading(false)
    }
  }

  const handleResume = async () => {
    setIsLoading(true)
    try {
      await onResume?.()
      setStatus('running')
      onStatusChange?.('running')
    } catch {
      // Handle error
    } finally {
      setIsLoading(false)
    }
  }

  const handleTerminate = async () => {
    if (!confirm('确定要终止任务吗？这将立即停止任务执行。')) return

    setIsLoading(true)
    try {
      await onTerminate?.()
      setStatus('terminated')
      onStatusChange?.('terminated')
    } catch {
      // Handle error
    } finally {
      setIsLoading(false)
    }
  }

  const handleRestart = async () => {
    setIsLoading(true)
    setProgress(0)
    setElapsedTime(0)
    try {
      await onRestart?.()
      setStatus('starting')
      setTimeout(() => setStatus('running'), 1000)
    } catch {
      setStatus('failed')
    } finally {
      setIsLoading(false)
    }
  }

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  const currentConfig = statusConfig[status]
  const StatusIcon = currentConfig.icon

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${currentConfig.bgColor}`}>
              <StatusIcon className={`h-5 w-5 ${currentConfig.color} ${status === 'starting' || status === 'completing' ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <CardTitle>{task.title}</CardTitle>
              <CardDescription>{currentConfig.description}</CardDescription>
            </div>
          </div>
          <Badge className={currentConfig.bgColor} variant="secondary">
            <span className={currentConfig.color}>{currentConfig.label}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Section */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">执行进度</span>
            <span className="font-medium">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Time Info */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">已用时间</span>
            <span className="font-medium ml-auto">{formatTime(elapsedTime)}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">预估剩余</span>
            <span className="font-medium ml-auto">
              {formatTime(Math.round(elapsedTime * (100 - progress) / Math.max(progress, 1)))}
            </span>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-center gap-3">
          {status === 'idle' || status === 'terminated' ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button size="lg" onClick={handleStart} disabled={isLoading}>
                  <Play className="h-5 w-5 mr-2" />
                  开始执行
                </Button>
              </TooltipTrigger>
              <TooltipContent>启动任务执行</TooltipContent>
            </Tooltip>
          ) : status === 'running' ? (
            <>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="lg" onClick={handlePause} disabled={isLoading}>
                    <Pause className="h-5 w-5 mr-2" />
                    暂停
                  </Button>
                </TooltipTrigger>
                <TooltipContent>暂停任务执行</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="destructive" size="lg" onClick={handleTerminate} disabled={isLoading}>
                    <Square className="h-5 w-5 mr-2" />
                    终止
                  </Button>
                </TooltipTrigger>
                <TooltipContent>立即终止任务</TooltipContent>
              </Tooltip>
            </>
          ) : status === 'paused' ? (
            <>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button size="lg" onClick={handleResume} disabled={isLoading}>
                    <Play className="h-5 w-5 mr-2" />
                    继续
                  </Button>
                </TooltipTrigger>
                <TooltipContent>恢复任务执行</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="destructive" size="lg" onClick={handleTerminate} disabled={isLoading}>
                    <Square className="h-5 w-5 mr-2" />
                    终止
                  </Button>
                </TooltipTrigger>
                <TooltipContent>立即终止任务</TooltipContent>
              </Tooltip>
            </>
          ) : status === 'completed' || status === 'failed' ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button size="lg" onClick={handleRestart} disabled={isLoading}>
                  <RotateCcw className="h-5 w-5 mr-2" />
                  重新执行
                </Button>
              </TooltipTrigger>
              <TooltipContent>重新开始任务</TooltipContent>
            </Tooltip>
          ) : null}

          {isLoading && (
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          )}
        </div>

        {/* Error Display */}
        {celeryState?.error && (
          <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
            <AlertCircle className="h-4 w-4 inline mr-2" />
            {celeryState.error}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
