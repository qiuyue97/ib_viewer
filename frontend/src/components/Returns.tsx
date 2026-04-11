import type { ReturnMetrics } from '../types'

function fmtPct(n: number | null) {
  if (n === null) return '—'
  const sign = n >= 0 ? '+' : ''
  return `${sign}${n.toFixed(2)}%`
}

function color(n: number | null) {
  if (n === null) return 'text-gray-500'
  return n >= 0 ? 'text-green-600' : 'text-red-500'
}

function fmt(n: number) {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function Returns({ metrics }: { metrics: ReturnMetrics }) {
  return (
    <div className="bg-white rounded-2xl shadow p-5 space-y-3">
      <h2 className="text-lg font-semibold text-gray-700">收益分析</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded-xl p-4 text-center">
          <p className="text-gray-400 text-xs mb-1">总收益</p>
          <p className={`text-2xl font-extrabold ${color(metrics.total_return_pct)}`}>
            {fmtPct(metrics.total_return_pct)}
          </p>
        </div>
        <div className="bg-gray-50 rounded-xl p-4 text-center">
          <p className="text-gray-400 text-xs mb-1">年化收益率</p>
          <p className={`text-2xl font-extrabold ${color(metrics.annualized_return_pct)}`}>
            {fmtPct(metrics.annualized_return_pct)}
          </p>
        </div>
      </div>
      <div className="flex justify-between text-sm text-gray-500 pt-1">
        <span>累计投入</span>
        <span className="font-medium text-gray-700">¥ {fmt(metrics.total_invested_cny)}</span>
      </div>
      <div className="flex justify-between text-sm text-gray-500">
        <span>当前总值</span>
        <span className="font-medium text-gray-700">¥ {fmt(metrics.current_value_cny)}</span>
      </div>
    </div>
  )
}
