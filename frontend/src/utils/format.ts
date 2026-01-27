export function formatCurrency(value: number | null | undefined): string {
  if (value == null) return '-'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value)
}

export function formatNumber(value: number | null | undefined, decimals = 2): string {
  if (value == null) return '-'
  return value.toFixed(decimals)
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return '-'
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}

export function formatMarketCap(value: number | null | undefined): string {
  if (value == null) return '-'
  if (value >= 100000) return `${(value / 100000).toFixed(0)} L Cr`
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K Cr`
  return `${value.toFixed(0)} Cr`
}

export function pnlColor(value: number | null | undefined): string {
  if (value == null) return 'text-gray-500'
  return value >= 0 ? 'text-gain' : 'text-loss'
}
