import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  FolderKanban,
  ListTodo,
  CheckCircle2,
  Receipt,
  ArrowUpRight,
  Plus,
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
import { getDashboardStats } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import type { DashboardStats, Activity } from '@/types'

const mockStats: DashboardStats = {
  total_projects: 12,
  active_projects: 8,
  total_tasks: 156,
  completed_tasks: 89,
  total_cost: 258000,
  recent_activities: [],
}

const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'project_created',
    description: '创建了新项目 "电商 App v2.0"',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: '2',
    type: 'task_completed',
    description: '任务 "用户登录模块" 已完成',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    id: '3',
    type: 'cost_added',
    description: '新增成本记录 ¥15,000（服务器费用）',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
  },
  {
    id: '4',
    type: 'member_joined',
    description: '李四加入了 "社交 App" 项目',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
]

function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
}: {
  title: string
  value: string | number
  description: string
  icon: React.ElementType
  trend?: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
        {trend && (
          <div className="flex items-center mt-2 text-xs text-green-600">
            <ArrowUpRight className="h-3 w-3" />
            {trend}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ActivityItem({ activity }: { activity: Activity }) {
  const typeLabels: Record<Activity['type'], { label: string; color: string }> = {
    project_created: { label: '项目', color: 'bg-blue-100 text-blue-700' },
    task_completed: { label: '任务', color: 'bg-green-100 text-green-700' },
    cost_added: { label: '成本', color: 'bg-orange-100 text-orange-700' },
    member_joined: { label: '成员', color: 'bg-purple-100 text-purple-700' },
  }

  const { label, color } = typeLabels[activity.type]

  return (
    <div className="flex items-start gap-3 py-3">
      <Badge className={color} variant="secondary">
        {label}
      </Badge>
      <div className="flex-1 min-w-0">
        <p className="text-sm">{activity.description}</p>
        <p className="text-xs text-muted-foreground mt-1">
          {formatDateTime(activity.timestamp)}
        </p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>(mockStats)
  const [activities] = useState<Activity[]>(mockActivities)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getDashboardStats()
        setStats(data)
      } catch {
        // Use mock data on error
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">项目概览与统计</p>
        </div>
        <Button asChild>
          <Link to="/dev/projects/new">
            <Plus className="h-4 w-4 mr-2" />
            新建项目
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="总项目数"
          value={loading ? '-' : stats.total_projects}
          description="所有创建的项目"
          icon={FolderKanban}
          trend="+2 本月"
        />
        <StatCard
          title="进行中项目"
          value={loading ? '-' : stats.active_projects}
          description="当前活跃的项目"
          icon={FolderKanban}
          trend="+1 本周"
        />
        <StatCard
          title="完成任务"
          value={`${loading ? '-' : stats.completed_tasks}/${loading ? '-' : stats.total_tasks}`}
          description="已完成的任务数"
          icon={CheckCircle2}
        />
        <StatCard
          title="总成本"
          value={loading ? '-' : `¥${(stats.total_cost / 10000).toFixed(1)}万`}
          description="项目总支出"
          icon={Receipt}
        />
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>最近活动</CardTitle>
            <CardDescription>项目动态与更新</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="divide-y">
              {activities.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>快捷操作</CardTitle>
            <CardDescription>常用功能入口</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Button variant="outline" className="justify-start" asChild>
              <Link to="/dev/projects">
                <FolderKanban className="h-4 w-4 mr-2" />
                查看所有项目
              </Link>
            </Button>
            <Button variant="outline" className="justify-start" asChild>
              <Link to="/dev/tasks">
                <ListTodo className="h-4 w-4 mr-2" />
                查看所有任务
              </Link>
            </Button>
            <Button variant="outline" className="justify-start" asChild>
              <Link to="/dev/costs">
                <Receipt className="h-4 w-4 mr-2" />
                成本分析
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Project Progress Overview */}
      <Card>
        <CardHeader>
          <CardTitle>项目进度概览</CardTitle>
          <CardDescription>主要项目的完成情况</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { name: '电商 App v2.0', progress: 75 },
              { name: '社交 App', progress: 45 },
              { name: '企业管理系统', progress: 90 },
              { name: '在线教育平台', progress: 30 },
            ].map((project) => (
              <div key={project.name} className="flex items-center gap-4">
                <div className="w-32 text-sm truncate">{project.name}</div>
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
                <div className="w-12 text-sm text-right">{project.progress}%</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
