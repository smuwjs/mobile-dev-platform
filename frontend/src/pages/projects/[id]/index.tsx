import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Users,
  ListTodo,
  Calendar,
  Plus,
  MoreHorizontal,
  CheckCircle2,
  Circle,
  Clock,
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
import { Progress } from '@/components/ui/progress'
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
import { getProject, getRequirements } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { Project, Requirement, Task } from '@/types'

const mockProject: Project = {
  id: '1',
  name: '电商 App v2.0',
  description: '全新设计的电商移动应用，包含商品展示、购物车、订单管理、支付等功能模块。目标是为用户提供流畅的移动购物体验。',
  status: 'in_progress',
  created_at: '2024-01-15T08:00:00Z',
  updated_at: '2024-03-18T10:30:00Z',
  member_count: 5,
  task_count: 45,
  progress: 75,
}

const mockRequirements: Requirement[] = [
  {
    id: '1',
    project_id: '1',
    title: '用户登录注册',
    description: '支持手机号验证码登录，第三方登录（微信、苹果）',
    status: 'completed',
    priority: 'high',
    created_at: '2024-01-15T08:00:00Z',
    updated_at: '2024-02-20T10:00:00Z',
  },
  {
    id: '2',
    project_id: '1',
    title: '商品展示模块',
    description: '首页推荐、商品分类、商品详情、商品搜索',
    status: 'active',
    priority: 'high',
    created_at: '2024-01-20T08:00:00Z',
    updated_at: '2024-03-10T14:00:00Z',
  },
  {
    id: '3',
    project_id: '1',
    title: '购物车功能',
    description: '添加购物车、数量修改、删除、结算',
    status: 'active',
    priority: 'high',
    created_at: '2024-02-01T08:00:00Z',
    updated_at: '2024-03-15T16:00:00Z',
  },
  {
    id: '4',
    project_id: '1',
    title: '订单管理',
    description: '订单列表、订单详情、订单状态跟踪、取消订单',
    status: 'draft',
    priority: 'medium',
    created_at: '2024-02-15T08:00:00Z',
    updated_at: '2024-02-15T08:00:00Z',
  },
  {
    id: '5',
    project_id: '1',
    title: '支付模块',
    description: '支付宝、微信支付集成',
    status: 'draft',
    priority: 'high',
    created_at: '2024-02-20T08:00:00Z',
    updated_at: '2024-02-20T08:00:00Z',
  },
]

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
]

const statusColors: Record<Task['status'], string> = {
  pending: 'bg-gray-100 text-gray-700',
  running: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

const statusLabels: Record<Task['status'], string> = {
  pending: '待开始',
  running: '进行中',
  completed: '已完成',
  failed: '失败',
}

const priorityColors: Record<Task['priority'], string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-red-100 text-red-700',
}

const reqStatusColors: Record<Requirement['status'], string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  archived: 'bg-gray-100 text-gray-500',
}

function RequirementRow({ requirement }: { requirement: Requirement }) {
  return (
    <TableRow>
      <TableCell>
        <div>
          <p className="font-medium">{requirement.title}</p>
          <p className="text-sm text-muted-foreground line-clamp-1">
            {requirement.description}
          </p>
        </div>
      </TableCell>
      <TableCell>
        <Badge className={reqStatusColors[requirement.status]} variant="secondary">
          {requirement.status === 'draft' ? '草稿' :
           requirement.status === 'active' ? '进行中' :
           requirement.status === 'completed' ? '已完成' : '已归档'}
        </Badge>
      </TableCell>
      <TableCell>
        <Badge className={priorityColors[requirement.priority]} variant="secondary">
          {requirement.priority === 'low' ? '低' :
           requirement.priority === 'medium' ? '中' : '高'}
        </Badge>
      </TableCell>
      <TableCell className="text-muted-foreground">
        {formatDate(requirement.updated_at)}
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
            <DropdownMenuItem>删除</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </TableCell>
    </TableRow>
  )
}

function TaskRow({ task }: { task: Task }) {
  const StatusIcon = {
    pending: Circle,
    running: Clock,
    completed: CheckCircle2,
    failed: Circle,
  }[task.status]

  return (
    <TableRow>
      <TableCell>
        <div className="flex items-center gap-3">
          <StatusIcon className="h-4 w-4 text-muted-foreground" />
          <div>
            <p className="font-medium">{task.title}</p>
            <p className="text-sm text-muted-foreground line-clamp-1">
              {task.description}
            </p>
          </div>
        </div>
      </TableCell>
      <TableCell>
        <Badge className={statusColors[task.status]} variant="secondary">
          {statusLabels[task.status]}
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
    </TableRow>
  )
}

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [requirements, setRequirements] = useState<Requirement[]>(mockRequirements)
  const [tasks] = useState<Task[]>(mockTasks)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      if (!id) return
      try {
        const data = await getProject(id)
        setProject(data)
        const reqData = await getRequirements(id)
        if (reqData.items.length > 0) {
          setRequirements(reqData.items)
        }
      } catch {
        // Use mock data on error
        setProject(mockProject)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">加载中...</p>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-muted-foreground">项目不存在</p>
        <Button variant="outline" asChild>
          <Link to="projects">返回项目列表</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link to="projects">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <p className="text-muted-foreground mt-1">{project.description}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">编辑项目</Button>
          <Button>新建任务</Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              项目状态
            </CardTitle>
            <Badge
              className={
                project.status === 'in_progress'
                  ? 'bg-yellow-100 text-yellow-700'
                  : project.status === 'completed'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }
            >
              {project.status === 'planning'
                ? '规划中'
                : project.status === 'in_progress'
                ? '进行中'
                : project.status === 'completed'
                ? '已完成'
                : '已暂停'}
            </Badge>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              成员数量
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{project.member_count}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              任务数量
            </CardTitle>
            <ListTodo className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{project.task_count}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              更新时间
            </CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatDate(project.updated_at)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Progress */}
      <Card>
        <CardHeader>
          <CardTitle>项目进度</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Progress value={project.progress} className="h-3 flex-1" />
            <span className="text-lg font-bold">{project.progress}%</span>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="requirements" className="space-y-4">
        <TabsList>
          <TabsTrigger value="requirements">
            需求列表 ({requirements.length})
          </TabsTrigger>
          <TabsTrigger value="tasks">任务列表 ({tasks.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="requirements">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>需求列表</CardTitle>
                <CardDescription>项目需求与功能点</CardDescription>
              </div>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                新增需求
              </Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[400px]">需求</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>优先级</TableHead>
                    <TableHead>更新时间</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {requirements.map((req) => (
                    <RequirementRow key={req.id} requirement={req} />
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>任务列表</CardTitle>
                <CardDescription>开发任务与进度</CardDescription>
              </div>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                新建任务
              </Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[400px]">任务</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>优先级</TableHead>
                    <TableHead>负责人</TableHead>
                    <TableHead>更新时间</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tasks.map((task) => (
                    <TaskRow key={task.id} task={task} />
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
