import { useState } from 'react'
import { useStocks, useSearchScrape } from '../hooks/useStocks'
import { Link } from 'react-router-dom'
import { formatCurrency, formatNumber, formatMarketCap } from '../utils/format'

export default function StockScreener() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [sortBy, setSortBy] = useState('market_cap')
  const [sortOrder, setSortOrder] = useState('desc')
  const [minRoce, setMinRoce] = useState<number | undefined>()
  const [maxPe, setMaxPe] = useState<number | undefined>()
  const [maxDe, setMaxDe] = useState<number | undefined>()

  const { data, isLoading } = useStocks({ page, search, sortBy, sortOrder, minRoce, maxPe, maxDebtToEquity: maxDe })
  const searchScrape = useSearchScrape()

  const toggleSort = (col: string) => {
    if (sortBy === col) setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    else { setSortBy(col); setSortOrder('desc') }
  }

  const handleScrape = () => {
    if (!search.trim()) return
    searchScrape.mutate(search.trim())
  }

  const showScrapeButton = search.trim() && !isLoading && data?.total === 0

  const SortHeader = ({ col, label }: { col: string; label: string }) => (
    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:text-gray-700"
        onClick={() => toggleSort(col)}>
      {label} {sortBy === col && (sortOrder === 'asc' ? ' ^' : ' v')}
    </th>
  )

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Stock Screener</h1>
      <div className="flex flex-wrap gap-3">
        <input placeholder="Search stocks..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-64 outline-none focus:ring-2 focus:ring-primary-500" />
        <input placeholder="Min ROCE %" type="number" value={minRoce ?? ''} onChange={(e) => setMinRoce(e.target.value ? +e.target.value : undefined)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-32 outline-none" />
        <input placeholder="Max PE" type="number" value={maxPe ?? ''} onChange={(e) => setMaxPe(e.target.value ? +e.target.value : undefined)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-32 outline-none" />
        <input placeholder="Max D/E" type="number" value={maxDe ?? ''} onChange={(e) => setMaxDe(e.target.value ? +e.target.value : undefined)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-32 outline-none" />
      </div>

      {showScrapeButton && (
        <div className="flex items-center gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
          <span className="text-yellow-800">No stocks found for "{search}".</span>
          <button
            onClick={handleScrape}
            disabled={searchScrape.isPending}
            className="px-3 py-1.5 bg-primary-600 text-white rounded-md text-sm hover:bg-primary-700 disabled:opacity-50"
          >
            {searchScrape.isPending ? 'Fetching...' : 'Fetch from Screener.in'}
          </button>
          {searchScrape.isError && (
            <span className="text-red-600">Could not find this stock on screener.in</span>
          )}
        </div>
      )}

      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <SortHeader col="current_price" label="Price" />
                <SortHeader col="market_cap" label="MCap" />
                <SortHeader col="pe_ratio" label="PE" />
                <SortHeader col="roce" label="ROCE" />
                <SortHeader col="roe" label="ROE" />
                <SortHeader col="dividend_yield" label="Div Yield" />
                <SortHeader col="promoter_holding" label="Promoter %" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                <tr><td colSpan={8} className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>
              ) : data?.items?.map((s: any) => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <Link to={`/stocks/${s.symbol}`} className="text-primary-600 hover:underline font-medium">{s.symbol}</Link>
                    <div className="text-xs text-gray-400 truncate max-w-[150px]">{s.name}</div>
                  </td>
                  <td className="px-4 py-2 text-sm">{formatCurrency(s.current_price)}</td>
                  <td className="px-4 py-2 text-sm">{formatMarketCap(s.market_cap)}</td>
                  <td className="px-4 py-2 text-sm">{formatNumber(s.pe_ratio)}</td>
                  <td className="px-4 py-2 text-sm">{s.roce ? `${formatNumber(s.roce)}%` : '-'}</td>
                  <td className="px-4 py-2 text-sm">{s.roe ? `${formatNumber(s.roe)}%` : '-'}</td>
                  <td className="px-4 py-2 text-sm">{s.dividend_yield ? `${formatNumber(s.dividend_yield)}%` : '-'}</td>
                  <td className="px-4 py-2 text-sm">{s.promoter_holding ? `${formatNumber(s.promoter_holding)}%` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data && (
          <div className="flex justify-between items-center px-4 py-3 border-t bg-gray-50 text-sm text-gray-500">
            <span>Showing {data.items?.length} of {data.total} stocks</span>
            <div className="space-x-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                className="px-3 py-1 border rounded hover:bg-white disabled:opacity-50">Prev</button>
              <span>Page {data.page}</span>
              <button onClick={() => setPage(p => p + 1)} disabled={data.items?.length < 20}
                className="px-3 py-1 border rounded hover:bg-white disabled:opacity-50">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
