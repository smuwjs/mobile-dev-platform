import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Settings,
  Play,
  FileText,
  TreePine,
  Zap,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  getProject,
  getRequirements,
  getTasks,
  specExecute,
  specGenerateReport,
  getSpecFrameworks,
} from '@/lib/api'
import { formatDate } from '@/lib/utils'
import { RequirementTree } from '@/components/tree'
import { TaskExecutionPanel, ReportViewer } from '@/components/execution'
import type { Project, Requirement, Task, SpecFramework, ProjectReport } from '@/types'

// Mock data for demo
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
    id: '2-1',
    project_id: '1',
    parent_id: '2',
    title: '首页推荐',
    description: '轮播图、精选商品',
    status: 'active',
    priority: 'high',
    created_at: '2024-01-20T08:00:00Z',
    updated_at: '2024-03-10T14:00:00Z',
  },
  {
    id: '2-2',
    project_id: '1',
    parent_id: '2',
    title: '商品分类',
    description: '分类列表、筛选',
    status: 'draft',
    priority: 'medium',
    created_at: '2024-01-20T08:00:00Z',
    updated_at: '2024-03-10T14:00:00Z',
  },
]

const mockTasks: Task[] = [
  {
    id: '1',
    project_id: '1',
    title: '设计登录界面原型',
    status: 'completed',
    priority: 'high',
    created_at: '2024-01-15T08:00:00Z',
    updated_at: '2024-01-20T10:00:00Z',
    token_usage: { input: 5000, output: 2000, total: 7000 },
  },
  {
    id: '2',
    project_id: '1',
    title: '实现用户登录 API',
    status: 'running',
    priority: 'high',
    progress: 60,
    created_at: '2024-01-20T08:00:00Z',
    updated_at: '2024-03-18T10:00:00Z',
    token_usage: { input: 3000, output: 1500, total: 4500 },
  },
  {
    id: '3',
    project_id: '1',
    title: '商品列表页面开发',
    status: 'pending',
    priority: 'medium',
    created_at: '2024-02-01T08:00:00Z',
    updated_at: '2024-02-01T08:00:00Z',
  },
]

const frameworkLabels: Record<string, string> = {
  openspec: 'OpenSpec',
  speckit: 'SpecKit',
  superpowers: 'SuperPowers',
}

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [requirements, setRequirements] = useState<Requirement[]>(mockRequirements)
  const [tasks, setTasks] = useState<Task[]>(mockTasks)
  const [frameworks, setFrameworks] = useState<SpecFramework[]>([])
  const [report, setReport] = useState<ProjectReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)

  useEffect(() => {
    async function fetchData() {
      if (!id) return
      try {
        // Fetch project
        const projectData = await getProject(id)
        setProject(projectData)

        // Fetch requirements
        const reqData = await getRequirements(id)
        if (reqData.items.length > 0) {
          setRequirements(reqData.items)
        }

        // Fetch tasks
        const taskData = await getTasks({ project_id: id })
        if (taskData.items.length > 0) {
          setTasks(taskData.items)
        }

        // Fetch frameworks
        const fwData = await getSpecFrameworks()
        setFrameworks(fwData.frameworks || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleExecuteTasks = async (taskIds: string[]) => {
    if (!id) return
    setExecuting(true)
    try {
      await specExecute({
        task_ids: taskIds,
        project_id: id,
        parallel: true,
      })
      // Refresh tasks
      const taskData = await getTasks({ project_id: id })
      if (taskData.items.length > 0) {
        setTasks(taskData.items)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setExecuting(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!id || requirements.length === 0) return
    setReportLoading(true)
    try {
      const reportData = await specGenerateReport(id, requirements[0].id)
      setReport(reportData)
    } catch (e) {
      console.error(e)
    } finally {
      setReportLoading(false)
    }
  }

  const handleRefresh = async () => {
    if (!id) return
    const taskData = await getTasks({ project_id: id })
    if (taskData.items.length > 0) {
      setTasks(taskData.items)
    }
  }

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
          <Link to="/projects">返回项目列表</Link>
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
            <Link to="/projects">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <p className="text-muted-foreground mt-1">{project.description}</p>
            <div className="flex gap-2 mt-2">
              <Badge variant="outline">{project.platform}</Badge>
              {project.spec_framework && (
                <Badge variant="secondary">
                  {frameworkLabels[project.spec_framework] || project.spec_framework}
                </Badge>
              )}
              {project.local_path && (
                <Badge variant="outline" className="font-mono text-xs">
                  {project.local_path}
                </Badge>
              )}
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            项目配置
          </Button>
          <Button>
            <Play className="h-4 w-4 mr-2" />
            开始执行
          </Button>
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
              需求数量
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{requirements.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              任务数量
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Token 消耗
            </CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.reduce((acc, t) => acc + (t.token_usage?.total || 0), 0).toLocaleString()}
            </div>
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

      {/* Main Content Tabs */}
      <Tabs defaultValue="tree" className="space-y-4">
        <TabsList>
          <TabsTrigger value="tree" className="flex items-center gap-2">
            <TreePine className="h-4 w-4" />
            树状视图
          </TabsTrigger>
          <TabsTrigger value="execution" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            任务执行
          </TabsTrigger>
          <TabsTrigger value="report" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            完成报告
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tree">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>需求树状结构</CardTitle>
                  <CardDescription>
                    项目 → 需求 → 子需求 → 任务 的层级关系
                  </CardDescription>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  新增需求
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <RequirementTree
                requirements={requirements}
                onSelect={(req) => console.log('Select:', req)}
                onExecute={(req) => console.log('Execute:', req)}
                onViewTasks={(req) => console.log('View tasks:', req)}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="execution">
          <TaskExecutionPanel
            tasks={tasks}
            projectId={id || ''}
            onExecute={handleExecuteTasks}
            onRefresh={handleRefresh}
          />
        </TabsContent>

        <TabsContent value="report">
          <ReportViewer
            report={report}
            loading={reportLoading}
            onRegenerate={handleGenerateReport}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Need Plus import
import { Plus } from 'lucide-react'
