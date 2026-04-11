import type { AccountSnapshot } from '../types'

export function ExchangeRate({ snap }: { snap: AccountSnapshot }) {
  return (
    <div className="bg-white rounded-2xl shadow p-5 flex justify-between items-center">
      <div>
        <h2 className="text-lg font-semibold text-gray-700">USD / CNH 汇率</h2>
        <p className="text-gray-400 text-xs mt-1">{new Date(snap.rate_timestamp).toLocaleString('zh-CN')}</p>
      </div>
      <span className="text-3xl font-extrabold text-orange-500">{snap.usdcnh_rate.toFixed(4)}</span>
    </div>
  )
}
