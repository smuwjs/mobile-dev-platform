import { useState } from 'react'
import {
  GripVertical,
  Plus,
  Trash2,
  Clock,
  Edit2,
  Check,
  X,
  ChevronUp,
  ChevronDown,
  AlertCircle,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useDecompositionStore, type DecompositionResult } from '@/stores/requirementStore'

interface TaskListEditorProps {
  result: DecompositionResult
  onSave: (tasks: DecompositionResult['tasks']) => void
  onCancel: () => void
}

interface EditableTask {
  id: string
  title: string
  description: string
  requirement_id: string
  project_id: string
  priority: number
  task_type: string
  estimated_hours: number
  sort_order: number
  dependencies: string[]
}

const taskTypes = [
  { value: 'frontend', label: '前端开发' },
  { value: 'backend', label: '后端开发' },
  { value: 'design', label: 'UI/UX设计' },
  { value: 'testing', label: '测试' },
  { value: 'devops', label: '部署/DevOps' },
  { value: 'api', label: 'API集成' },
  { value: 'database', label: '数据库' },
  { value: 'security', label: '安全' },
  { value: 'performance', label: '性能优化' },
  { value: 'documentation', label: '文档' },
  { value: 'other', label: '其他' },
]

export function TaskListEditor({ result, onSave, onCancel }: TaskListEditorProps) {
  const [tasks, setTasks] = useState<EditableTask[]>(
    result.tasks.map((t) => ({ ...t }))
  )
  const [editingId, setEditingId] = useState<string | null>(null)
  const [draggedId, setDraggedId] = useState<string | null>(null)

  const handleAddTask = () => {
    const newTask: EditableTask = {
      id: `new-${Date.now()}`,
      title: '',
      description: '',
      requirement_id: result.requirement_id,
      project_id: result.tasks[0]?.project_id || '',
      priority: 2,
      task_type: 'frontend',
      estimated_hours: 1,
      sort_order: tasks.length + 1,
      dependencies: [],
    }
    setTasks([...tasks, newTask])
    setEditingId(newTask.id)
  }

  const handleDeleteTask = (id: string) => {
    setTasks(tasks.filter((t) => t.id !== id))
  }

  const handleUpdateTask = (id: string, updates: Partial<EditableTask>) => {
    setTasks(tasks.map((t) => (t.id === id ? { ...t, ...updates } : t)))
  }

  const handleMoveUp = (index: number) => {
    if (index === 0) return
    const newTasks = [...tasks]
    ;[newTasks[index - 1], newTasks[index]] = [newTasks[index], newTasks[index - 1]]
    newTasks.forEach((t, i) => (t.sort_order = i + 1))
    setTasks(newTasks)
  }

  const handleMoveDown = (index: number) => {
    if (index === tasks.length - 1) return
    const newTasks = [...tasks]
    ;[newTasks[index], newTasks[index + 1]] = [newTasks[index + 1], newTasks[index]]
    newTasks.forEach((t, i) => (t.sort_order = i + 1))
    setTasks(newTasks)
  }

  const handleDragStart = (id: string) => {
    setDraggedId(id)
  }

  const handleDragOver = (e: React.DragEvent, targetId: string) => {
    e.preventDefault()
    if (!draggedId || draggedId === targetId) return

    const draggedIndex = tasks.findIndex((t) => t.id === draggedId)
    const targetIndex = tasks.findIndex((t) => t.id === targetId)
    if (draggedIndex === targetIndex) return

    const newTasks = [...tasks]
    const [draggedTask] = newTasks.splice(draggedIndex, 1)
    newTasks.splice(targetIndex, 0, draggedTask)
    newTasks.forEach((t, i) => (t.sort_order = i + 1))
    setTasks(newTasks)
  }

  const handleDragEnd = () => {
    setDraggedId(null)
  }

  const handleSave = () => {
    const validTasks = tasks.filter((t) => t.title.trim())
    if (validTasks.length === 0) return
    onSave(validTasks as DecompositionResult['tasks'])
  }

  const totalHours = tasks.reduce((sum, t) => sum + t.estimated_hours, 0)

  const renderTaskContent = (task: EditableTask) => {
    if (editingId === task.id) {
      return (
        <div className="space-y-2">
          <Input
            value={task.title}
            onChange={(e) => handleUpdateTask(task.id, { title: e.target.value })}
            placeholder="任务标题"
            className="font-medium"
          />
          <Textarea
            value={task.description}
            onChange={(e) => handleUpdateTask(task.id, { description: e.target.value })}
            placeholder="任务描述"
            rows={2}
            className="text-sm"
          />
          <div className="flex gap-2 flex-wrap">
            <Select
              value={task.task_type}
              onValueChange={(v) => handleUpdateTask(task.id, { task_type: v })}
            >
              <SelectTrigger className="w-[140px] h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {taskTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={String(task.priority)}
              onValueChange={(v) => handleUpdateTask(task.id, { priority: Number(v) })}
            >
              <SelectTrigger className="w-[100px] h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">优先级 低</SelectItem>
                <SelectItem value="2">优先级 中</SelectItem>
                <SelectItem value="3">优先级 高</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <Input
                type="number"
                value={task.estimated_hours}
                onChange={(e) =>
                  handleUpdateTask(task.id, {
                    estimated_hours: Math.max(0.5, parseFloat(e.target.value) || 1),
                  })
                }
                className="w-[80px] h-8"
                min={0.5}
                step={0.5}
              />
              <span className="text-sm text-muted-foreground">h</span>
            </div>
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="font-medium">{task.title || '(未填写标题)'}</span>
          <Badge variant="outline" className="text-xs">
            {taskTypes.find((t) => t.value === task.task_type)?.label || task.task_type}
          </Badge>
          <Badge
            variant={
              task.priority >= 3
                ? 'destructive'
                : task.priority >= 2
                ? 'secondary'
                : 'outline'
            }
            className="text-xs"
          >
            P{task.priority}
          </Badge>
          <Badge variant="secondary" className="text-xs">
            {task.estimated_hours}h
          </Badge>
        </div>
        {task.description && (
          <p className="text-sm text-muted-foreground line-clamp-1">
            {task.description}
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">编辑任务清单</h2>
          <p className="text-sm text-muted-foreground mt-1">
            共 {tasks.length} 个任务，总计 {totalHours}h
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel}>
            取消
          </Button>
          <Button onClick={handleSave}>
            <Check className="h-4 w-4 mr-2" />
            保存修改
          </Button>
        </div>
      </div>

      {/* Task List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>任务列表</CardTitle>
              <CardDescription>拖拽排序，点击编辑</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleAddTask}>
              <Plus className="h-4 w-4 mr-2" />
              添加任务
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[500px]">
            <div className="space-y-2">
              {tasks.map((task, index) => (
                <div
                  key={task.id}
                  className={`flex items-start gap-3 p-3 border rounded-lg transition-colors ${
                    draggedId === task.id ? 'bg-muted' : 'hover:bg-muted/30'
                  }`}
                  draggable
                  onDragStart={() => handleDragStart(task.id)}
                  onDragOver={(e) => handleDragOver(e, task.id)}
                  onDragEnd={handleDragEnd}
                >
                  {/* Drag Handle */}
                  <div className="flex items-center gap-1 pt-1 cursor-move text-muted-foreground">
                    <GripVertical className="h-4 w-4" />
                    <ChevronUp
                      className="h-3 w-3 hover:text-foreground cursor-pointer"
                      onClick={() => handleMoveUp(index)}
                    />
                    <ChevronDown
                      className="h-3 w-3 hover:text-foreground cursor-pointer"
                      onClick={() => handleMoveDown(index)}
                    />
                  </div>

                  {/* Task Number */}
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-medium shrink-0 mt-1">
                    {index + 1}
                  </div>

                  {/* Task Content */}
                  <div className="flex-1 min-w-0">
                    {renderTaskContent(task)}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1 shrink-0">
                    {editingId === task.id ? (
                      <>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => setEditingId(null)}
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive"
                          onClick={() => handleDeleteTask(task.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => setEditingId(task.id)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive"
                          onClick={() => handleDeleteTask(task.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))}

              {tasks.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>暂无任务</p>
                  <p className="text-sm">点击"添加任务"创建新任务</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}
