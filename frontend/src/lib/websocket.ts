import type { Task } from '@/types'

export type WebSocketMessageType =
  | 'task_update'
  | 'task_progress'
  | 'task_completed'
  | 'execution_update'
  | 'celery_task_update'
  | 'celery_task_progress'
  | 'celery_task_completed'
  | 'requirement_update'
  | 'decomposition_update'
  | 'pong'
  | 'subscribed'
  | 'error'

export interface WebSocketMessage {
  type: WebSocketMessageType
  task_id?: string
  execution_id?: string
  progress?: number
  status?: string
  state?: string
  result?: unknown
  error?: string
  data?: Partial<Task>
  message?: string
  requirement_id?: string
  sub_requirements?: unknown[]
  tasks?: unknown[]
  metadata?: Record<string, unknown>
}

export type MessageHandler = (message: WebSocketMessage) => void

class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private handlers: Set<MessageHandler> = new Set()
  private isConnecting = false

  constructor(url: string = '') {
    this.url = url || this.getWebSocketUrl()
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/ws`
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
        resolve()
        return
      }

      this.isConnecting = true

      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          this.isConnecting = false
          this.reconnectAttempts = 0
          console.log('[WS] Connected')
          resolve()
        }

        this.ws.onclose = () => {
          this.isConnecting = false
          console.log('[WS] Disconnected')
          this.handleReconnect()
        }

        this.ws.onerror = (error) => {
          this.isConnecting = false
          console.error('[WS] Error:', error)
          reject(error)
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.notifyHandlers(message)
          } catch (e) {
            console.error('[WS] Failed to parse message:', e)
          }
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)

    setTimeout(() => {
      this.connect().catch(() => {})
    }, delay)
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  ping(): void {
    this.send({ type: 'ping' })
  }

  subscribe(projectId: string): void {
    this.send({ type: 'subscribe', project_id: projectId })
  }

  unsubscribe(): void {
    this.send({ type: 'unsubscribe' })
  }

  onMessage(handler: MessageHandler): () => void {
    this.handlers.add(handler)
    return () => this.handlers.delete(handler)
  }

  private notifyHandlers(message: WebSocketMessage): void {
    this.handlers.forEach((handler) => {
      try {
        handler(message)
      } catch (e) {
        console.error('[WS] Handler error:', e)
      }
    })
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

let wsClient: WebSocketClient | null = null

export function getWebSocketClient(): WebSocketClient {
  if (!wsClient) {
    wsClient = new WebSocketClient()
  }
  return wsClient
}

export function useWebSocket(onMessage?: MessageHandler): {
  client: WebSocketClient
  connect: () => Promise<void>
  disconnect: () => void
} {
  const client = getWebSocketClient()

  if (onMessage) {
    const unsubscribe = client.onMessage(onMessage)
    return { client, connect: () => client.connect(), disconnect: unsubscribe }
  }

  return { client, connect: () => client.connect(), disconnect: () => {} }
}

export default WebSocketClient
