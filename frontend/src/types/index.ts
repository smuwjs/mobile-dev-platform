export interface Project {
  id: string
  name: string
  description: string
  platform?: 'android' | 'ios' | 'harmony' | 'cross'
  status: 'planning' | 'in_progress' | 'completed' | 'suspended'
  created_at: string
  updated_at: string
  member_count: number
  task_count: number
  progress: number
  // 新增字段
  local_path?: string
  spec_framework?: 'openspec' | 'speckit' | 'superpowers'
  spec_config?: Record<string, any>
}

export interface Task {
  id: string
  project_id: string
  requirement_id?: string
  title: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  assignee?: string
  priority: 'low' | 'medium' | 'high'
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
  progress?: number
  // 新增字段
  claude_session_id?: string
  token_usage?: {
    input: number
    output: number
    total: number
  }
  artifacts?: Record<string, any>
  execution_log?: {
    output: string
    error: string
  }
}

export interface Requirement {
  id: string
  project_id: string
  parent_id?: string
  title: string
  description: string
  status: 'draft' | 'active' | 'completed' | 'archived'
  priority: 'low' | 'medium' | 'high'
  created_at: string
  updated_at: string
  // 树状结构支持
  children?: Requirement[]
  tasks?: Task[]
}

export interface CostRecord {
  id: string
  project_id: string
  category: 'development' | 'design' | 'infrastructure' | 'other'
  amount: number
  description: string
  date: string
}

export interface DashboardStats {
  total_projects: number
  active_projects: number
  total_tasks: number
  completed_tasks: number
  total_cost: number
  recent_activities: Activity[]
}

export interface Activity {
  id: string
  type: 'project_created' | 'task_completed' | 'cost_added' | 'member_joined'
  description: string
  timestamp: string
}

export interface ApiResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface User {
  id: string
  username: string
  email?: string
}

// 报告类型
export interface ProjectReport {
  project_id: string
  requirement_id: string
  generated_at: string
  summary: string
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  total_token_usage: {
    input: number
    output: number
    total: number
  }
  sections: {
    title: string
    content: string
  }[]
}

// 规范框架
export interface SpecFramework {
  id: string
  name: string
  description: string
  url: string
}

// 任务执行状态
export interface ExecutionStatus {
  task_id: string
  status: string
  progress: number
  token_usage: {
    input: number
    output: number
    total: number
  }
}
