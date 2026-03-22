import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createProject } from '@/lib/api'
import { Plus, Search, MoreHorizontal, FolderKanban } from 'lucide-react'
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { getProjects } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { Project } from '@/types'

const mockProjects: Project[] = [
  {
    id: '1',
    name: '抖音Android',
    description: '抖音Android客户端开发',
    platform: 'android',
    spec_framework: 'openspec',
    local_path: '/workspace/douyin-android',
    status: 'in_progress',
    created_at: '2024-01-15T08:00:00Z',
    updated_at: '2024-03-18T10:30:00Z',
    member_count: 5,
    task_count: 45,
    progress: 75,
  },
  {
    id: '2',
    name: '头条iOS',
    description: '头条iOS客户端开发',
    platform: 'ios',
    spec_framework: 'openspec',
    local_path: '/workspace/toutiao-ios',
    status: 'in_progress',
    created_at: '2024-02-01T08:00:00Z',
    updated_at: '2024-03-17T14:20:00Z',
    member_count: 8,
    task_count: 32,
    progress: 45,
  },
  {
    id: '3',
    name: '企业管理系统',
    description: '企业内部管理系统',
    platform: 'ios',
    spec_framework: 'speckit',
    status: 'in_progress',
    created_at: '2024-02-01T08:00:00Z',
    updated_at: '2024-03-17T14:20:00Z',
    member_count: 8,
    task_count: 32,
    progress: 45,
  },
  {
    id: '3',
    name: '企业管理系统',
    description: '企业内部管理系统',
    platform: 'ios',
    spec_framework: 'openspec',
    status: 'completed',
    created_at: '2023-11-10T08:00:00Z',
    updated_at: '2024-03-15T16:00:00Z',
    member_count: 12,
    task_count: 89,
    progress: 100,
  },
  {
    id: '4',
    name: '在线教育平台',
    description: 'K12 在线教育应用',
    platform: 'cross',
    spec_framework: 'superpowers',
    status: 'planning',
    created_at: '2024-03-01T08:00:00Z',
    updated_at: '2024-03-16T09:00:00Z',
    member_count: 3,
    task_count: 15,
    progress: 30,
  },
]

const statusColors: Record<Project['status'], string> = {
  planning: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-green-100 text-green-700',
  suspended: 'bg-gray-100 text-gray-700',
}

const statusLabels: Record<Project['status'], string> = {
  planning: '规划中',
  in_progress: '进行中',
  completed: '已完成',
  suspended: '已暂停',
}

function CreateProjectDialog() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [platform, setPlatform] = useState('android')
  const [localPath, setLocalPath] = useState('')
  const [specFramework, setSpecFramework] = useState('openspec')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const project = await createProject({
        name,
        description,
        platform: platform as 'android' | 'ios' | 'harmony' | 'cross',
        local_path: localPath || undefined,
        spec_framework: specFramework as 'openspec' | 'speckit' | 'superpowers',
      })
      setOpen(false)
      setName('')
      setDescription('')
      setLocalPath('')
      navigate(`/projects/${project.id}`)
    } catch (error) {
      console.error('Failed to create project:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          新建项目
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>创建新项目</DialogTitle>
            <DialogDescription>
              填写项目基本信息，创建新项目
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">项目名称</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例如: 抖音Android、头条iOS"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">项目描述</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="描述项目目标与范围"
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="platform">平台</Label>
                <Select value={platform} onValueChange={setPlatform}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择平台" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="android">Android</SelectItem>
                    <SelectItem value="ios">iOS</SelectItem>
                    <SelectItem value="harmony">HarmonyOS</SelectItem>
                    <SelectItem value="cross">跨平台</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="specFramework">规范框架</Label>
                <Select value={specFramework} onValueChange={setSpecFramework}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择规范框架" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="openspec">OpenSpec</SelectItem>
                    <SelectItem value="speckit">SpecKit</SelectItem>
                    <SelectItem value="superpowers">SuperPowers</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="localPath">本地开发目录</Label>
              <Input
                id="localPath"
                value={localPath}
                onChange={(e) => setLocalPath(e.target.value)}
                placeholder="/path/to/your/project"
              />
              <p className="text-xs text-muted-foreground">
                Claude Code 将自动在此目录下创建和修改代码
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={loading}>
              {loading ? '创建中...' : '创建项目'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

function ProjectRow({ project }: { project: Project }) {
  const frameworkLabels: Record<string, string> = {
    openspec: 'OpenSpec',
    speckit: 'SpecKit',
    superpowers: 'SuperPowers',
  }

  return (
    <TableRow>
      <TableCell>
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <FolderKanban className="h-5 w-5 text-primary" />
          </div>
          <div>
            <Link
              to={`/projects/${project.id}`}
              className="font-medium hover:underline"
            >
              {project.name}
            </Link>
            <p className="text-sm text-muted-foreground line-clamp-1">
              {project.description}
            </p>
            {project.local_path && (
              <p className="text-xs text-muted-foreground font-mono">
                {project.local_path}
              </p>
            )}
          </div>
        </div>
      </TableCell>
      <TableCell>
        <Badge variant="outline">{project.platform}</Badge>
        {project.spec_framework && (
          <Badge variant="secondary" className="ml-1">
            {frameworkLabels[project.spec_framework] || project.spec_framework}
          </Badge>
        )}
      </TableCell>
      <TableCell>
        <Badge className={statusColors[project.status]} variant="secondary">
          {statusLabels[project.status]}
        </Badge>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full"
              style={{ width: `${project.progress}%` }}
            />
          </div>
          <span className="text-sm">{project.progress}%</span>
        </div>
      </TableCell>
      <TableCell className="text-muted-foreground">
        {project.member_count} 人
      </TableCell>
      <TableCell className="text-muted-foreground">
        {project.task_count} 任务
      </TableCell>
      <TableCell className="text-muted-foreground">
        {formatDate(project.updated_at)}
      </TableCell>
      <TableCell>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link to={`projects/${project.id}`}>查看详情</Link>
            </DropdownMenuItem>
            <DropdownMenuItem>编辑项目</DropdownMenuItem>
            <DropdownMenuItem className="text-destructive">
              删除项目
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </TableCell>
    </TableRow>
  )
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>(mockProjects)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>('all')

  useEffect(() => {
    async function fetchProjects() {
      try {
        const data = await getProjects()
        if (data.items.length > 0) {
          setProjects(data.items)
        }
      } catch {
        // Use mock data on error
      } finally {
        setLoading(false)
      }
    }
    fetchProjects()
  }, [])

  const filteredProjects = projects.filter((project) => {
    const matchesSearch = project.name
      .toLowerCase()
      .includes(search.toLowerCase())
    const matchesStatus = status === 'all' || project.status === status
    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground mt-1">管理所有项目</p>
        </div>
        <CreateProjectDialog />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索项目..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="状态筛选" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="planning">规划中</SelectItem>
                <SelectItem value="in_progress">进行中</SelectItem>
                <SelectItem value="completed">已完成</SelectItem>
                <SelectItem value="suspended">已暂停</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Projects Table */}
      <Card>
        <CardHeader>
          <CardTitle>项目列表</CardTitle>
          <CardDescription>
            共 {filteredProjects.length} 个项目
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[300px]">项目</TableHead>
                <TableHead>平台/规范</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>进度</TableHead>
                <TableHead>成员</TableHead>
                <TableHead>任务</TableHead>
                <TableHead>更新时间</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    加载中...
                  </TableCell>
                </TableRow>
              ) : filteredProjects.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    暂无项目
                  </TableCell>
                </TableRow>
              ) : (
                filteredProjects.map((project) => (
                  <ProjectRow key={project.id} project={project} />
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
