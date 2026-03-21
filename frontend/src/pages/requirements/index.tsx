import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus,
  Search,
  MoreHorizontal,
  Sparkles,
  ChevronRight,
  AlertTriangle,
  CheckCircle2,
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
import { Input } from '@/components/ui/input'
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { useDecompositionStore, type DecompositionResult } from '@/stores'
import type { Requirement } from '@/types'
import { formatDate } from '@/lib/utils'

const reqStatusColors: Record<Requirement['status'], string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  archived: 'bg-gray-100 text-gray-500',
}

const statusLabels: Record<Requirement['status'], string> = {
  draft: '草稿',
  active: '进行中',
  completed: '已完成',
  archived: '已归档',
}

const priorityColors: Record<Requirement['priority'], string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-red-100 text-red-700',
}

function RequirementRow({
  requirement,
  onDecompose,
}: {
  requirement: Requirement
  onDecompose: (req: Requirement) => void
}) {
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
          {statusLabels[requirement.status]}
        </Badge>
      </TableCell>
      <TableCell>
        <Badge className={priorityColors[requirement.priority]} variant="secondary">
          {requirement.priority === 'low' ? '低' : requirement.priority === 'medium' ? '中' : '高'}
        </Badge>
      </TableCell>
      <TableCell className="text-muted-foreground">
        {formatDate(requirement.updated_at)}
      </TableCell>
      <TableCell>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => onDecompose(requirement)}>
            <Sparkles className="h-4 w-4 mr-1" />
            AI 分解
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link to={`/dev/requirements/${requirement.id}`}>查看详情</Link>
              </DropdownMenuItem>
              <DropdownMenuItem>编辑</DropdownMenuItem>
              <DropdownMenuItem className="text-destructive">删除</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </TableCell>
    </TableRow>
  )
}

function DecompositionResultView({ result }: { result: DecompositionResult }) {
  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-yellow-500" />
            AI 分解结果
          </CardTitle>
          <CardDescription>
            基于需求分析自动生成的任务分解
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex flex-col">
              <span className="text-sm text-muted-foreground">复杂度</span>
              <span className="text-2xl font-bold">{result.complexity}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm text-muted-foreground">预估工时</span>
              <span className="text-2xl font-bold">{result.estimated_total_hours}h</span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm text-muted-foreground">子需求</span>
              <span className="text-2xl font-bold">{result.sub_requirements.length}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Validation */}
      {result.validation.status !== 'valid' && (
        <Card className="border-yellow-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-700">
              <AlertTriangle className="h-5 w-5" />
              验证结果
            </CardTitle>
          </CardHeader>
          <CardContent>
            {result.validation.conflicts.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-red-700 mb-2">冲突</h4>
                <ul className="space-y-1">
                  {result.validation.conflicts.map((c, i) => (
                    <li key={i} className="text-sm text-red-600">
                      {c.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.validation.warnings.length > 0 && (
              <div>
                <h4 className="font-medium text-yellow-700 mb-2">警告</h4>
                <ul className="space-y-1">
                  {result.validation.warnings.map((w, i) => (
                    <li key={i} className="text-sm text-yellow-600">
                      {w}
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
          <CardTitle>子需求</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {result.sub_requirements.map((subReq) => (
              <div key={subReq.id} className="flex items-start gap-4 p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{subReq.title}</h4>
                    <Badge variant="outline">优先级 {subReq.priority}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{subReq.description}</p>
                  <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                    <span>复杂度: {subReq.complexity}</span>
                    <span>预估: {subReq.estimated_hours}h</span>
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-muted-foreground" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Generated Tasks */}
      <Card>
        <CardHeader>
          <CardTitle>生成的任务</CardTitle>
          <CardDescription>
            共 {result.tasks.length} 个任务，建议执行顺序
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {result.tasks.map((task, index) => (
              <div key={task.id} className="flex items-center gap-4">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-medium">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{task.title}</p>
                  <p className="text-sm text-muted-foreground">{task.description}</p>
                </div>
                <Badge variant="outline">{task.estimated_hours}h</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function RequirementsPage() {
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [decomposeDialogOpen, setDecomposeDialogOpen] = useState(false)
  const [selectedRequirement, setSelectedRequirement] = useState<Requirement | null>(null)
  const [requirementText, setRequirementText] = useState('')
  const [decompositionResult, setDecompositionResult] = useState<DecompositionResult | null>(null)

  const { isDecomposing, setDecomposing, setDecompositionError } = useDecompositionStore()

  // Load requirements from store
  useEffect(() => {
    async function fetchRequirements() {
      try {
        // Use mock data for now
        const mockReqs: Requirement[] = [
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
        ]
        setRequirements(mockReqs)
      } finally {
        setLoading(false)
      }
    }
    fetchRequirements()
  }, [])

  const filteredRequirements = requirements.filter(
    (req) =>
      req.title.toLowerCase().includes(search.toLowerCase()) ||
      req.description?.toLowerCase().includes(search.toLowerCase())
  )

  const handleDecompose = (req: Requirement) => {
    setSelectedRequirement(req)
    setRequirementText(req.description || req.title)
    setDecompositionResult(null)
    setDecomposeDialogOpen(true)
  }

  const handleDecomposeSubmit = async () => {
    if (!requirementText.trim()) return

    setDecomposing(true)
    setDecompositionError(null)

    try {
      const response = await fetch('/api/v1/requirements/decompose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirement_text: requirementText,
          project_id: selectedRequirement?.project_id || '1',
          requirement_id: selectedRequirement?.id,
        }),
      })

      if (!response.ok) throw new Error('Decomposition failed')

      const result: DecompositionResult = await response.json()
      setDecompositionResult(result)
    } catch (error) {
      setDecompositionError(error instanceof Error ? error.message : 'Failed to decompose')
    } finally {
      setDecomposing(false)
    }
  }

  const stats = {
    total: requirements.length,
    active: requirements.filter((r) => r.status === 'active').length,
    completed: requirements.filter((r) => r.status === 'completed').length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">需求管理</h1>
          <p className="text-muted-foreground mt-1">需求分解与任务生成</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          新建需求
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              总需求数
            </CardTitle>
            <Sparkles className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
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
            <div className="text-2xl font-bold">{stats.active}</div>
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
            <div className="text-2xl font-bold">{stats.completed}</div>
          </CardContent>
        </Card>
      </div>

      {/* Requirements Table */}
      <Card>
        <CardHeader>
          <CardTitle>需求列表</CardTitle>
          <CardDescription>
            <div className="mt-2 flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索需求..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[400px]">需求</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>优先级</TableHead>
                <TableHead>更新时间</TableHead>
                <TableHead className="w-[200px]">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    加载中...
                  </TableCell>
                </TableRow>
              ) : filteredRequirements.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    暂无需求
                  </TableCell>
                </TableRow>
              ) : (
                filteredRequirements.map((req) => (
                  <RequirementRow key={req.id} requirement={req} onDecompose={handleDecompose} />
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Decomposition Dialog */}
      <Dialog open={decomposeDialogOpen} onOpenChange={setDecomposeDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-yellow-500" />
              AI 需求分解
            </DialogTitle>
            <DialogDescription>
              {selectedRequirement
                ? `分解需求: ${selectedRequirement.title}`
                : '输入需求文本进行 AI 分析和分解'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">需求描述</label>
              <Textarea
                value={requirementText}
                onChange={(e) => setRequirementText(e.target.value)}
                placeholder="描述你想要实现的功能..."
                rows={4}
              />
            </div>

            {isDecomposing ? (
              <div className="flex flex-col items-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4" />
                <p className="text-muted-foreground">AI 正在分析需求...</p>
              </div>
            ) : decompositionResult ? (
              <DecompositionResultView result={decompositionResult} />
            ) : (
              <Button onClick={handleDecomposeSubmit} disabled={!requirementText.trim()}>
                <Sparkles className="h-4 w-4 mr-2" />
                开始分解
              </Button>
            )}
          </div>

          {decompositionResult && (
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setDecompositionResult(null)}
              >
                重新分解
              </Button>
              <Button onClick={() => setDecomposeDialogOpen(false)}>
                创建任务
              </Button>
            </DialogFooter>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
