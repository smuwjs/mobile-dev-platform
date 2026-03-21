import {
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ChevronRight,
  GitBranch,
  Layers,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { DecompositionResult } from '@/stores/requirementStore'

interface DecompositionResultViewProps {
  result: DecompositionResult
  onCreateTasks?: () => void
  onEdit?: () => void
}

const complexityLabels: Record<number, { label: string; color: string }> = {
  1: { label: '简单', color: 'bg-green-100 text-green-700' },
  2: { label: '中等', color: 'bg-yellow-100 text-yellow-700' },
  3: { label: '复杂', color: 'bg-orange-100 text-orange-700' },
  4: { label: '困难', color: 'bg-red-100 text-red-700' },
}

export function DecompositionResultView({ result, onCreateTasks, onEdit }: DecompositionResultViewProps) {
  const complexity = complexityLabels[result.complexity] || complexityLabels[1]

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card className="border-primary/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-yellow-500" />
            AI 分解结果
          </CardTitle>
          <CardDescription>基于需求分析自动生成的任务分解</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">复杂度</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-2xl font-bold">{result.complexity}</span>
                <Badge className={complexity.color} variant="secondary">
                  {complexity.label}
                </Badge>
              </div>
            </div>
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">预估工时</span>
              <span className="text-2xl font-bold">{result.estimated_total_hours}h</span>
              <span className="text-xs text-muted-foreground">
                ≈ {(result.estimated_total_hours / 8).toFixed(1)} 人天
              </span>
            </div>
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">子需求</span>
              <span className="text-2xl font-bold">{result.sub_requirements.length}</span>
              <span className="text-xs text-muted-foreground">功能模块</span>
            </div>
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">生成任务</span>
              <span className="text-2xl font-bold">{result.tasks.length}</span>
              <span className="text-xs text-muted-foreground">可执行任务</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Validation */}
      {result.validation.status !== 'valid' && (
        <Card className="border-yellow-200 bg-yellow-50/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-800">
              <AlertTriangle className="h-5 w-5" />
              验证结果
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {result.validation.conflicts.length > 0 && (
              <div>
                <h4 className="font-medium text-red-700 mb-2 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  冲突 ({result.validation.conflicts.length})
                </h4>
                <ul className="space-y-2">
                  {result.validation.conflicts.map((c, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-red-600">
                      <span className="font-medium">{c.type}:</span>
                      <span>{c.message}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.validation.warnings.length > 0 && (
              <div>
                <h4 className="font-medium text-yellow-700 mb-2 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  警告 ({result.validation.warnings.length})
                </h4>
                <ul className="space-y-1">
                  {result.validation.warnings.map((w, i) => (
                    <li key={i} className="text-sm text-yellow-600 flex items-start gap-2">
                      <span>•</span>
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.validation.suggestions.length > 0 && (
              <div>
                <h4 className="font-medium text-blue-700 mb-2 flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  优化建议
                </h4>
                <ul className="space-y-1">
                  {result.validation.suggestions.map((s, i) => (
                    <li key={i} className="text-sm text-blue-600 flex items-start gap-2">
                      <span>•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Sub-requirements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="h-5 w-5" />
            功能模块分解
          </CardTitle>
          <CardDescription>共 {result.sub_requirements.length} 个子需求</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {result.sub_requirements.map((subReq) => (
              <div
                key={subReq.id}
                className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/30 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium">{subReq.title}</h4>
                    <Badge variant="outline" className="text-xs">
                      优先级 {subReq.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{subReq.description}</p>
                  <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      预估: {subReq.estimated_hours}h
                    </span>
                    <span className="flex items-center gap-1">
                      <Layers className="h-3 w-3" />
                      复杂度: {subReq.complexity}
                    </span>
                    {subReq.dependencies.length > 0 && (
                      <span className="flex items-center gap-1">
                        <GitBranch className="h-3 w-3" />
                        依赖: {subReq.dependencies.length} 项
                      </span>
                    )}
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Generated Tasks */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                生成的任务清单
              </CardTitle>
              <CardDescription>共 {result.tasks.length} 个任务，建议执行顺序</CardDescription>
            </div>
            {onEdit && (
              <Button variant="outline" size="sm" onClick={onEdit}>
                编辑任务
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {result.tasks.map((task, index) => (
                <div key={task.id} className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-medium shrink-0">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium truncate">{task.title}</p>
                      <Badge variant="outline" className="text-xs shrink-0">
                        {task.task_type}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground truncate">{task.description}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant="secondary" className="text-xs">
                      <Clock className="h-3 w-3 mr-1" />
                      {task.estimated_hours}h
                    </Badge>
                    <Badge
                      variant="outline"
                      className={`text-xs ${
                        task.priority >= 3
                          ? 'border-red-200 text-red-600'
                          : task.priority >= 2
                          ? 'border-yellow-200 text-yellow-600'
                          : 'border-green-200 text-green-600'
                      }`}
                    >
                      P{task.priority}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          {onCreateTasks && (
            <div className="flex justify-end mt-4">
              <Button onClick={onCreateTasks} size="lg">
                <CheckCircle2 className="h-4 w-4 mr-2" />
                创建所有任务
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
