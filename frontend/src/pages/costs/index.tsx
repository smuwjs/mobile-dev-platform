import { useEffect, useState } from 'react'
import {
  BarChart3,
  PieChart,
  TrendingUp,
  Receipt,
  Plus,
  Download,
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line,
} from 'recharts'
import { getCosts, getCostSummary } from '@/lib/api'
import { formatDate, formatCurrency } from '@/lib/utils'
import type { CostRecord } from '@/types'

const mockCosts: CostRecord[] = [
  {
    id: '1',
    project_id: '1',
    category: 'development',
    amount: 50000,
    description: '开发团队人力成本',
    date: '2024-03-01',
  },
  {
    id: '2',
    project_id: '1',
    category: 'infrastructure',
    amount: 15000,
    description: '云服务器费用（3月）',
    date: '2024-03-01',
  },
  {
    id: '3',
    project_id: '2',
    category: 'design',
    amount: 25000,
    description: 'UI/UX 设计费用',
    date: '2024-03-05',
  },
  {
    id: '4',
    project_id: '1',
    category: 'development',
    amount: 35000,
    description: '后端开发人力成本',
    date: '2024-03-10',
  },
  {
    id: '5',
    project_id: '3',
    category: 'infrastructure',
    amount: 8000,
    description: '数据库服务费用',
    date: '2024-03-15',
  },
  {
    id: '6',
    project_id: '2',
    category: 'other',
    amount: 5000,
    description: '第三方 API 调用费用',
    date: '2024-03-18',
  },
]

const mockCostSummary = {
  total: 258000,
  by_category: {
    development: 145000,
    design: 45000,
    infrastructure: 48000,
    other: 20000,
  },
  by_month: [
    { month: '1月', amount: 35000 },
    { month: '2月', amount: 48000 },
    { month: '3月', amount: 65000 },
    { month: '4月', amount: 42000 },
    { month: '5月', amount: 38000 },
    { month: '6月', amount: 30000 },
  ],
}

const COLORS = ['#aa3bff', '#8b5cf6', '#6366f1', '#3b82f6']

const categoryLabels: Record<CostRecord['category'], string> = {
  development: '开发',
  design: '设计',
  infrastructure: '基础设施',
  other: '其他',
}

const categoryColors: Record<CostRecord['category'], string> = {
  development: 'bg-purple-100 text-purple-700',
  design: 'bg-pink-100 text-pink-700',
  infrastructure: 'bg-blue-100 text-blue-700',
  other: 'bg-gray-100 text-gray-700',
}

function CostDialog() {
  const [open, setOpen] = useState(false)
  const [category, setCategory] = useState<string>('')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Add cost:', { category, amount, description })
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          记录成本
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>记录成本</DialogTitle>
            <DialogDescription>添加新的成本记录</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="category">成本类别</Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="选择类别" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="development">开发</SelectItem>
                  <SelectItem value="design">设计</SelectItem>
                  <SelectItem value="infrastructure">基础设施</SelectItem>
                  <SelectItem value="other">其他</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="amount">金额</Label>
              <Input
                id="amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="输入金额"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">描述</Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="成本描述"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit">添加</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default function CostsPage() {
  const [costs, setCosts] = useState<CostRecord[]>(mockCosts)
  const [summary, setSummary] = useState<{
    total: number
    by_category: { development: number; design: number; infrastructure: number; other: number }
    by_month: { month: string; amount: number }[]
  }>(mockCostSummary)
  const [loading, setLoading] = useState(true)
  const [dateRange, setDateRange] = useState<string>('all')

  useEffect(() => {
    async function fetchData() {
      try {
        const [costsData, summaryData] = await Promise.all([
          getCosts(),
          getCostSummary(),
        ])
        if (costsData.items.length > 0) {
          setCosts(costsData.items)
        }
        if (summaryData.total) {
          setSummary(summaryData as typeof mockCostSummary)
        }
      } catch {
        // Use mock data on error
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const pieData = Object.entries(summary.by_category).map(([key, value]) => ({
    name: categoryLabels[key as CostRecord['category']],
    value,
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Costs</h1>
          <p className="text-muted-foreground mt-1">成本分析与统计</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            导出报表
          </Button>
          <CostDialog />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              总成本
            </CardTitle>
            <Receipt className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(summary.total)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              累计项目支出
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              开发成本
            </CardTitle>
            <BarChart3 className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(summary.by_category.development)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {((summary.by_category.development / summary.total) * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              设计成本
            </CardTitle>
            <PieChart className="h-4 w-4 text-pink-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(summary.by_category.design)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {((summary.by_category.design / summary.total) * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              基础设施
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(summary.by_category.infrastructure)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {((summary.by_category.infrastructure / summary.total) * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Monthly Cost Trend */}
        <Card>
          <CardHeader>
            <CardTitle>月度成本趋势</CardTitle>
            <CardDescription>近6个月成本变化</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={summary.by_month}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip
                    formatter={(value) => formatCurrency(value as number)}
                  />
                  <Line
                    type="monotone"
                    dataKey="amount"
                    stroke="#aa3bff"
                    strokeWidth={2}
                    dot={{ fill: '#aa3bff' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Cost by Category */}
        <Card>
          <CardHeader>
            <CardTitle>成本类别分布</CardTitle>
            <CardDescription>按类别统计成本占比</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {pieData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => formatCurrency(value as number)}
                  />
                  <Legend />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Cost Bar Chart */}
      <Card>
        <CardHeader>
          <CardTitle>月度成本明细</CardTitle>
          <CardDescription>各月成本柱状图</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary.by_month}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip
                  formatter={(value) => formatCurrency(value as number)}
                />
                <Bar dataKey="amount" fill="#aa3bff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Cost Records Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>成本记录</CardTitle>
              <CardDescription>共 {costs.length} 条记录</CardDescription>
            </div>
            <Select value={dateRange} onValueChange={setDateRange}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="时间范围" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部时间</SelectItem>
                <SelectItem value="30d">最近30天</SelectItem>
                <SelectItem value="90d">最近90天</SelectItem>
                <SelectItem value="1y">最近1年</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>描述</TableHead>
                <TableHead>类别</TableHead>
                <TableHead>金额</TableHead>
                <TableHead>日期</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8">
                    加载中...
                  </TableCell>
                </TableRow>
              ) : costs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8">
                    暂无成本记录
                  </TableCell>
                </TableRow>
              ) : (
                costs.map((cost) => (
                  <TableRow key={cost.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{cost.description}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={categoryColors[cost.category]}
                        variant="secondary"
                      >
                        {categoryLabels[cost.category]}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">
                      {formatCurrency(cost.amount)}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDate(cost.date)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
