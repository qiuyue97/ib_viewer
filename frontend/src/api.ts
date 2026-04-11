import type { CapitalInjection } from './types'

const BASE = '/api'

export async function listCapital(): Promise<CapitalInjection[]> {
  const r = await fetch(`${BASE}/capital`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function addCapital(body: { amount_cny: number; injected_on: string; note: string }): Promise<CapitalInjection> {
  const r = await fetch(`${BASE}/capital`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function deleteCapital(id: number): Promise<void> {
  const r = await fetch(`${BASE}/capital/${id}`, { method: 'DELETE' })
  if (!r.ok) throw new Error(await r.text())
}
