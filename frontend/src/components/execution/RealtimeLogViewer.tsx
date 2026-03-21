import { useEffect, useRef, useState } from 'react'
import {
  Terminal,
  Copy,
  Trash2,
  Download,
  Filter,
  Search,
  Maximize2,
  Minimize2,
  Pause,
  Play,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useExecutionLogStore, type ExecutionLog } from '@/stores/taskStore'
import { getWebSocketClient } from '@/lib/websocket'

interface RealtimeLogViewerProps {
  taskId: string
  taskName?: string
  autoScroll?: boolean
  maxLines?: number
  onFullscreenToggle?: (isFullscreen: boolean) => void
}

type LogLevel = 'all' | 'info' | 'warning' | 'error' | 'debug'

const levelColors: Record<string, { text: string; bg: string; label: string }> = {
  info: { text: 'text-blue-400', bg: 'bg-blue-500', label: 'INFO' },
  warning: { text: 'text-yellow-400', bg: 'bg-yellow-500', label: 'WARN' },
  error: { text: 'text-red-400', bg: 'bg-red-500', label: 'ERROR' },
  debug: { text: 'text-gray-400', bg: 'bg-gray-500', label: 'DEBUG' },
}

export function RealtimeLogViewer({
  taskId,
  taskName = '任务日志',
  autoScroll = true,
  maxLines = 1000,
  onFullscreenToggle,
}: RealtimeLogViewerProps) {
  const [logs, setLogs] = useState<ExecutionLog[]>([])
  const [filter] = useState<LogLevel>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [isPaused, setIsPaused] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [visibleLevels, setVisibleLevels] = useState<Record<string, boolean>>({
    info: true,
    warning: true,
    error: true,
    debug: true,
  })

  const scrollRef = useRef<HTMLDivElement>(null)
  const { getLogs, addLog } = useExecutionLogStore()

  // Load initial logs
  useEffect(() => {
    const initialLogs = getLogs(taskId)
    if (initialLogs.length > 0) {
      setLogs(initialLogs)
    }
  }, [taskId, getLogs])

  // WebSocket connection for real-time logs
  useEffect(() => {
    const client = getWebSocketClient()

    const handleMessage = (message: { type: string; task_id?: string; level?: string; message?: string; state?: string }) => {
      if (isPaused) return

      if (message.type === 'execution_log' && message.task_id === taskId) {
        const newLog: ExecutionLog = {
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          task_id: taskId,
          timestamp: new Date().toISOString(),
          level: (message.level as 'info' | 'warning' | 'error') || 'info',
          message: message.message || '',
        }
        addLog(taskId, { level: newLog.level, message: newLog.message })
        setLogs((prev) => [...prev.slice(-maxLines), newLog])
      }

      if (message.type === 'celery_task_update' && message.task_id === taskId) {
        // Add state change as info log
        const stateLog: ExecutionLog = {
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          task_id: taskId,
          timestamp: new Date().toISOString(),
          level: 'info',
          message: `[STATE] Task state changed to ${message.state}`,
        }
        addLog(taskId, { level: 'info', message: stateLog.message })
        setLogs((prev) => [...prev.slice(-maxLines), stateLog])
      }
    }

    client.onMessage(handleMessage as Parameters<typeof client.onMessage>[0])

    if (!client.isConnected) {
      client.connect().catch(console.error)
    }

    return () => {}
  }, [taskId, isPaused, addLog, maxLines])

  // Auto-scroll
  useEffect(() => {
    if (autoScroll && !isPaused && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs, autoScroll, isPaused])

  const filteredLogs = logs.filter((log) => {
    if (!visibleLevels[log.level]) return false
    if (filter !== 'all' && log.level !== filter) return false
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  const handleCopyLogs = () => {
    const text = filteredLogs
      .map((log) => `[${new Date(log.timestamp).toLocaleTimeString()}] [${log.level.toUpperCase()}] ${log.message}`)
      .join('\n')
    navigator.clipboard.writeText(text)
  }

  const handleDownloadLogs = () => {
    const text = filteredLogs
      .map((log) => `[${new Date(log.timestamp).toISOString()}] [${log.level.toUpperCase()}] ${log.message}`)
      .join('\n')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `task-${taskId}-logs-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleClearLogs = () => {
    setLogs([])
  }

  const handleLevelToggle = (level: string) => {
    setVisibleLevels((prev) => ({ ...prev, [level]: !prev[level] }))
  }

  const toggleFullscreen = () => {
    setIsFullscreen((prev) => !prev)
    onFullscreenToggle?.(!isFullscreen)
  }

  const errorCount = logs.filter((l) => l.level === 'error').length
  const warningCount = logs.filter((l) => l.level === 'warning').length

  return (
    <Card className={isFullscreen ? 'fixed inset-4 z-50 shadow-2xl' : ''}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-black/10">
              <Terminal className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base">实时日志</CardTitle>
              <CardDescription>{taskName}</CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Stats */}
            {errorCount > 0 && (
              <Badge variant="destructive" className="text-xs">
                {errorCount} errors
              </Badge>
            )}
            {warningCount > 0 && (
              <Badge variant="secondary" className="text-xs text-yellow-600">
                {warningCount} warnings
              </Badge>
            )}

            {/* Level Filter */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-1" />
                  筛选
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuCheckboxItem
                  checked={visibleLevels.info}
                  onCheckedChange={() => handleLevelToggle('info')}
                >
                  INFO
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={visibleLevels.warning}
                  onCheckedChange={() => handleLevelToggle('warning')}
                >
                  WARNING
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={visibleLevels.error}
                  onCheckedChange={() => handleLevelToggle('error')}
                >
                  ERROR
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={visibleLevels.debug}
                  onCheckedChange={() => handleLevelToggle('debug')}
                >
                  DEBUG
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Actions */}
            <Button variant="ghost" size="icon" onClick={toggleFullscreen}>
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-2 mt-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索日志内容..."
              className="pl-9 h-9"
            />
          </div>
          <Button
            variant={isPaused ? 'default' : 'outline'}
            size="sm"
            onClick={() => setIsPaused((p) => !p)}
          >
            {isPaused ? <Play className="h-4 w-4 mr-1" /> : <Pause className="h-4 w-4 mr-1" />}
            {isPaused ? '继续' : '暂停'}
          </Button>
          <Button variant="outline" size="sm" onClick={handleCopyLogs}>
            <Copy className="h-4 w-4 mr-1" />
            复制
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownloadLogs}>
            <Download className="h-4 w-4 mr-1" />
            下载
          </Button>
          <Button variant="outline" size="sm" onClick={handleClearLogs}>
            <Trash2 className="h-4 w-4 mr-1" />
            清空
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <ScrollArea
          ref={scrollRef}
          className={`${isFullscreen ? 'h-[calc(100vh-200px)]' : 'h-[400px]'} bg-black rounded-b-lg`}
        >
          <div className="p-4 font-mono text-xs space-y-1">
            {filteredLogs.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                {logs.length === 0 ? '等待日志输出...' : '没有匹配的日志'}
              </div>
            ) : (
              filteredLogs.map((log) => {
                const config = levelColors[log.level] || levelColors.info
                return (
                  <div key={log.id} className="flex gap-3 hover:bg-white/5 py-1">
                    <span className="text-gray-500 shrink-0">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`${config.text} shrink-0 w-16`}>
                      [{config.label}]
                    </span>
                    <span className="text-gray-300 break-all">{log.message}</span>
                  </div>
                )
              })
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
