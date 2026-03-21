import {
  DollarSign,
  Cpu,
  Zap,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Info,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

interface CostEstimationProps {
  estimatedHours: number
  complexity: number
  subRequirementsCount: number
  tasksCount: number
  platform?: string
  techStack?: string
  budget?: number
  onBudgetChange?: (budget: number) => void
}

interface CostBreakdown {
  category: string
  amount: number
  percentage: number
  icon: React.ElementType
  color: string
}

export function CostEstimation({
  estimatedHours,
  complexity,
  subRequirementsCount: _subRequirementsCount,
  tasksCount: _tasksCount,
  platform = 'React Native',
  techStack = 'mobile',
  budget,
}: CostEstimationProps) {
  // Cost calculation factors
  const hourlyRates = {
    development: 150, // CNY/hour
    design: 120,
    testing: 100,
    management: 80,
  }

  const platformMultipliers: Record<string, number> = {
    ios: 1.3,
    android: 1.2,
    'react-native': 1.0,
    flutter: 1.1,
    'uni-app': 0.9,
  }

  const complexityMultipliers: Record<number, number> = {
    1: 0.8,
    2: 1.0,
    3: 1.3,
    4: 1.6,
  }

  const hourlyRate = hourlyRates.development * (platformMultipliers[techStack] || 1.0)
  const complexityMultiplier = complexityMultipliers[complexity] || 1.0

  // Calculate costs
  const developmentCost = Math.round(estimatedHours * hourlyRate * complexityMultiplier)
  const designCost = Math.round(estimatedHours * 0.15 * hourlyRates.design)
  const testingCost = Math.round(estimatedHours * 0.1 * hourlyRates.testing)
  const managementCost = Math.round(estimatedHours * 0.08 * hourlyRates.management)

  const totalCost = developmentCost + designCost + testingCost + managementCost

  const breakdown: CostBreakdown[] = [
    {
      category: '开发',
      amount: developmentCost,
      percentage: Math.round((developmentCost / totalCost) * 100),
      icon: Cpu,
      color: 'text-blue-500',
    },
    {
      category: '设计',
      amount: designCost,
      percentage: Math.round((designCost / totalCost) * 100),
      icon: Zap,
      color: 'text-pink-500',
    },
    {
      category: '测试',
      amount: testingCost,
      percentage: Math.round((testingCost / totalCost) * 100),
      icon: CheckCircle2,
      color: 'text-green-500',
    },
    {
      category: '管理',
      amount: managementCost,
      percentage: Math.round((managementCost / totalCost) * 100),
      icon: TrendingUp,
      color: 'text-orange-500',
    },
  ]

  // Token estimation (rough estimate for Claude API)
  const estimatedTokens = Math.round(estimatedHours * 5000) // ~5000 tokens per hour of dev work
  const tokenCostUSD = estimatedTokens * 0.000015 // Claude 3.5 Sonnet input price
  const tokenCostCNY = Math.round(tokenCostUSD * 7.25)

  // Risk assessment
  const riskFactors: { level: 'low' | 'medium' | 'high'; message: string }[] = []
  if (complexity >= 3) {
    riskFactors.push({ level: 'high', message: '高复杂度项目，存在需求变更风险' })
  }
  if (estimatedHours > 200) {
    riskFactors.push({ level: 'medium', message: '大型项目，建议分阶段交付' })
  }
  if (techStack === 'ios' || techStack === 'android') {
    riskFactors.push({ level: 'medium', message: '原生平台开发周期较长' })
  }

  const budgetStatus = budget
    ? totalCost <= budget
      ? { status: 'under', label: '预算内', color: 'text-green-600' }
      : { status: 'over', label: '超出预算', color: 'text-red-600' }
    : null

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card className="border-primary/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-green-500" />
            成本预估
          </CardTitle>
          <CardDescription>
            基于 {platform} / {techStack} 技术栈的估算
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">预估总成本</span>
              <span className="text-2xl font-bold text-green-600">
                ¥{totalCost.toLocaleString()}
              </span>
              <span className="text-xs text-muted-foreground">
                ≈ ${Math.round(totalCost / 7.25).toLocaleString()} USD
              </span>
            </div>
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">开发工时</span>
              <span className="text-2xl font-bold">{estimatedHours}h</span>
              <span className="text-xs text-muted-foreground">
                ≈ {(estimatedHours / 8).toFixed(1)} 人天
              </span>
            </div>
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">小时成本率</span>
              <span className="text-2xl font-bold">¥{hourlyRate}</span>
              <span className="text-xs text-muted-foreground">元/小时</span>
            </div>
            <div className="flex flex-col p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">复杂度系数</span>
              <span className="text-2xl font-bold">×{complexityMultiplier}</span>
              <span className="text-xs text-muted-foreground">
                {complexity >= 3 ? '高' : complexity >= 2 ? '中' : '低'}复杂度
              </span>
            </div>
          </div>

          {budgetStatus && (
            <div className="mt-4 p-3 rounded-lg bg-muted">
              <div className="flex items-center justify-between">
                <span className="text-sm">预算状态</span>
                <Badge className={budgetStatus.color} variant="outline">
                  {budgetStatus.label}
                </Badge>
              </div>
              <Progress
                value={Math.min((totalCost / (budget || 1)) * 100, 100)}
                className="mt-2"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>已用: ¥{totalCost.toLocaleString()}</span>
                <span>预算: ¥{budget?.toLocaleString()}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cost Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>成本细分</CardTitle>
          <CardDescription>各类型成本占比与金额</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {breakdown.map((item) => (
            <div key={item.category} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <item.icon className={`h-4 w-4 ${item.color}`} />
                  <span className="font-medium">{item.category}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground">{item.percentage}%</span>
                  <span className="font-medium">¥{item.amount.toLocaleString()}</span>
                </div>
              </div>
              <Progress value={item.percentage} className="h-2" />
            </div>
          ))}

          <Separator className="my-4" />

          <div className="flex items-center justify-between">
            <span className="font-semibold">总计</span>
            <span className="text-xl font-bold text-green-600">
              ¥{totalCost.toLocaleString()}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Token Cost */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-purple-500" />
            AI 成本预估
          </CardTitle>
          <CardDescription>Claude API 消耗估算</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex flex-col p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">预估 Token 数</span>
              <span className="text-lg font-bold">{estimatedTokens.toLocaleString()}</span>
            </div>
            <div className="flex flex-col p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">USD 成本</span>
              <span className="text-lg font-bold">${tokenCostUSD.toFixed(2)}</span>
            </div>
            <div className="flex flex-col p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">CNY 成本</span>
              <span className="text-lg font-bold text-purple-600">¥{tokenCostCNY}</span>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            * 基于 Claude 3.5 Sonnet API 价格估算，实际消耗会因任务复杂度而有所不同
          </p>
        </CardContent>
      </Card>

      {/* Risk Assessment */}
      {riskFactors.length > 0 && (
        <Card className="border-yellow-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-700">
              <AlertCircle className="h-5 w-5" />
              风险提示
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {riskFactors.map((risk, index) => (
                <li
                  key={index}
                  className={`flex items-start gap-2 text-sm ${
                    risk.level === 'high' ? 'text-red-600' : 'text-yellow-600'
                  }`}
                >
                  <span>•</span>
                  <span>{risk.message}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Info */}
      <Card className="border-dashed">
        <CardContent className="pt-4">
          <div className="flex items-start gap-3 text-sm text-muted-foreground">
            <Info className="h-4 w-4 shrink-0 mt-0.5" />
            <p>
              以上估值为参考值，实际成本可能因项目复杂度、团队经验、需求变更等因素有所不同。
              建议在项目执行过程中持续跟踪实际消耗，及时调整预算和计划。
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
