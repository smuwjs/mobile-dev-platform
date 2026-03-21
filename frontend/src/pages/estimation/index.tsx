import { useState } from 'react'
import {
  Settings,
  Calculator,
  Clock,
  DollarSign,
  Cpu,
  Save,
  RotateCcw,
  TestTube,
  TrendingUp,
  Zap,
  Globe,
  Smartphone,
  Monitor,
} from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useDecompositionStore } from '@/stores/requirementStore'

interface ModelConfig {
  // Hourly rates
  hourlyRates: {
    development: number
    design: number
    testing: number
    management: number
    devops: number
  }
  // Platform multipliers
  platformMultipliers: {
    ios: number
    android: number
    reactNative: number
    flutter: number
    web: number
  }
  // Complexity factors
  complexityFactors: {
    simple: number
    medium: number
    complex: number
    veryComplex: number
  }
  // AI/Token settings
  tokenSettings: {
    inputCostPer1M: number
    outputCostPer1M: number
    avgInputTokensPerHour: number
    avgOutputTokensPerHour: number
  }
  // Risk factors
  riskFactors: {
    contingencyPercent: number
    bufferMultiplier: number
  }
}

const defaultConfig: ModelConfig = {
  hourlyRates: {
    development: 150,
    design: 120,
    testing: 100,
    management: 80,
    devops: 130,
  },
  platformMultipliers: {
    ios: 1.3,
    android: 1.2,
    reactNative: 1.0,
    flutter: 1.1,
    web: 0.8,
  },
  complexityFactors: {
    simple: 0.7,
    medium: 1.0,
    complex: 1.4,
    veryComplex: 1.8,
  },
  tokenSettings: {
    inputCostPer1M: 15, // Claude 3.5 Sonnet
    outputCostPer1M: 75,
    avgInputTokensPerHour: 300000,
    avgOutputTokensPerHour: 100000,
  },
  riskFactors: {
    contingencyPercent: 15,
    bufferMultiplier: 1.2,
  },
}

export default function EstimationConfigPage() {
  const [config, setConfig] = useState<ModelConfig>(defaultConfig)
  const [savedConfig, setSavedConfig] = useState<ModelConfig>(defaultConfig)
  const [hasChanges, setHasChanges] = useState(false)
  const [testResult, setTestResult] = useState<{
    estimatedHours: number
    estimatedCost: number
    tokenCost: number
    totalCost: number
  } | null>(null)

  const updateConfig = (path: string, value: number) => {
    setHasChanges(true)
    setConfig((prev) => {
      const keys = path.split('.')
      const newConfig = { ...prev }
      let obj: Record<string, unknown> = newConfig
      for (let i = 0; i < keys.length - 1; i++) {
        obj[keys[i]] = { ...(obj[keys[i]] as Record<string, unknown>) }
        obj = obj[keys[i]] as Record<string, unknown>
      }
      obj[keys[keys.length - 1]] = value
      return newConfig
    })
  }

  const handleSave = () => {
    setSavedConfig(config)
    setHasChanges(false)
    // In real implementation, save to server
    localStorage.setItem('estimation-model-config', JSON.stringify(config))
  }

  const handleReset = () => {
    setConfig(savedConfig)
    setHasChanges(false)
  }

  const handleTest = () => {
    // Test with sample values
    const sampleComplexity = 2.5
    const sampleHours = 40
    const sampleTokenEstimate = 200000

    const devCost = sampleHours * config.hourlyRates.development * sampleComplexity
    const tokenCostUSD =
      (sampleTokenEstimate * config.tokenSettings.inputCostPer1M) / 1000000 +
      (sampleTokenEstimate * config.tokenSettings.outputCostPer1M) / 1000000
    const tokenCostCNY = tokenCostUSD * 7.25
    const totalWithRisk = (devCost + tokenCostCNY) * (1 + config.riskFactors.contingencyPercent / 100)

    setTestResult({
      estimatedHours: sampleHours,
      estimatedCost: devCost,
      tokenCost: tokenCostCNY,
      totalCost: Math.round(totalWithRisk),
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">预估模型配置</h1>
          <p className="text-muted-foreground mt-1">
            配置成本计算参数、校准预估模型
          </p>
        </div>
        <div className="flex gap-2">
          {hasChanges && (
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              重置
            </Button>
          )}
          <Button onClick={handleSave} disabled={!hasChanges}>
            <Save className="h-4 w-4 mr-2" />
            保存配置
          </Button>
        </div>
      </div>

      {hasChanges && (
        <div className="p-3 rounded-lg bg-yellow-50 border border-yellow-200 text-sm">
          <Badge variant="outline" className="bg-yellow-100">未保存</Badge>
          <span className="ml-2 text-yellow-800">您有未保存的更改</span>
        </div>
      )}

      <Tabs defaultValue="rates" className="space-y-6">
        <TabsList>
          <TabsTrigger value="rates" className="gap-2">
            <DollarSign className="h-4 w-4" />
            人力费率
          </TabsTrigger>
          <TabsTrigger value="platform" className="gap-2">
            <Smartphone className="h-4 w-4" />
            平台系数
          </TabsTrigger>
          <TabsTrigger value="complexity" className="gap-2">
            <TrendingUp className="h-4 w-4" />
            复杂度
          </TabsTrigger>
          <TabsTrigger value="tokens" className="gap-2">
            <Cpu className="h-4 w-4" />
            AI 成本
          </TabsTrigger>
          <TabsTrigger value="test" className="gap-2">
            <TestTube className="h-4 w-4" />
            测试
          </TabsTrigger>
        </TabsList>

        {/* Hourly Rates */}
        <TabsContent value="rates">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                人力费率配置
              </CardTitle>
              <CardDescription>
                设置不同角色/工种的每小时成本（单位：CNY）
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {[
                  { key: 'development', label: '开发', icon: Monitor },
                  { key: 'design', label: '设计', icon: Globe },
                  { key: 'testing', label: '测试', icon: TestTube },
                  { key: 'management', label: '管理', icon: Settings },
                  { key: 'devops', label: 'DevOps', icon: Zap },
                ].map(({ key, label, icon: Icon }) => (
                  <div key={key} className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                      {label}
                    </Label>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">¥</span>
                      <Input
                        type="number"
                        value={config.hourlyRates[key as keyof typeof config.hourlyRates]}
                        onChange={(e) =>
                          updateConfig(`hourlyRates.${key}`, parseFloat(e.target.value) || 0)
                        }
                        className="w-32"
                      />
                      <span className="text-sm text-muted-foreground">/小时</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Platform Multipliers */}
        <TabsContent value="platform">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smartphone className="h-5 w-5" />
                平台复杂度系数
              </CardTitle>
              <CardDescription>
                不同平台开发复杂度不同，设置相应的系数调整
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                {[
                  { key: 'ios', label: 'iOS 原生', description: 'Swift/SwiftUI 开发' },
                  { key: 'android', label: 'Android 原生', description: 'Kotlin 开发' },
                  { key: 'reactNative', label: 'React Native', description: '跨平台移动开发' },
                  { key: 'flutter', label: 'Flutter', description: 'Google 跨平台框架' },
                  { key: 'web', label: 'Web', description: '响应式 Web 应用' },
                ].map(({ key, label, description }) => (
                  <div key={key} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>{label}</Label>
                        <p className="text-sm text-muted-foreground">{description}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">×</span>
                        <Input
                          type="number"
                          step="0.1"
                          value={config.platformMultipliers[key as keyof typeof config.platformMultipliers]}
                          onChange={(e) =>
                            updateConfig(`platformMultipliers.${key}`, parseFloat(e.target.value) || 1)
                          }
                          className="w-24"
                        />
                      </div>
                    </div>
                    <Slider
                      value={[config.platformMultipliers[key as keyof typeof config.platformMultipliers]]}
                      min={0.5}
                      max={2}
                      step={0.1}
                      onValueChange={([v]) => updateConfig(`platformMultipliers.${key}`, v)}
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Complexity Factors */}
        <TabsContent value="complexity">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                需求复杂度系数
              </CardTitle>
              <CardDescription>
                根据需求复杂度调整工时预估
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>复杂度等级</TableHead>
                    <TableHead>描述</TableHead>
                    <TableHead>系数</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[
                    { key: 'simple', label: '简单', desc: '功能单一，无外部依赖' },
                    { key: 'medium', label: '中等', desc: '有多个模块，轻微外部依赖' },
                    { key: 'complex', label: '复杂', desc: '多系统集成，高性能要求' },
                    { key: 'veryComplex', label: '非常复杂', desc: '创新性功能，高风险技术' },
                  ].map(({ key, label, desc }) => (
                    <TableRow key={key}>
                      <TableCell className="font-medium">{label}</TableCell>
                      <TableCell className="text-muted-foreground">{desc}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Slider
                            value={[config.complexityFactors[key as keyof typeof config.complexityFactors]]}
                            min={0.5}
                            max={2.5}
                            step={0.1}
                            onValueChange={([v]) => updateConfig(`complexityFactors.${key}`, v)}
                            className="w-32"
                          />
                          <Input
                            type="number"
                            step="0.1"
                            value={config.complexityFactors[key as keyof typeof config.complexityFactors]}
                            onChange={(e) =>
                              updateConfig(`complexityFactors.${key}`, parseFloat(e.target.value) || 1)
                            }
                            className="w-20"
                          />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <Separator />

              <div className="space-y-3">
                <h4 className="font-medium">风险系数</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>应急储备百分比</Label>
                    <div className="flex items-center gap-4">
                      <Slider
                        value={[config.riskFactors.contingencyPercent]}
                        min={0}
                        max={30}
                        step={1}
                        onValueChange={([v]) => updateConfig('riskFactors.contingencyPercent', v)}
                        className="flex-1"
                      />
                      <Input
                        type="number"
                        value={config.riskFactors.contingencyPercent}
                        onChange={(e) =>
                          updateConfig('riskFactors.contingencyPercent', parseFloat(e.target.value) || 0)
                        }
                        className="w-20"
                      />
                      <span className="text-muted-foreground">%</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>缓冲系数</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        step="0.1"
                        value={config.riskFactors.bufferMultiplier}
                        onChange={(e) =>
                          updateConfig('riskFactors.bufferMultiplier', parseFloat(e.target.value) || 1)
                        }
                        className="w-24"
                      />
                      <span className="text-sm text-muted-foreground">
                        (工时 × {config.riskFactors.bufferMultiplier} = 调整后工时)
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Token/AI Settings */}
        <TabsContent value="tokens">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="h-5 w-5" />
                AI 成本配置
              </CardTitle>
              <CardDescription>
                配置 Claude API 成本参数（价格基于 Claude 3.5 Sonnet）
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>输入 Token 成本 (每 1M)</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">$</span>
                    <Input
                      type="number"
                      value={config.tokenSettings.inputCostPer1M}
                      onChange={(e) =>
                        updateConfig('tokenSettings.inputCostPer1M', parseFloat(e.target.value) || 0)
                      }
                      className="w-32"
                    />
                    <span className="text-sm text-muted-foreground">USD</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>输出 Token 成本 (每 1M)</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">$</span>
                    <Input
                      type="number"
                      value={config.tokenSettings.outputCostPer1M}
                      onChange={(e) =>
                        updateConfig('tokenSettings.outputCostPer1M', parseFloat(e.target.value) || 0)
                      }
                      className="w-32"
                    />
                    <span className="text-sm text-muted-foreground">USD</span>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <h4 className="font-medium">每小时 Token 消耗估算</h4>
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>平均输入 Token/小时</Label>
                    <Input
                      type="number"
                      value={config.tokenSettings.avgInputTokensPerHour}
                      onChange={(e) =>
                        updateConfig('tokenSettings.avgInputTokensPerHour', parseFloat(e.target.value) || 0)
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>平均输出 Token/小时</Label>
                    <Input
                      type="number"
                      value={config.tokenSettings.avgOutputTokensPerHour}
                      onChange={(e) =>
                        updateConfig('tokenSettings.avgOutputTokensPerHour', parseFloat(e.target.value) || 0)
                      }
                    />
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">
                  预估每小时 AI 成本：$
                  {(
                    (config.tokenSettings.avgInputTokensPerHour * config.tokenSettings.inputCostPer1M +
                      config.tokenSettings.avgOutputTokensPerHour * config.tokenSettings.outputCostPer1M) /
                    1000000
                  ).toFixed(2)}{' '}
                  ≈ ¥
                  {Math.round(
                    (config.tokenSettings.avgInputTokensPerHour * config.tokenSettings.inputCostPer1M +
                      config.tokenSettings.avgOutputTokensPerHour * config.tokenSettings.outputCostPer1M) /
                      1000000 *
                      7.25
                  )}
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Test */}
        <TabsContent value="test">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="h-5 w-5" />
                配置测试
              </CardTitle>
              <CardDescription>
                使用示例数据测试当前配置的计算结果
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">测试参数</h4>
                <div className="grid gap-2 text-sm">
                  <div className="flex gap-4">
                    <span className="text-muted-foreground">复杂度等级：</span>
                    <span>中等 (×{config.complexityFactors.medium})</span>
                  </div>
                  <div className="flex gap-4">
                    <span className="text-muted-foreground">基础工时：</span>
                    <span>40 小时</span>
                  </div>
                  <div className="flex gap-4">
                    <span className="text-muted-foreground">Token 消耗：</span>
                    <span>200,000 tokens</span>
                  </div>
                </div>
              </div>

              <Button onClick={handleTest} className="gap-2">
                <TestTube className="h-4 w-4" />
                运行测试
              </Button>

              {testResult && (
                <div className="space-y-4">
                  <Separator />
                  <h4 className="font-medium">计算结果</h4>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <Card>
                      <CardContent className="pt-4">
                        <div className="text-sm text-muted-foreground">预估工时</div>
                        <div className="text-2xl font-bold">{testResult.estimatedHours}h</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-4">
                        <div className="text-sm text-muted-foreground">人力成本</div>
                        <div className="text-2xl font-bold text-blue-600">
                          ¥{testResult.estimatedCost.toLocaleString()}
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-4">
                        <div className="text-sm text-muted-foreground">AI 成本</div>
                        <div className="text-2xl font-bold text-purple-600">
                          ¥{testResult.tokenCost.toLocaleString()}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="border-primary">
                      <CardContent className="pt-4">
                        <div className="text-sm text-muted-foreground">总成本（含风险）</div>
                        <div className="text-2xl font-bold text-green-600">
                          ¥{testResult.totalCost.toLocaleString()}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="p-3 bg-muted rounded-lg text-sm">
                    <p className="text-muted-foreground">
                      计算公式：基础成本 ¥{testResult.estimatedCost.toLocaleString()} + AI成本 ¥
                      {testResult.tokenCost.toLocaleString()} = ¥
                      {(testResult.estimatedCost + testResult.tokenCost).toLocaleString()}
                    </p>
                    <p className="text-muted-foreground mt-1">
                      含 {config.riskFactors.contingencyPercent}% 应急储备：¥{testResult.totalCost.toLocaleString()}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
