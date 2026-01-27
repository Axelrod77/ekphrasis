import { useState } from 'react'
import { usePortfolioSummary, useAddHolding, useDeleteHolding } from '../hooks/usePortfolio'
import { useStocks } from '../hooks/useStocks'
import { formatCurrency, formatPercent, pnlColor } from '../utils/format'
import PnLChart from '../components/charts/PnLChart'

export default function Portfolio() {
  const { data: portfolio, isLoading } = usePortfolioSummary()
  const addHolding = useAddHolding()
  const deleteHolding = useDeleteHolding()
  const [showForm, setShowForm] = useState(false)
  const [stockSearch, setStockSearch] = useState('')
  const { data: stockResults } = useStocks({ search: stockSearch, pageSize: 5 })

  const [form, setForm] = useState({ stock_id: '', quantity: '', buy_price: '', buy_date: '' })

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault()
    addHolding.mutate({
      stock_id: form.stock_id,
      quantity: +form.quantity,
      buy_price: +form.buy_price,
      buy_date: form.buy_date,
    })
    setForm({ stock_id: '', quantity: '', buy_price: '', buy_date: '' })
    setShowForm(false)
  }

  if (isLoading) return <div className="text-center py-12 text-gray-500">Loading...</div>

  const chartData = portfolio?.holdings?.map((h: any) => ({ name: h.stock_symbol, value: h.pnl })) || []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
        <button onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700">
          + Add Holding
        </button>
      </div>

      {portfolio && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">Total Invested</p>
            <p className="text-xl font-bold">{formatCurrency(portfolio.total_invested)}</p>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">Current Value</p>
            <p className="text-xl font-bold">{formatCurrency(portfolio.current_value)}</p>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">P&L</p>
            <p className={`text-xl font-bold ${pnlColor(portfolio.total_pnl)}`}>{formatCurrency(portfolio.total_pnl)}</p>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">Returns</p>
            <p className={`text-xl font-bold ${pnlColor(portfolio.total_pnl_percent)}`}>{formatPercent(portfolio.total_pnl_percent)}</p>
          </div>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleAdd} className="bg-white rounded-lg border p-4 space-y-3">
          <div>
            <input placeholder="Search stock..." value={stockSearch} onChange={(e) => setStockSearch(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm outline-none" />
            {stockResults?.items?.length > 0 && stockSearch && (
              <div className="border rounded mt-1 max-h-32 overflow-y-auto">
                {stockResults.items.map((s: any) => (
                  <button key={s.id} type="button" onClick={() => { setForm({...form, stock_id: s.id}); setStockSearch(s.symbol) }}
                    className="block w-full text-left px-3 py-1 text-sm hover:bg-gray-50">
                    {s.symbol} - {s.name}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="grid grid-cols-3 gap-3">
            <input placeholder="Quantity" type="number" value={form.quantity} onChange={(e) => setForm({...form, quantity: e.target.value})}
              className="px-3 py-2 border rounded-lg text-sm outline-none" required />
            <input placeholder="Buy Price" type="number" step="0.01" value={form.buy_price} onChange={(e) => setForm({...form, buy_price: e.target.value})}
              className="px-3 py-2 border rounded-lg text-sm outline-none" required />
            <input type="date" value={form.buy_date} onChange={(e) => setForm({...form, buy_date: e.target.value})}
              className="px-3 py-2 border rounded-lg text-sm outline-none" required />
          </div>
          <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm">Add</button>
        </form>
      )}

      {chartData.length > 0 && <PnLChart data={chartData} title="P&L by Stock" />}

      <div className="bg-white rounded-lg border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Qty</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Buy Price</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">CMP</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Invested</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Current</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {portfolio?.holdings?.map((h: any) => (
              <tr key={h.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium">{h.stock_symbol}</td>
                <td className="px-4 py-2 text-sm">{h.quantity}</td>
                <td className="px-4 py-2 text-sm">{formatCurrency(h.buy_price)}</td>
                <td className="px-4 py-2 text-sm">{formatCurrency(h.current_price)}</td>
                <td className="px-4 py-2 text-sm">{formatCurrency(h.invested_value)}</td>
                <td className="px-4 py-2 text-sm">{formatCurrency(h.current_value)}</td>
                <td className={`px-4 py-2 text-sm font-medium ${pnlColor(h.pnl)}`}>
                  {formatCurrency(h.pnl)} ({formatPercent(h.pnl_percent)})
                </td>
                <td className="px-4 py-2">
                  <button onClick={() => deleteHolding.mutate(h.id)} className="text-red-500 hover:text-red-700 text-sm">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
