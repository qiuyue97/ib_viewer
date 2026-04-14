import type { AccountSnapshot } from '../types'

function fmt(n: number, decimals = 2) {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export function AccountBalance({ snap }: { snap: AccountSnapshot }) {
  return (
    <div className="bg-white rounded-2xl shadow p-5 space-y-3">
      <h2 className="text-lg font-semibold text-gray-700">账户总资产</h2>

      {/* Total value — prominent */}
      <div className="text-right">
        <span className="text-3xl font-extrabold text-green-600">
          ¥ {fmt(snap.total_value_cny)}
        </span>
      </div>

      {/* Cash breakdown — always show both currencies */}
      <div className="border-t pt-2 space-y-1">
        <div className="flex justify-between items-baseline">
          <span className="text-gray-400 text-xs">现金余额</span>
          <span className="text-gray-500 text-sm space-x-4">
            <span>{fmt(snap.cash_usd)}<span className="text-gray-400 text-xs ml-0.5">（美元）</span></span>
            <span>{fmt(snap.cash_cnh)}<span className="text-gray-400 text-xs ml-0.5">（人民币）</span></span>
          </span>
        </div>
      </div>
    </div>
  )
}
