import { useState } from 'react'
import { ChevronRight, ChevronDown, Circle, Clock, CheckCircle2, AlertCircle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { Requirement, Task } from '@/types'

interface TreeNodeProps {
  requirement: Requirement
  level?: number
  onSelect?: (requirement: Requirement) => void
  onExecute?: (requirement: Requirement) => void
  onViewTasks?: (requirement: Requirement) => void
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  archived: 'bg-gray-100 text-gray-500',
}

const priorityColors: Record<string, string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-red-100 text-red-700',
}

export function RequirementTreeNode({
  requirement,
  level = 0,
  onSelect,
  onExecute,
  onViewTasks,
}: TreeNodeProps) {
  const [expanded, setExpanded] = useState(level < 2)
  const hasChildren = requirement.children && requirement.children.length > 0
  const hasTasks = requirement.tasks && requirement.tasks.length > 0

  const StatusIcon = {
    draft: Circle,
    active: Clock,
    completed: CheckCircle2,
    archived: AlertCircle,
  }[requirement.status] || Circle

  return (
    <div className="select-none">
      <div
        className={cn(
          'flex items-center gap-2 py-2 px-3 hover:bg-accent rounded-md cursor-pointer',
          level > 0 && 'ml-4'
        )}
        style={{ paddingLeft: `${level * 20 + 12}px` }}
        onClick={() => onSelect?.(requirement)}
      >
        {/* Expand/Collapse Button */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            setExpanded(!expanded)
          }}
          className={cn(
            'p-0.5 hover:bg-accent rounded',
            !hasChildren && 'invisible'
          )}
        >
          {expanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
        </button>

        {/* Status Icon */}
        <StatusIcon
          className={cn(
            'h-4 w-4',
            requirement.status === 'completed' && 'text-green-500',
            requirement.status === 'active' && 'text-blue-500',
            requirement.status === 'draft' && 'text-gray-400'
          )}
        />

        {/* Title */}
        <span className="flex-1 font-medium">{requirement.title}</span>

        {/* Status Badge */}
        <Badge
          className={cn('text-xs', statusColors[requirement.status])}
          variant="secondary"
        >
          {requirement.status === 'draft' && '草稿'}
          {requirement.status === 'active' && '进行中'}
          {requirement.status === 'completed' && '已完成'}
          {requirement.status === 'archived' && '已归档'}
        </Badge>

        {/* Priority Badge */}
        <Badge
          className={cn('text-xs', priorityColors[requirement.priority])}
          variant="secondary"
        >
          {requirement.priority === 'low' ? '低' : requirement.priority === 'medium' ? '中' : '高'}
        </Badge>

        {/* Actions */}
        <div className="flex gap-1">
          {hasTasks && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onViewTasks?.(requirement)
              }}
            >
              任务
            </Button>
          )}
          {requirement.status === 'active' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onExecute?.(requirement)
              }}
            >
              执行
            </Button>
          )}
        </div>
      </div>

      {/* Children */}
      {expanded && hasChildren && (
        <div className="border-l border-dashed ml-6">
          {requirement.children!.map((child) => (
            <RequirementTreeNode
              key={child.id}
              requirement={child}
              level={level + 1}
              onSelect={onSelect}
              onExecute={onExecute}
              onViewTasks={onViewTasks}
            />
          ))}
        </div>
      )}

      {/* Tasks under this requirement */}
      {expanded && hasTasks && requirement.tasks && (
        <div className="ml-8">
          {requirement.tasks.map((task) => (
            <TaskNode key={task.id} task={task} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

interface TaskNodeProps {
  task: Task
  level?: number
}

function TaskNode({ task, level = 0 }: TaskNodeProps) {
  const StatusIcon = {
    pending: Circle,
    running: Clock,
    completed: CheckCircle2,
    failed: AlertCircle,
  }[task.status] || Circle

  return (
    <div
      className="flex items-center gap-2 py-1.5 px-3 hover:bg-accent rounded-md ml-4"
      style={{ paddingLeft: `${level * 20 + 12}px` }}
    >
      <StatusIcon
        className={cn(
          'h-3.5 w-3.5',
          task.status === 'completed' && 'text-green-500',
          task.status === 'running' && 'text-blue-500',
          task.status === 'failed' && 'text-red-500',
          task.status === 'pending' && 'text-gray-400'
        )}
      />
      <span className="text-sm text-muted-foreground">{task.title}</span>
      <Badge className="text-xs" variant="outline">
        {task.status === 'pending' && '待开始'}
        {task.status === 'running' && '进行中'}
        {task.status === 'completed' && '已完成'}
        {task.status === 'failed' && '失败'}
      </Badge>
      {task.token_usage && (
        <span className="text-xs text-muted-foreground">
          {task.token_usage.total} tokens
        </span>
      )}
    </div>
  )
}

interface RequirementTreeProps {
  requirements: Requirement[]
  onSelect?: (requirement: Requirement) => void
  onExecute?: (requirement: Requirement) => void
  onViewTasks?: (requirement: Requirement) => void
}

export function RequirementTree({
  requirements,
  onSelect,
  onExecute,
  onViewTasks,
}: RequirementTreeProps) {
  // Build tree structure
  const rootRequirements = buildTree(requirements)

  if (requirements.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        暂无需求，请先创建需求
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {rootRequirements.map((req) => (
        <RequirementTreeNode
          key={req.id}
          requirement={req}
          onSelect={onSelect}
          onExecute={onExecute}
          onViewTasks={onViewTasks}
        />
      ))}
    </div>
  )
}

// Helper function to build tree from flat list
function buildTree(requirements: Requirement[]): Requirement[] {
  const map = new Map<string, Requirement>()
  const roots: Requirement[] = []

  // First pass: create map
  requirements.forEach((req) => {
    map.set(req.id, { ...req, children: [], tasks: req.tasks || [] })
  })

  // Second pass: build tree
  requirements.forEach((req) => {
    const node = map.get(req.id)!
    if (req.parent_id && map.has(req.parent_id)) {
      map.get(req.parent_id)!.children!.push(node)
    } else {
      roots.push(node)
    }
  })

  return roots
}
