import { useParams } from 'react-router-dom'
import { useStockDetail } from '../hooks/useStocks'
import { useAddToWatchlist } from '../hooks/useWatchlist'
import { formatCurrency, formatNumber, formatMarketCap } from '../utils/format'
import MetricsTable from '../components/MetricsTable'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function StockDetail() {
  const { symbol } = useParams<{ symbol: string }>()
  const { data: stock, isLoading } = useStockDetail(symbol || '')
  const addToWatchlist = useAddToWatchlist()

  if (isLoading) return <div className="text-center py-12 text-gray-500">Loading...</div>
  if (!stock) return <div className="text-center py-12 text-gray-500">Stock not found</div>

  const ratios = [
    { label: 'Market Cap', value: formatMarketCap(stock.market_cap) },
    { label: 'Current Price', value: formatCurrency(stock.current_price) },
    { label: '52W High / Low', value: `${formatCurrency(stock.high_52w)} / ${formatCurrency(stock.low_52w)}` },
    { label: 'P/E Ratio', value: formatNumber(stock.pe_ratio) },
    { label: 'P/B Ratio', value: formatNumber(stock.pb_ratio) },
    { label: 'ROCE', value: stock.roce ? `${formatNumber(stock.roce)}%` : '-' },
    { label: 'ROE', value: stock.roe ? `${formatNumber(stock.roe)}%` : '-' },
    { label: 'Debt/Equity', value: formatNumber(stock.debt_to_equity) },
    { label: 'Dividend Yield', value: stock.dividend_yield ? `${formatNumber(stock.dividend_yield)}%` : '-' },
    { label: 'EPS', value: formatNumber(stock.eps) },
    { label: 'Book Value', value: formatNumber(stock.book_value) },
    { label: 'Promoter Holding', value: stock.promoter_holding ? `${formatNumber(stock.promoter_holding)}%` : '-' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{stock.symbol}</h1>
          <p className="text-gray-500">{stock.name}</p>
          {stock.sector && <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded mt-1 inline-block">{stock.sector}</span>}
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-3xl font-bold">{formatCurrency(stock.current_price)}</span>
          <button onClick={() => addToWatchlist.mutate({ stock_id: stock.id })}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700">
            + Watchlist
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {ratios.map((r) => (
          <div key={r.label} className="bg-white rounded-lg border p-3">
            <p className="text-xs text-gray-500">{r.label}</p>
            <p className="font-semibold text-gray-900">{r.value}</p>
          </div>
        ))}
      </div>

      {stock.pros && (
        <div className="bg-green-50 rounded-lg border border-green-200 p-4">
          <h3 className="font-semibold text-green-800 mb-2">Strengths</h3>
          <ul className="list-disc list-inside text-sm text-green-700 space-y-1">
            {stock.pros.split('\n').map((p: string, i: number) => <li key={i}>{p}</li>)}
          </ul>
        </div>
      )}
      {stock.cons && (
        <div className="bg-red-50 rounded-lg border border-red-200 p-4">
          <h3 className="font-semibold text-red-800 mb-2">Weaknesses</h3>
          <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
            {stock.cons.split('\n').map((c: string, i: number) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      )}

      {stock.quarterly_results?.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Quarterly Results</h2>
          <div className="bg-white rounded-lg border p-4 mb-4">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={stock.quarterly_results.slice(-8)}>
                <XAxis dataKey="quarter" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" />
                <Bar dataKey="net_profit" fill="#10b981" name="Net Profit" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <MetricsTable
            columns={[
              { key: 'quarter', label: 'Quarter' },
              { key: 'revenue', label: 'Revenue', format: (v: number) => formatCurrency(v) },
              { key: 'net_profit', label: 'Net Profit', format: (v: number) => formatCurrency(v) },
              { key: 'eps', label: 'EPS', format: (v: number) => formatNumber(v) },
              { key: 'opm_percent', label: 'OPM %', format: (v: number) => v ? `${formatNumber(v)}%` : '-' },
            ]}
            data={stock.quarterly_results}
          />
        </div>
      )}

      {stock.shareholding_patterns?.length > 0 && (
        <MetricsTable
          title="Shareholding Pattern"
          columns={[
            { key: 'quarter', label: 'Quarter' },
            { key: 'promoter_percent', label: 'Promoter %', format: (v: number) => formatNumber(v) },
            { key: 'fii_percent', label: 'FII %', format: (v: number) => formatNumber(v) },
            { key: 'dii_percent', label: 'DII %', format: (v: number) => formatNumber(v) },
            { key: 'public_percent', label: 'Public %', format: (v: number) => formatNumber(v) },
          ]}
          data={stock.shareholding_patterns}
        />
      )}

      {stock.peers?.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Peer Comparison</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {stock.peers.map((p: any) => (
              <div key={p.id} className="bg-white rounded-lg border p-3">
                <p className="font-medium text-primary-600">{p.symbol}</p>
                <p className="text-xs text-gray-500">{p.name}</p>
                <div className="flex justify-between mt-2 text-sm">
                  <span>PE: {formatNumber(p.pe_ratio)}</span>
                  <span>ROCE: {p.roce ? `${formatNumber(p.roce)}%` : '-'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {stock.about && (
        <div className="bg-white rounded-lg border p-4">
          <h3 className="font-semibold text-gray-900 mb-2">About</h3>
          <p className="text-sm text-gray-600">{stock.about}</p>
        </div>
      )}
    </div>
  )
}
