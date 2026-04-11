import { useState } from 'react'
import type { CapitalInjection } from '../types'
import { addCapital, deleteCapital } from '../api'

function fmt(n: number) {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

export function CapitalManager({
  injections,
  onRefresh,
}: {
  injections: CapitalInjection[]
  onRefresh: () => void
}) {
  const [amount, setAmount] = useState('')
  const [date, setDate] = useState('')
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAdd() {
    if (!amount || !date) { setError('请填写金额和日期'); return }
    setLoading(true); setError('')
    try {
      await addCapital({ amount_cny: parseFloat(amount), injected_on: date, note })
      setAmount(''); setDate(''); setNote('')
      onRefresh()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('确认删除这笔注入记录？')) return
    await deleteCapital(id)
    onRefresh()
  }

  return (
    <div className="bg-white rounded-2xl shadow p-5 space-y-4">
      <h2 className="text-lg font-semibold text-gray-700">资金注入记录</h2>

      {/* Add form */}
      <div className="flex flex-wrap gap-2 items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">金额 (CNY)</label>
          <input
            type="number"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            placeholder="100000"
            className="border rounded-lg px-3 py-2 text-sm w-32 focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">注入日期</label>
          <input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">备注（可选）</label>
          <input
            type="text"
            value={note}
            onChange={e => setNote(e.target.value)}
            placeholder="首次注入"
            className="border rounded-lg px-3 py-2 text-sm w-28 focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
        <button
          onClick={handleAdd}
          disabled={loading}
          className="bg-blue-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '添加中…' : '添加'}
        </button>
      </div>
      {error && <p className="text-red-500 text-sm">{error}</p>}

      {/* List */}
      {injections.length === 0 ? (
        <p className="text-gray-400 text-sm">暂无记录</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 border-b text-left">
              <th className="pb-2 pr-3">日期</th>
              <th className="pb-2 pr-3 text-right">金额 (CNY)</th>
              <th className="pb-2 pr-3">备注</th>
              <th className="pb-2" />
            </tr>
          </thead>
          <tbody>
            {injections.map(inj => (
              <tr key={inj.id} className="border-b last:border-0">
                <td className="py-2 pr-3">{inj.injected_on}</td>
                <td className="py-2 pr-3 text-right font-medium">¥ {fmt(inj.amount_cny)}</td>
                <td className="py-2 pr-3 text-gray-500">{inj.note}</td>
                <td className="py-2 text-right">
                  <button
                    onClick={() => handleDelete(inj.id)}
                    className="text-red-400 hover:text-red-600 text-xs"
                  >
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
