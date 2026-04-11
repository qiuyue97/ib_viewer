import { useEffect, useRef, useState } from 'react'
import type { WsPayload } from './types'

export type WsStatus = 'connecting' | 'connected' | 'disconnected'

export function useWebSocket(url: string) {
  const [data, setData] = useState<WsPayload | null>(null)
  const [status, setStatus] = useState<WsStatus>('connecting')
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    function connect() {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => setStatus('connected')
      ws.onmessage = (e) => {
        try {
          setData(JSON.parse(e.data) as WsPayload)
        } catch { /* ignore parse errors */ }
      }
      ws.onclose = () => {
        setStatus('disconnected')
        // reconnect after 5s
        setTimeout(connect, 5000)
      }
      ws.onerror = () => ws.close()
    }

    connect()
    return () => wsRef.current?.close()
  }, [url])

  return { data, status }
}
