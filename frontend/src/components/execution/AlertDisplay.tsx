import { useState, useEffect } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  Info,
  CheckCircle2,
  Bell,
  BellOff,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Clock,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'

type AlertSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info'
type AlertType = 'error' | 'warning' | 'info' | 'success'

interface Alert {
  id: string
  type: AlertType
  severity: AlertSeverity
  title: string
  message: string
  timestamp: string
  taskId?: string
  taskName?: string
  acknowledged: boolean
  resolved: boolean
  metadata?: Record<string, string>
}

interface AlertDisplayProps {
  alerts?: Alert[]
  onAcknowledge?: (alertId: string) => void
  onResolve?: (alertId: string) => void
  onDismiss?: (alertId: string) => void
  autoRefresh?: boolean
  maxVisible?: number
}

const severityConfig: Record<AlertSeverity, { label: string; color: string; bgColor: string }> = {
  critical: { label: '严重', color: 'text-red-600', bgColor: 'bg-red-100 border-red-200' },
  high: { label: '高', color: 'text-orange-600', bgColor: 'bg-orange-100 border-orange-200' },
  medium: { label: '中', color: 'text-yellow-600', bgColor: 'bg-yellow-100 border-yellow-200' },
  low: { label: '低', color: 'text-blue-600', bgColor: 'bg-blue-100 border-blue-200' },
  info: { label: '提示', color: 'text-gray-600', bgColor: 'bg-gray-100 border-gray-200' },
}

const typeIcons: Record<AlertType, React.ElementType> = {
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
  success: CheckCircle2,
}

const typeColors: Record<AlertType, string> = {
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
  success: 'text-green-500',
}

function AlertCard({
  alert,
  onAcknowledge,
  onResolve,
  onDismiss,
  expanded,
  onToggle,
}: {
  alert: Alert
  onAcknowledge?: (id: string) => void
  onResolve?: (id: string) => void
  onDismiss?: (id: string) => void
  expanded: boolean
  onToggle: () => void
}) {
  const Icon = typeIcons[alert.type]
  const severity = severityConfig[alert.severity]
  const colorClass = typeColors[alert.type]

  return (
    <div
      className={`border rounded-lg transition-colors ${severity.bgColor} ${
        alert.acknowledged ? 'opacity-70' : ''
      }`}
    >
      <div
        className="flex items-start gap-3 p-4 cursor-pointer"
        onClick={onToggle}
      >
        <Icon className={`h-5 w-5 ${colorClass} shrink-0 mt-0.5`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-medium text-sm">{alert.title}</h4>
            <Badge variant="outline" className={`text-xs ${severity.color}`}>
              {severity.label}
            </Badge>
            {alert.acknowledged && (
              <Badge variant="secondary" className="text-xs">已确认</Badge>
            )}
            {alert.resolved && (
              <Badge variant="secondary" className="text-xs text-green-600">已解决</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2">{alert.message}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(alert.timestamp).toLocaleString()}
            </span>
            {alert.taskName && (
              <span className="truncate">任务: {alert.taskName}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation()
              onToggle()
            }}
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="px-4 pb-4">
          {alert.metadata && Object.keys(alert.metadata).length > 0 && (
            <div className="mb-3 p-3 bg-white/50 rounded-lg">
              <h5 className="text-xs font-medium text-muted-foreground mb-2">详细信息</h5>
              <div className="space-y-1 text-xs font-mono">
                {Object.entries(alert.metadata).map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <span className="text-muted-foreground">{key}:</span>
                    <span className="truncate">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2">
            {!alert.acknowledged && (
              <Button
                size="sm"
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation()
                  onAcknowledge?.(alert.id)
                }}
              >
                确认
              </Button>
            )}
            {!alert.resolved && (
              <Button
                size="sm"
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation()
                  onResolve?.(alert.id)
                }}
              >
                标记已解决
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation()
                onDismiss?.(alert.id)
              }}
            >
              忽略
            </Button>
            {alert.taskId && (
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation()
                  // Navigate to task
                }}
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                查看任务
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Mock alerts for demonstration
const mockAlerts: Alert[] = [
  {
    id: '1',
    type: 'error',
    severity: 'critical',
    title: '编译失败',
    message: 'Task "实现用户登录API" 执行失败。错误: npm ERR! code ENOWORKSPACES',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    taskId: '2',
    taskName: '实现用户登录API',
    acknowledged: false,
    resolved: false,
    metadata: {
      error: 'ENOWORKSPACES',
      stage: 'install',
      exitCode: '1',
    },
  },
  {
    id: '2',
    type: 'warning',
    severity: 'high',
    title: '无输出超时',
    message: 'Task "数据库优化" 超过5分钟无输出，可能已卡死',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    taskId: '6',
    taskName: '数据库优化',
    acknowledged: true,
    resolved: false,
  },
  {
    id: '3',
    type: 'warning',
    severity: 'medium',
    title: 'API 限流',
    message: '检测到 API 请求频率限制，将自动降速处理',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    acknowledged: true,
    resolved: true,
  },
  {
    id: '4',
    type: 'info',
    severity: 'low',
    title: '任务完成',
    message: 'Task "设计登录界面原型" 已成功完成',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    taskId: '1',
    taskName: '设计登录界面原型',
    acknowledged: false,
    resolved: true,
  },
]

export function AlertDisplay({
  alerts = mockAlerts,
  onAcknowledge,
  onResolve,
  onDismiss,
  autoRefresh = true,
  maxVisible = 10,
}: AlertDisplayProps) {
  const [localAlerts, setLocalAlerts] = useState(alerts)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [activeTab, setActiveTab] = useState('all')

  // Sync with props
  useEffect(() => {
    setLocalAlerts(alerts)
  }, [alerts])

  // Auto-refresh simulation
  useEffect(() => {
    if (!autoRefresh) return
    const interval = setInterval(() => {
      // In real implementation, this would fetch new alerts from server
    }, 30000)
    return () => clearInterval(interval)
  }, [autoRefresh])

  const handleAcknowledge = (id: string) => {
    setLocalAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a))
    )
    onAcknowledge?.(id)
  }

  const handleResolve = (id: string) => {
    setLocalAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, resolved: true } : a))
    )
    onResolve?.(id)
  }

  const handleDismiss = (id: string) => {
    setLocalAlerts((prev) => prev.filter((a) => a.id !== id))
    onDismiss?.(id)
  }

  const toggleExpanded = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const filteredAlerts = localAlerts.filter((alert) => {
    if (activeTab === 'active') return !alert.resolved
    if (activeTab === 'acknowledged') return alert.acknowledged && !alert.resolved
    if (activeTab === 'resolved') return alert.resolved
    return true
  })

  const unacknowledgedCount = localAlerts.filter((a) => !a.acknowledged && !a.resolved).length
  const criticalCount = localAlerts.filter((a) => a.severity === 'critical' && !a.resolved).length

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-destructive/10">
              <Bell className="h-5 w-5 text-destructive" />
            </div>
            <div>
              <CardTitle>告警中心</CardTitle>
              <CardDescription>
                {unacknowledgedCount > 0 && (
                  <span className="text-destructive font-medium">
                    {unacknowledgedCount} 条未确认
                  </span>
                )}
                {criticalCount > 0 && (
                  <span className="text-destructive ml-2">
                    {criticalCount} 严重
                  </span>
                )}
              </CardDescription>
            </div>
          </div>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSoundEnabled((s) => !s)}
              >
                {soundEnabled ? (
                  <Bell className="h-4 w-4" />
                ) : (
                  <BellOff className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {soundEnabled ? '关闭声音' : '开启声音'}
            </TooltipContent>
          </Tooltip>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
          <TabsList>
            <TabsTrigger value="all">
              全部 ({localAlerts.length})
            </TabsTrigger>
            <TabsTrigger value="active">
              待处理 ({localAlerts.filter((a) => !a.resolved).length})
            </TabsTrigger>
            <TabsTrigger value="acknowledged">
              已确认 ({localAlerts.filter((a) => a.acknowledged && !a.resolved).length})
            </TabsTrigger>
            <TabsTrigger value="resolved">
              已解决 ({localAlerts.filter((a) => a.resolved).length})
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>

      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          <div className="space-y-3 p-4">
            {filteredAlerts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle2 className="h-12 w-12 mx-auto mb-4 text-green-500 opacity-50" />
                <p>暂无告警信息</p>
              </div>
            ) : (
              filteredAlerts.slice(0, maxVisible).map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onAcknowledge={handleAcknowledge}
                  onResolve={handleResolve}
                  onDismiss={handleDismiss}
                  expanded={expandedIds.has(alert.id)}
                  onToggle={() => toggleExpanded(alert.id)}
                />
              ))
            )}

            {filteredAlerts.length > maxVisible && (
              <div className="text-center pt-2">
                <Button variant="link" size="sm">
                  查看全部 {filteredAlerts.length} 条告警
                </Button>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
