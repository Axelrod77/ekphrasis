import { useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import { usePortfolioSummary } from '../hooks/usePortfolio'
import { useWatchlist } from '../hooks/useWatchlist'
import { formatCurrency, formatPercent, pnlColor } from '../utils/format'
import { Link } from 'react-router-dom'
import StockCard from '../components/StockCard'

export default function Dashboard() {
  const fetchUser = useAuthStore((s) => s.fetchUser)
  const user = useAuthStore((s) => s.user)
  const { data: portfolio } = usePortfolioSummary()
  const { data: watchlist } = useWatchlist()

  useEffect(() => { fetchUser() }, [fetchUser])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        Welcome{user ? `, ${user.full_name}` : ''}
      </h1>

      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">Total Invested</p>
            <p className="text-xl font-bold">{formatCurrency(portfolio.total_invested)}</p>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">Current Value</p>
            <p className="text-xl font-bold">{formatCurrency(portfolio.current_value)}</p>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">Total P&L</p>
            <p className={`text-xl font-bold ${pnlColor(portfolio.total_pnl)}`}>
              {formatCurrency(portfolio.total_pnl)}
            </p>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <p className="text-sm text-gray-500">Returns</p>
            <p className={`text-xl font-bold ${pnlColor(portfolio.total_pnl_percent)}`}>
              {formatPercent(portfolio.total_pnl_percent)}
            </p>
          </div>
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-semibold text-gray-900">Watchlist</h2>
          <Link to="/stocks" className="text-sm text-primary-600 hover:underline">Browse Stocks</Link>
        </div>
        {watchlist && watchlist.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {watchlist.map((w: any) => (
              <StockCard key={w.id} stock={w.stock} />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg border p-8 text-center text-gray-500">
            No stocks in watchlist. <Link to="/stocks" className="text-primary-600 hover:underline">Add some</Link>
          </div>
        )}
      </div>
    </div>
  )
}
