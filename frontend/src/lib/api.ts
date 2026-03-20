import axios from 'axios'
import type {
  Project,
  Task,
  Requirement,
  CostRecord,
  DashboardStats,
  ApiResponse,
  Activity,
} from '@/types'

const api = axios.create({
  baseURL: '/dev-api',
  timeout: 10000,
})

// Dashboard
export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get('/dashboard/stats')
  return data
}

export async function getRecentActivities(): Promise<Activity[]> {
  const { data } = await api.get('/dashboard/activities')
  return data.items || []
}

// Projects
export async function getProjects(params?: {
  page?: number
  page_size?: number
}): Promise<ApiResponse<Project>> {
  const { data } = await api.get('/v1/projects/', { params })
  return data
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await api.get(`/v1/projects/${id}`)
  return data
}

export async function createProject(payload: Partial<Project>): Promise<Project> {
  const { data } = await api.post('/v1/projects/', payload)
  return data
}

export async function updateProject(id: string, payload: Partial<Project>): Promise<Project> {
  const { data } = await api.put(`/v1/projects/${id}`, payload)
  return data
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/v1/projects/${id}`)
}

// Requirements
export async function getRequirements(projectId: string): Promise<ApiResponse<Requirement>> {
  const { data } = await api.get(`/v1/projects/${projectId}/requirements`)
  return data
}

// Tasks
export async function getTasks(params?: {
  project_id?: string
  status?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<Task>> {
  const { data } = await api.get('/v1/tasks/', { params })
  return data
}

export async function getTask(id: string): Promise<Task> {
  const { data } = await api.get(`/v1/tasks/${id}`)
  return data
}

// Costs
export async function getCosts(params?: {
  project_id?: string
  start_date?: string
  end_date?: string
}): Promise<ApiResponse<CostRecord>> {
  const { data } = await api.get('/v1/costs/', { params })
  return data
}

export async function getCostSummary(): Promise<{
  total: number
  by_category: Record<string, number>
  by_month: Array<{ month: string; amount: number }>
}> {
  const { data } = await api.get('/v1/costs/summary')
  return data
}

export default api
