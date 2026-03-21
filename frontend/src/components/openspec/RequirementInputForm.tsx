import { useState } from 'react'
import { Sparkles, Loader2, FileText, Lightbulb, Target } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { useDecompositionStore, type DecompositionResult } from '@/stores/requirementStore'

interface RequirementInputFormProps {
  projectId: string
  onDecompose: (requirementText: string, projectId: string) => Promise<void>
  onResult?: (result: DecompositionResult) => void
}

const templateSuggestions = [
  { label: '用户认证模块', text: '实现完整的用户认证系统，包括手机号注册登录、第三方登录（微信/苹果）、密码找回功能，需要考虑安全性与用户体验平衡' },
  { label: '商品展示模块', text: '开发商品展示功能，包含首页推荐、商品分类筛选、商品详情页、商品搜索功能，支持图片懒加载与下拉刷新' },
  { label: '订单支付模块', text: '实现订单管理与在线支付功能，支持购物车、订单创建、支付流程、订单状态跟踪、退款申请等完整交易流程' },
  { label: '社交分享模块', text: '开发社交分享功能，支持图片/文字分享到主流社交平台，生成分享海报，集成裂变营销机制' },
]

export function RequirementInputForm({ projectId, onDecompose, onResult }: RequirementInputFormProps) {
  const [requirementText, setRequirementText] = useState('')
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium')
  const [platform, setPlatform] = useState('mobile')
  const [techStack, setTechStack] = useState('react-native')

  const { isDecomposing, setDecomposing, setDecompositionError, decompositionError } = useDecompositionStore()

  const handleSubmit = async () => {
    if (!requirementText.trim()) return

    setDecomposing(true)
    setDecompositionError(null)

    try {
      await onDecompose(requirementText, projectId)
    } finally {
      setDecomposing(false)
    }
  }

  const handleTemplateClick = (text: string) => {
    setRequirementText(text)
  }

  return (
    <div className="space-y-6">
      {/* Quick Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            快速模板
          </CardTitle>
          <CardDescription>选择常用需求模板快速开始</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {templateSuggestions.map((template) => (
              <Badge
                key={template.label}
                variant="outline"
                className="cursor-pointer hover:bg-secondary transition-colors"
                onClick={() => handleTemplateClick(template.text)}
              >
                {template.label}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Requirement Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            需求描述
          </CardTitle>
          <CardDescription>
            详细描述你想要实现的功能，系统将自动分析并拆解为可执行的任务
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Basic Info */}
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="title">需求标题</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="简洁描述需求"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="priority">优先级</Label>
              <Select value={priority} onValueChange={(v) => setPriority(v as typeof priority)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">低</SelectItem>
                  <SelectItem value="medium">中</SelectItem>
                  <SelectItem value="high">高</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="platform">目标平台</Label>
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mobile">移动端</SelectItem>
                  <SelectItem value="ios">iOS</SelectItem>
                  <SelectItem value="android">Android</SelectItem>
                  <SelectItem value="cross-platform">跨平台</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Tech Stack */}
          <div className="space-y-2">
            <Label htmlFor="techStack">技术栈</Label>
            <Select value={techStack} onValueChange={setTechStack}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="react-native">React Native</SelectItem>
                <SelectItem value="flutter">Flutter</SelectItem>
                <SelectItem value="swift">Swift (iOS)</SelectItem>
                <SelectItem value="kotlin">Kotlin (Android)</SelectItem>
                <SelectItem value="uni-app">uni-app</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Requirement Text */}
          <div className="space-y-2">
            <Label htmlFor="requirement">详细需求</Label>
            <Textarea
              id="requirement"
              value={requirementText}
              onChange={(e) => setRequirementText(e.target.value)}
              placeholder="详细描述你的需求，包括功能点、用户场景、技术要求等..."
              rows={6}
              className="font-mono text-sm"
            />
          </div>

          {/* Error Display */}
          {decompositionError && (
            <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
              {decompositionError}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button
              onClick={handleSubmit}
              disabled={!requirementText.trim() || isDecomposing}
              size="lg"
            >
              {isDecomposing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  分析中...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  AI 分解需求
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Platform Selection Tips */}
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Target className="h-5 w-5 text-blue-500" />
            分解说明
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="text-primary font-medium">1.</span>
              <span>系统将分析需求文本，识别核心功能模块</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary font-medium">2.</span>
              <span>基于功能复杂度预估开发时间和资源消耗</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary font-medium">3.</span>
              <span>生成可执行的任务清单，支持直接创建为任务</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary font-medium">4.</span>
              <span>提供成本预估，帮助你规划项目预算</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
