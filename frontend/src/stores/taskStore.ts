import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Task } from '@/types'

// Celery task state tracking
export interface CeleryTaskState {
  id: string
  task_name: string | null
  task_type: string | null
  state: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'REVOKED' | 'RETRY'
  progress: number
  result: unknown | null
  error: string | null
  project_id: string | null
  requirement_id: string | null
  celery_task_id: string | null
  created_at: string | null
  started_at: string | null
  completed_at: string | null
}

export interface TaskState {
  // Local tasks
  tasks: Task[]
  selectedTask: Task | null
  isLoading: boolean
  error: string | null

  // Celery task states
  celeryTaskStates: Record<string, CeleryTaskState>

  // Actions - Local tasks
  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (id: string, updates: Partial<Task>) => void
  removeTask: (id: string) => void
  selectTask: (task: Task | null) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void

  // Actions - Celery task states
  updateCeleryTaskState: (taskId: string, state: Partial<CeleryTaskState>) => void
  removeCeleryTaskState: (taskId: string) => void
  clearCeleryTaskStates: () => void
}

export const useTaskStore = create<TaskState>()(
  persist(
    (set) => ({
      tasks: [],
      selectedTask: null,
      isLoading: false,
      error: null,
      celeryTaskStates: {},

      // Local task actions
      setTasks: (tasks) => set({ tasks }),

      addTask: (task) =>
        set((state) => ({
          tasks: [...state.tasks, task],
        })),

      updateTask: (id, updates) =>
        set((state) => ({
          tasks: state.tasks.map((t) =>
            t.id === id ? { ...t, ...updates } : t
          ),
          selectedTask:
            state.selectedTask?.id === id
              ? { ...state.selectedTask, ...updates }
              : state.selectedTask,
        })),

      removeTask: (id) =>
        set((state) => ({
          tasks: state.tasks.filter((t) => t.id !== id),
          selectedTask:
            state.selectedTask?.id === id ? null : state.selectedTask,
        })),

      selectTask: (task) => set({ selectedTask: task }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      // Celery task state actions
      updateCeleryTaskState: (taskId, updates) =>
        set((state) => ({
          celeryTaskStates: {
            ...state.celeryTaskStates,
            [taskId]: {
              ...state.celeryTaskStates[taskId],
              ...updates,
            } as CeleryTaskState,
          },
        })),

      removeCeleryTaskState: (taskId) =>
        set((state) => {
          const { [taskId]: _, ...rest } = state.celeryTaskStates
          return { celeryTaskStates: rest }
        }),

      clearCeleryTaskStates: () => set({ celeryTaskStates: {} }),
    }),
    {
      name: 'task-storage',
      partialize: (state) => ({
        tasks: state.tasks,
        celeryTaskStates: state.celeryTaskStates,
      }),
    }
  )
)

// Execution log for task viewer
export interface ExecutionLog {
  id: string
  task_id: string
  timestamp: string
  level: 'info' | 'warning' | 'error'
  message: string
}

export interface ExecutionLogState {
  logs: Record<string, ExecutionLog[]>

  addLog: (taskId: string, log: Omit<ExecutionLog, 'id' | 'timestamp' | 'task_id'>) => void
  clearLogs: (taskId: string) => void
  getLogs: (taskId: string) => ExecutionLog[]
}

export const useExecutionLogStore = create<ExecutionLogState>()((set, get) => ({
  logs: {},

  addLog: (taskId, log) =>
    set((state) => ({
      logs: {
        ...state.logs,
        [taskId]: [
          ...(state.logs[taskId] || []),
          {
            ...log,
            task_id: taskId,
            id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
            timestamp: new Date().toISOString(),
          } as ExecutionLog,
        ],
      },
    })),

  clearLogs: (taskId) =>
    set((state) => {
      const { [taskId]: _, ...rest } = state.logs
      return { logs: rest }
    }),

  getLogs: (taskId) => get().logs[taskId] || [],
}))
