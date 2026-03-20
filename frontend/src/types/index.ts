export interface Project {
  id: string
  name: string
  description: string
  status: 'planning' | 'in_progress' | 'completed' | 'suspended'
  created_at: string
  updated_at: string
  member_count: number
  task_count: number
  progress: number
}

export interface Task {
  id: string
  project_id: string
  title: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  assignee?: string
  priority: 'low' | 'medium' | 'high'
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
}

export interface Requirement {
  id: string
  project_id: string
  title: string
  description: string
  status: 'draft' | 'active' | 'completed' | 'archived'
  priority: 'low' | 'medium' | 'high'
  created_at: string
  updated_at: string
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
