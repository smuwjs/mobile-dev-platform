import { useEffect, useCallback } from 'react'
import { getWebSocketClient, type WebSocketMessage } from '@/lib/websocket'
import { useTaskStore, useRequirementStore, useDecompositionStore, type DecompositionResult } from '@/stores'
import type { Task } from '@/types'

export function useWebSocketSync() {
  const { updateTask, updateCeleryTaskState } = useTaskStore()
  const { updateRequirement } = useRequirementStore()
  const { setDecomposition } = useDecompositionStore()

  const handleMessage = useCallback((message: WebSocketMessage) => {
    const { type } = message

    switch (type) {
      case 'task_update': {
        const { task_id, data } = message
        if (task_id && data) {
          updateTask(task_id, data)
        }
        break
      }

      case 'task_progress': {
        const { task_id, progress, status } = message
        if (task_id) {
          updateCeleryTaskState(task_id, {
            id: task_id,
            state: (status as 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE') || 'PENDING',
            progress: progress || 0,
          })
        }
        break
      }

      case 'task_completed': {
        const { task_id, result, error } = message
        if (task_id) {
          updateCeleryTaskState(task_id, {
            id: task_id,
            state: error ? 'FAILURE' : 'SUCCESS',
            result,
            error: error || null,
          })
          // Also update the local task
          if (error) {
            updateTask(task_id, { status: 'failed' })
          }
        }
        break
      }

      case 'celery_task_update': {
        const { task_id, state, progress, result, error, metadata } = message
        if (task_id) {
          updateCeleryTaskState(task_id, {
            id: task_id,
            state: (state as 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE') || 'PENDING',
            progress: progress || 0,
            result: result || null,
            error: error || null,
            task_name: metadata?.task_name as string | null,
            task_type: metadata?.task_type as string | null,
          })
        }
        break
      }

      case 'celery_task_progress': {
        const { task_id, progress, state } = message
        if (task_id) {
          updateCeleryTaskState(task_id, {
            id: task_id,
            state: (state as 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE') || 'PENDING',
            progress: progress || 0,
          })
        }
        break
      }

      case 'celery_task_completed': {
        const { task_id, result, error } = message
        if (task_id) {
          updateCeleryTaskState(task_id, {
            id: task_id,
            state: error ? 'FAILURE' : 'SUCCESS',
            result: result || null,
            error: error || null,
          })
        }
        break
      }

      case 'requirement_update': {
        const { requirement_id, data } = message
        if (requirement_id && data) {
          // Extract only fields that are valid for Requirement
          const { status, ...rest } = data as Partial<Task> & { status?: string }
          updateRequirement(requirement_id, rest)
        }
        break
      }

      case 'decomposition_update': {
        const { requirement_id, sub_requirements, tasks } = message
        if (requirement_id && sub_requirements && tasks) {
          // Update decomposition store with results
          setDecomposition({
            requirement_id,
            complexity: 0,
            estimated_total_hours: 0,
            sub_requirements: sub_requirements as DecompositionResult['sub_requirements'],
            tasks: tasks as DecompositionResult['tasks'],
            validation: { status: 'valid', conflicts: [], warnings: [], suggestions: [] },
          })
        }
        break
      }

      case 'execution_update': {
        const { task_id, execution_id, status, result, error } = message
        if (task_id) {
          updateCeleryTaskState(execution_id || task_id, {
            id: execution_id || task_id,
            state: (status as 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE') || 'PENDING',
            result: result || null,
            error: error || null,
          })
        }
        break
      }

      default:
        break
    }
  }, [updateTask, updateCeleryTaskState, updateRequirement, setDecomposition])

  useEffect(() => {
    const client = getWebSocketClient()

    const unsubscribe = client.onMessage(handleMessage)

    // Connect if not connected
    if (!client.isConnected) {
      client.connect().catch(console.error)
    }

    return () => {
      unsubscribe()
    }
  }, [handleMessage])
}

// Hook for task-specific WebSocket updates
export function useTaskWebSocket(taskId: string) {
  const { celeryTaskStates, updateCeleryTaskState } = useTaskStore()

  const taskState = celeryTaskStates[taskId]

  useEffect(() => {
    const client = getWebSocketClient()

    const handleMessage = (message: WebSocketMessage) => {
      if (message.task_id === taskId) {
        const { type, state, progress, result, error } = message

        if (type === 'celery_task_update' || type === 'celery_task_progress') {
          updateCeleryTaskState(taskId, {
            id: taskId,
            state: (state as 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE') || 'PENDING',
            progress: progress || 0,
            result: result || null,
            error: error || null,
          })
        }
      }
    }

    const unsubscribe = client.onMessage(handleMessage)

    return () => {
      unsubscribe()
    }
  }, [taskId, updateCeleryTaskState])

  return {
    state: taskState?.state || 'PENDING',
    progress: taskState?.progress || 0,
    result: taskState?.result,
    error: taskState?.error,
  }
}
