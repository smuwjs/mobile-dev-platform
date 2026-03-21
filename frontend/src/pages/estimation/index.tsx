import { useState } from 'react'
import { Calculator, Info } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { CostEstimation } from '@/components/openspec/CostEstimation'

const platformOptions = [
  { value: 'react-native', label: 'React Native' },
  { value: 'flutter', label: 'Flutter' },
  { value: 'ios', label: 'iOS (原生)' },
  { value: 'android', label: 'Android (原生)' },
  { value: 'uni-app', label: 'Uni-app' },
]

export default function EstimationPage() {
  const [estimatedHours, setEstimatedHours] = useState(100)
  const [complexity, setComplexity] = useState(2)
  const [subRequirementsCount, setSubRequirementsCount] = useState(5)
  const [tasksCount, setTasksCount] = useState(20)
  const [platform, setPlatform] = useState('react-native')
  const [budget, setBudget] = useState<number | undefined>(undefined)
  const [budgetInput, setBudgetInput] = useState('')

  const handleBudgetInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setBudgetInput(val)
    const parsed = parseInt(val, 10)
    setBudget(isNaN(parsed) ? undefined : parsed)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">成本估算</h1>
          <p className="text-muted-foreground mt-1">项目成本与资源预估工具</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Input Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              项目参数
            </CardTitle>
            <CardDescription>调整参数以获取实时成本估算</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Estimated Hours */}
            <div className="space-y-2">
              <Label>预估工时 (小时)</Label>
              <Input
                type="number"
                value={estimatedHours}
                onChange={(e) => setEstimatedHours(Math.max(1, parseInt(e.target.value) || 0))}
                min={1}
              />
              <p className="text-xs text-muted-foreground">
                约 {Math.round(estimatedHours / 8)} 人天 / {Math.round(estimatedHours / 24)} 人月
              </p>
            </div>

            {/* Complexity */}
            <div className="space-y-2">
              <Label>项目复杂度</Label>
              <Select
                value={complexity.toString()}
                onValueChange={(val) => setComplexity(parseInt(val))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">简单 (×0.8)</SelectItem>
                  <SelectItem value="2">中等 (×1.0)</SelectItem>
                  <SelectItem value="3">复杂 (×1.3)</SelectItem>
                  <SelectItem value="4">非常复杂 (×1.6)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Platform */}
            <div className="space-y-2">
              <Label>目标平台</Label>
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {platformOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Sub-requirements Count */}
            <div className="space-y-2">
              <Label>子需求数量</Label>
              <div className="pt-2">
                <Slider
                  value={[subRequirementsCount]}
                  onValueChange={(val) => setSubRequirementsCount(val[0])}
                  min={1}
                  max={50}
                  step={1}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>1</span>
                <span className="font-medium">{subRequirementsCount}</span>
                <span>50</span>
              </div>
            </div>

            {/* Tasks Count */}
            <div className="space-y-2">
              <Label>任务数量</Label>
              <div className="pt-2">
                <Slider
                  value={[tasksCount]}
                  onValueChange={(val) => setTasksCount(val[0])}
                  min={1}
                  max={200}
                  step={1}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>1</span>
                <span className="font-medium">{tasksCount}</span>
                <span>200</span>
              </div>
            </div>

            {/* Budget */}
            <div className="space-y-2">
              <Label>项目预算 (可选)</Label>
              <Input
                type="number"
                placeholder="输入预算金额"
                value={budgetInput}
                onChange={handleBudgetInputChange}
              />
              <p className="text-xs text-muted-foreground">
                设置预算后可对比实际估算成本
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Estimation Result */}
        <div className="lg:col-span-2">
          <CostEstimation
            estimatedHours={estimatedHours}
            complexity={complexity}
            subRequirementsCount={subRequirementsCount}
            tasksCount={tasksCount}
            platform="Mobile"
            techStack={platform}
            budget={budget}
            onBudgetChange={setBudget}
          />
        </div>
      </div>

      {/* Info Card */}
      <Card className="border-dashed">
        <CardContent className="pt-4">
          <div className="flex items-start gap-3 text-sm text-muted-foreground">
            <Info className="h-4 w-4 shrink-0 mt-0.5" />
            <p>
              成本估算基于行业标准费率计算，实际项目成本可能因团队经验、技术选型、需求变更等因素而有所不同。
              建议结合 AI 需求分解结果进行综合评估，并在项目执行过程中持续跟踪实际消耗。
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
