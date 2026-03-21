import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus,
  Search,
  CheckCircle2,
  Clock,
  Circle,
  AlertCircle,
  MoreHorizontal,
} from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { getTasks } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { Task } from '@/types'

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
  {
    id: '7',
    project_id: '3',
    title: 'API 文档编写',
    description: '编写 RESTful API 文档',
    status: 'completed',
    assignee: '周九',
    priority: 'low',
    created_at: '2024-02-20T08:00:00Z',
    updated_at: '2024-03-01T10:00:00Z',
    completed_at: '2024-03-01T10:00:00Z',
  },
]

const statusConfig: Record<
  Task['status'],
  { label: string; color: string; icon: React.ElementType }
> = {
  pending: { label: '待开始', color: 'bg-gray-100 text-gray-700', icon: Circle },
  running: { label: '进行中', color: 'bg-blue-100 text-blue-700', icon: Clock },
  completed: {
    label: '已完成',
    color: 'bg-green-100 text-green-700',
    icon: CheckCircle2,
  },
  failed: { label: '失败', color: 'bg-red-100 text-red-700', icon: AlertCircle },
}

const priorityColors: Record<Task['priority'], string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-red-100 text-red-700',
}

function TaskRow({ task }: { task: Task }) {
  const status = statusConfig[task.status]
  const StatusIcon = status.icon

  return (
    <TableRow>
      <TableCell>
        <div className="flex items-center gap-3">
          <StatusIcon className="h-4 w-4 text-muted-foreground" />
          <div>
            <Link
              to={`projects/${task.project_id}`}
              className="font-medium hover:underline"
            >
              {task.title}
            </Link>
            <p className="text-sm text-muted-foreground line-clamp-1">
              {task.description}
            </p>
          </div>
        </div>
      </TableCell>
      <TableCell>
        <Badge className={status.color} variant="secondary">
          {status.label}
        </Badge>
      </TableCell>
      <TableCell>
        <Badge className={priorityColors[task.priority]} variant="secondary">
          {task.priority === 'low' ? '低' : task.priority === 'medium' ? '中' : '高'}
        </Badge>
      </TableCell>
      <TableCell className="text-muted-foreground">{task.assignee}</TableCell>
      <TableCell className="text-muted-foreground">
        {formatDate(task.updated_at)}
      </TableCell>
      <TableCell>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>查看详情</DropdownMenuItem>
            <DropdownMenuItem>编辑</DropdownMenuItem>
            <DropdownMenuItem>标记完成</DropdownMenuItem>
            <DropdownMenuItem className="text-destructive">删除</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </TableCell>
    </TableRow>
  )
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>('all')
  const [priority, setPriority] = useState<string>('all')

  useEffect(() => {
    async function fetchTasks() {
      try {
        const data = await getTasks()
        if (data.items.length > 0) {
          setTasks(data.items)
        }
      } catch {
        // Use mock data on error
      } finally {
        setLoading(false)
      }
    }
    fetchTasks()
  }, [])

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      task.title.toLowerCase().includes(search.toLowerCase()) ||
      task.description.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = status === 'all' || task.status === status
    const matchesPriority = priority === 'all' || task.priority === priority
    return matchesSearch && matchesStatus && matchesPriority
  })

  const taskStats = {
    total: tasks.length,
    pending: tasks.filter((t) => t.status === 'pending').length,
    running: tasks.filter((t) => t.status === 'running').length,
    completed: tasks.filter((t) => t.status === 'completed').length,
    failed: tasks.filter((t) => t.status === 'failed').length,
  }

  const statusTabs = [
    { value: 'all', label: '全部', count: taskStats.total },
    { value: 'pending', label: '待开始', count: taskStats.pending },
    { value: 'running', label: '进行中', count: taskStats.running },
    { value: 'completed', label: '已完成', count: taskStats.completed },
    { value: 'failed', label: '失败', count: taskStats.failed },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tasks</h1>
          <p className="text-muted-foreground mt-1">任务管理与执行状态</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          新建任务
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              总任务数
            </CardTitle>
            <Circle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              进行中
            </CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.running}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              已完成
            </CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.completed}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              失败
            </CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{taskStats.failed}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索任务..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="状态" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="pending">待开始</SelectItem>
                <SelectItem value="running">进行中</SelectItem>
                <SelectItem value="completed">已完成</SelectItem>
                <SelectItem value="failed">失败</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priority} onValueChange={setPriority}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="优先级" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部优先级</SelectItem>
                <SelectItem value="high">高</SelectItem>
                <SelectItem value="medium">中</SelectItem>
                <SelectItem value="low">低</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tasks Table */}
      <Card>
        <CardHeader>
          <CardTitle>任务列表</CardTitle>
          <CardDescription>共 {filteredTasks.length} 个任务</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all" className="space-y-4">
            <TabsList>
              {statusTabs.map((tab) => (
                <TabsTrigger key={tab.value} value={tab.value}>
                  {tab.label} ({tab.count})
                </TabsTrigger>
              ))}
            </TabsList>

            {statusTabs.map((tab) => (
              <TabsContent key={tab.value} value={tab.value}>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[400px]">任务</TableHead>
                      <TableHead>状态</TableHead>
                      <TableHead>优先级</TableHead>
                      <TableHead>负责人</TableHead>
                      <TableHead>更新时间</TableHead>
                      <TableHead className="w-[50px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {loading ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-8">
                          加载中...
                        </TableCell>
                      </TableRow>
                    ) : filteredTasks.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-8">
                          暂无任务
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredTasks
                        .filter(
                          (t) => tab.value === 'all' || t.status === tab.value
                        )
                        .map((task) => (
                          <TaskRow key={task.id} task={task} />
                        ))
                    )}
                  </TableBody>
                </Table>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
