export interface Position {
  symbol: string
  sec_type: string
  currency: string
  quantity: number
  avg_cost: number
  market_price: number
  market_value: number
  market_value_cny: number
}

export interface AccountSnapshot {
  cash_usd: number       // actual USD cash held
  cash_cnh: number       // actual CNH (offshore CNY) cash held
  cash_cny: number       // total cash in CNY = cash_cnh + cash_usd * rate
  usdcnh_rate: number
  positions: Position[]
  total_value_cny: number
  rate_timestamp: string
}

export interface ReturnMetrics {
  total_return_pct: number
  annualized_return_pct: number | null
  total_invested_cny: number
  current_value_cny: number
}

export interface CapitalInjection {
  id: number
  amount_cny: number
  injected_on: string
  note: string
}

export interface WsPayload {
  snapshot?: AccountSnapshot
  returns?: ReturnMetrics
  error?: string
}
