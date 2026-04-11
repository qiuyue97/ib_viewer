import { useEffect, useState } from 'react'
import { useWebSocket } from './useWebSocket'
import { listCapital } from './api'
import type { CapitalInjection } from './types'
import { StatusBar } from './components/StatusBar'
import { AccountBalance } from './components/AccountBalance'
import { ExchangeRate } from './components/ExchangeRate'
import { Positions } from './components/Positions'
import { Returns } from './components/Returns'
import { CapitalManager } from './components/CapitalManager'

const WS_URL = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`

export default function App() {
  const { data, status } = useWebSocket(WS_URL)
  const [injections, setInjections] = useState<CapitalInjection[]>([])

  async function refreshCapital() {
    try {
      setInjections(await listCapital())
    } catch { /* ignore */ }
  }

  useEffect(() => { refreshCapital() }, [])

  const snap = data?.snapshot
  const ret = data?.returns
  const connError = data?.error

  return (
    <div className="min-h-screen bg-gray-100">
      <StatusBar status={status} lastUpdate={snap?.rate_timestamp} />

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">
        <h1 className="text-2xl font-bold text-gray-800">IB 账户总览</h1>

        {connError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
            {connError}
          </div>
        )}

        {snap ? (
          <>
            <AccountBalance snap={snap} />
            <ExchangeRate snap={snap} />
            <Positions positions={snap.positions} />
          </>
        ) : (
          <div className="bg-white rounded-2xl shadow p-8 text-center text-gray-400">
            {status === 'connecting' ? '正在连接 IB Gateway…' : '等待数据…'}
          </div>
        )}

        {ret && <Returns metrics={ret} />}

        <CapitalManager injections={injections} onRefresh={refreshCapital} />
      </div>
    </div>
  )
}
