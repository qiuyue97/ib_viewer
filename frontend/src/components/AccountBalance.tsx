import type { AccountSnapshot } from '../types'

function fmt(n: number, decimals = 2) {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export function AccountBalance({ snap }: { snap: AccountSnapshot }) {
  return (
    <div className="bg-white rounded-2xl shadow p-5 space-y-3">
      <h2 className="text-lg font-semibold text-gray-700">账户余额</h2>
      <div className="flex justify-between items-baseline">
        <span className="text-gray-500 text-sm">现金 (USD)</span>
        <span className="text-xl font-bold">$ {fmt(snap.cash_usd)}</span>
      </div>
      <div className="flex justify-between items-baseline">
        <span className="text-gray-500 text-sm">现金折合人民币</span>
        <span className="text-xl font-bold text-blue-600">¥ {fmt(snap.cash_cny)}</span>
      </div>
      <div className="flex justify-between items-baseline border-t pt-3">
        <span className="text-gray-500 text-sm font-medium">总资产 (人民币)</span>
        <span className="text-2xl font-extrabold text-green-600">¥ {fmt(snap.total_value_cny)}</span>
      </div>
    </div>
  )
}
