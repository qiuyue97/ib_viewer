import type { Position } from '../types'

function fmt(n: number) {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function Positions({ positions }: { positions: Position[] }) {
  if (positions.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow p-5">
        <h2 className="text-lg font-semibold text-gray-700 mb-2">持仓明细</h2>
        <p className="text-gray-400 text-sm">暂无持仓</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow p-5">
      <h2 className="text-lg font-semibold text-gray-700 mb-4">持仓明细</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 border-b text-left">
              <th className="pb-2 pr-3">标的</th>
              <th className="pb-2 pr-3 text-right">数量</th>
              <th className="pb-2 pr-3 text-right">现价</th>
              <th className="pb-2 pr-3 text-right">市值</th>
              <th className="pb-2 text-right">折合人民币</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((p) => (
              <tr key={p.symbol} className="border-b last:border-0">
                <td className="py-2 pr-3 font-medium">{p.symbol}<span className="ml-1 text-gray-400 text-xs">{p.sec_type}</span></td>
                <td className="py-2 pr-3 text-right">{p.quantity}</td>
                <td className="py-2 pr-3 text-right">{p.currency} {fmt(p.market_price)}</td>
                <td className="py-2 pr-3 text-right">{p.currency} {fmt(p.market_value)}</td>
                <td className="py-2 text-right font-semibold text-blue-600">¥ {fmt(p.market_value_cny)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
