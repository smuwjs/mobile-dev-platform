import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FolderKanban,
  ListTodo,
  Receipt,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dev/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dev/projects', label: 'Projects', icon: FolderKanban },
  { href: '/dev/tasks', label: 'Tasks', icon: ListTodo },
  { href: '/dev/costs', label: 'Costs', icon: Receipt },
]

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-primary">Mobile Dev Platform</h1>
          <p className="text-sm text-muted-foreground mt-1">Project Management</p>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive =
                item.href === '/dev/'
                  ? location.pathname === '/dev/' || location.pathname === '/dev'
                  : location.pathname.startsWith(item.href)

              return (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )}
                  >
                    <item.icon className="h-4 w-4" />
                    {item.label}
                    {isActive && <ChevronRight className="ml-auto h-4 w-4" />}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        <div className="p-4 border-t">
          <div className="text-xs text-muted-foreground">
            <p>Version 1.0.0</p>
            <p className="mt-1">Dev Environment</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-muted/30">
        <div className="p-8">{children}</div>
      </main>
    </div>
  )
}
