import { useEffect, useState } from 'react'
import {
  CheckCircle2,
  Circle,
  Loader2,
  Clock,
  TrendingUp,
} from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface TaskStep {
  id: string
  title: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: number
  estimatedTime?: number // in seconds
  actualTime?: number // in seconds
  message?: string
}

interface TaskProgressProps {
  steps: TaskStep[]
  currentStep?: string
  totalProgress?: number
  showTimeline?: boolean
  compact?: boolean
}

const statusIcons: Record<string, React.ElementType> = {
  pending: Circle,
  running: Loader2,
  completed: CheckCircle2,
  failed: Circle,
}

const statusColors: Record<string, string> = {
  pending: 'text-gray-400',
  running: 'text-blue-500',
  completed: 'text-green-500',
  failed: 'text-red-500',
}

const stepColors: Record<string, string> = {
  pending: 'bg-gray-200',
  running: 'bg-blue-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
}

export function TaskProgress({
  steps,
  currentStep,
  totalProgress,
  showTimeline = true,
  compact = false,
}: TaskProgressProps) {
  const completedSteps = steps.filter((s) => s.status === 'completed').length
  const failedSteps = steps.filter((s) => s.status === 'failed').length
  const runningStep = steps.find((s) => s.status === 'running')

  const overallProgress = totalProgress !== undefined
    ? totalProgress
    : steps.length > 0
    ? Math.round(((completedSteps + (runningStep?.progress || 0) / 100) / steps.length) * 100)
    : 0

  if (compact) {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">总进度</span>
          <span className="font-medium">{overallProgress}%</span>
        </div>
        <Progress value={overallProgress} className="h-2" />
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>{completedSteps}/{steps.length} 步骤完成</span>
          {failedSteps > 0 && (
            <Badge variant="destructive" className="text-xs">{failedSteps} 失败</Badge>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            总体进度
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-3xl font-bold">{overallProgress}%</span>
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>{completedSteps} 完成</span>
                {failedSteps > 0 && (
                  <>
                    <Circle className="h-4 w-4 text-red-500 ml-2" />
                    <span>{failedSteps} 失败</span>
                  </>
                )}
              </div>
            </div>
            <div className="text-sm text-muted-foreground">
              {steps.length - completedSteps - failedSteps} 待执行
            </div>
          </div>
          <Progress value={overallProgress} className="h-3" />
        </CardContent>
      </Card>

      {/* Step Timeline */}
      {showTimeline && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">执行步骤</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {steps.map((step, index) => {
                const Icon = statusIcons[step.status]
                const isLast = index === steps.length - 1

                return (
                  <div key={step.id} className="flex gap-4">
                    {/* Timeline */}
                    <div className="flex flex-col items-center">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          stepColors[step.status]
                        } ${step.status === 'running' ? 'animate-pulse' : ''}`}
                      >
                        <Icon
                          className={`h-4 w-4 text-white ${step.status === 'running' ? 'animate-spin' : ''}`}
                        />
                      </div>
                      {!isLast && (
                        <div
                          className={`w-0.5 h-12 ${
                            steps[index + 1]?.status === 'completed'
                              ? 'bg-green-500'
                              : steps[index + 1]?.status === 'failed'
                              ? 'bg-red-500'
                              : 'bg-gray-200'
                          }`}
                        />
                      )}
                    </div>

                    {/* Step Content */}
                    <div className="flex-1 pb-8">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium">{step.title}</h4>
                          {step.message && (
                            <p className="text-sm text-muted-foreground mt-1">{step.message}</p>
                          )}
                        </div>
                        {step.estimatedTime && (
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {formatDuration(step.actualTime || 0)} / {formatDuration(step.estimatedTime)}
                          </div>
                        )}
                      </div>

                      {/* Step Progress */}
                      {step.status === 'running' && step.progress !== undefined && (
                        <div className="mt-2">
                          <Progress value={step.progress} className="h-1" />
                        </div>
                      )}

                      {/* Status Badge */}
                      <Badge
                        variant="secondary"
                        className={`mt-2 ${statusColors[step.status]}`}
                      >
                        {step.status === 'pending' && '待开始'}
                        {step.status === 'running' && `进行中 ${step.progress || 0}%`}
                        {step.status === 'completed' && '已完成'}
                        {step.status === 'failed' && '失败'}
                      </Badge>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
}

// Compact progress bar component
export function ProgressBar({
  value,
  max = 100,
  size = 'default',
  showLabel = false,
  variant = 'default',
}: {
  value: number
  max?: number
  size?: 'sm' | 'default' | 'lg'
  showLabel?: boolean
  variant?: 'default' | 'success' | 'warning' | 'danger'
}) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  const heightClass = {
    sm: 'h-1',
    default: 'h-2',
    lg: 'h-3',
  }[size]

  const colorClass = {
    default: 'bg-primary',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500',
  }[variant]

  return (
    <div className="space-y-1">
      {showLabel && (
        <div className="flex justify-between text-sm">
          <span>进度</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={`w-full bg-muted rounded-full overflow-hidden ${heightClass}`}>
        <div
          className={`${heightClass} ${colorClass} rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
