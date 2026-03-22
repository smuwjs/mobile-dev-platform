import { FileText, Download, Copy, Check, Clock, Zap, CheckCircle2, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useState } from 'react'
import type { ProjectReport } from '@/types'

interface ReportViewerProps {
  report: ProjectReport | null
  loading?: boolean
  onRegenerate?: () => void
}

export function ReportViewer({ report, loading, onRegenerate }: ReportViewerProps) {
  const [copied, setCopied] = useState(false)

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="mt-4 text-muted-foreground">生成报告中...</p>
        </CardContent>
      </Card>
    )
  }

  if (!report) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">暂无报告，请先生成报告</p>
          {onRegenerate && (
            <Button className="mt-4" onClick={onRegenerate}>
              生成报告
            </Button>
          )}
        </CardContent>
      </Card>
    )
  }

  const copyToClipboard = () => {
    const text = `${report.summary}\n\n${report.sections.map(s => `## ${s.title}\n${s.content}`).join('\n\n')}`
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const completionRate = report.total_tasks > 0 
    ? Math.round((report.completed_tasks / report.total_tasks) * 100) 
    : 0

  return (
    <div className="space-y-4">
      {/* 报告头部信息 */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              项目完成报告
            </CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={copyToClipboard}>
                {copied ? <Check className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
                {copied ? '已复制' : '复制'}
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-1" />
                导出
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">{report.summary}</p>
          
          {/* 统计卡片 */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center p-3 bg-accent rounded-lg">
              <p className="text-xs text-muted-foreground">总任务</p>
              <p className="text-2xl font-bold">{report.total_tasks}</p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="flex items-center justify-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <p className="text-xs text-green-600">已完成</p>
              </div>
              <p className="text-2xl font-bold text-green-600">{report.completed_tasks}</p>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="flex items-center justify-center gap-1">
                <XCircle className="h-4 w-4 text-red-500" />
                <p className="text-xs text-red-600">失败</p>
              </div>
              <p className="text-2xl font-bold text-red-600">{report.failed_tasks}</p>
            </div>
            <div className="text-center p-3 bg-accent rounded-lg">
              <div className="flex items-center justify-center gap-1">
                <Zap className="h-4 w-4" />
                <p className="text-xs text-muted-foreground">Token</p>
              </div>
              <p className="text-2xl font-bold">{report.total_token_usage.total.toLocaleString()}</p>
            </div>
          </div>

          {/* 完成率 */}
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-1">
              <span>完成率</span>
              <span>{completionRate}%</span>
            </div>
            <div className="h-2 bg-accent rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-500 transition-all"
                style={{ width: `${completionRate}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Token 消耗详情 */}
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Token 消耗详情
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-xs text-blue-600">输入 Token</p>
              <p className="text-xl font-bold text-blue-600">
                {report.total_token_usage.input.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="text-xs text-purple-600">输出 Token</p>
              <p className="text-xl font-bold text-purple-600">
                {report.total_token_usage.output.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-xs text-green-600">总计</p>
              <p className="text-xl font-bold text-green-600">
                {report.total_token_usage.total.toLocaleString()}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 报告内容 */}
      <Card>
        <Tabs defaultValue="summary">
          <CardHeader className="pb-0">
            <TabsList>
              {report.sections.map((section, i) => (
                <TabsTrigger key={i} value={`section-${i}`}>
                  {section.title}
                </TabsTrigger>
              ))}
            </TabsList>
          </CardHeader>
          <CardContent className="pt-4">
            {report.sections.map((section, i) => (
              <TabsContent key={i} value={`section-${i}`}>
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap font-sans">
                    {section.content}
                  </pre>
                </div>
              </TabsContent>
            ))}
          </CardContent>
        </Tabs>
      </Card>

      {/* 生成时间 */}
      <p className="text-xs text-muted-foreground text-center">
        报告生成时间: {new Date(report.generated_at).toLocaleString('zh-CN')}
      </p>
    </div>
  )
}
