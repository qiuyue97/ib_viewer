import type { WsStatus } from '../useWebSocket'

const colors: Record<WsStatus, string> = {
  connecting: 'bg-yellow-400',
  connected: 'bg-green-500',
  disconnected: 'bg-red-500',
}
const labels: Record<WsStatus, string> = {
  connecting: '连接中…',
  connected: '实时连接',
  disconnected: '已断开，重连中…',
}

export function StatusBar({ status, lastUpdate }: { status: WsStatus; lastUpdate?: string }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white text-sm">
      <span className={`w-2.5 h-2.5 rounded-full ${colors[status]}`} />
      <span>{labels[status]}</span>
      {lastUpdate && <span className="ml-auto text-gray-400">更新于 {new Date(lastUpdate).toLocaleTimeString('zh-CN')}</span>}
    </div>
  )
}
