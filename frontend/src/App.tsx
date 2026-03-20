import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">Mobile Dev Platform</h1>
          <p className="text-gray-600">React + TypeScript + TailwindCSS + shadcn/ui</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>React 18</CardTitle>
              <CardDescription>UI 框架</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                现代化 React 开发，使用 Hooks 和函数式组件
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>TypeScript 5</CardTitle>
              <CardDescription>类型安全</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                静态类型检查，提升代码质量和开发体验
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>TailwindCSS</CardTitle>
              <CardDescription>原子化 CSS</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                快速构建自定义 UI，设计系统集成
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-center gap-4">
          <Button variant="default">Default</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>项目目录结构</CardTitle>
            <CardDescription>src/ 目录结构</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div className="p-2 bg-muted rounded">components/</div>
              <div className="p-2 bg-muted rounded">pages/</div>
              <div className="p-2 bg-muted rounded">stores/</div>
              <div className="p-2 bg-muted rounded">hooks/</div>
              <div className="p-2 bg-muted rounded">lib/</div>
              <div className="p-2 bg-muted rounded">types/</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
