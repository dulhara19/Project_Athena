import { useEffect, useRef, useState, useCallback } from 'react'

interface UseWebSocketOptions {
  workflowId?: string
  onMessage?: (data: any) => void
  onError?: (error: Error) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { workflowId, onMessage, onError, onConnect, onDisconnect } = options
  const [isConnected, setIsConnected] = useState(false)
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    if (socket?.readyState === WebSocket.OPEN) return

    const wsUrl = workflowId 
      ? `ws://localhost:8000/api/v1/ws/${workflowId}`
      : 'ws://localhost:8000/api/v1/ws'

    try {
      const newSocket = new WebSocket(wsUrl)

      newSocket.onopen = () => {
        setIsConnected(true)
        onConnect?.()
      }

      newSocket.onclose = () => {
        setIsConnected(false)
        onDisconnect?.()
        // Attempt reconnection
        if (workflowId) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 1000)
        }
      }

      newSocket.onerror = (error) => {
        onError?.(new Error('WebSocket error'))
      }

      newSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage?.(data)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      setSocket(newSocket)
    } catch (error) {
      onError?.(error as Error)
    }
  }, [workflowId, onMessage, onError, onConnect, onDisconnect])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (socket) {
      socket.close()
      setSocket(null)
      setIsConnected(false)
    }
  }, [socket])

  const send = useCallback((data: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data))
    }
  }, [socket])

  useEffect(() => {
    if (workflowId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [workflowId])

  return {
    socket,
    isConnected,
    connect,
    disconnect,
    send,
  }
}
