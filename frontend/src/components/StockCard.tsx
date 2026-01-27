import { Link } from 'react-router-dom'
import { formatCurrency, formatNumber, formatMarketCap } from '../utils/format'

interface Props {
  stock: {
    symbol: string
    name: string
    current_price?: number
    market_cap?: number
    pe_ratio?: number
    roce?: number
    roe?: number
  }
}

export default function StockCard({ stock }: Props) {
  return (
    <Link
      to={`/stocks/${stock.symbol}`}
      className="block bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-gray-900">{stock.symbol}</h3>
          <p className="text-xs text-gray-500 truncate max-w-[180px]">{stock.name}</p>
        </div>
        <span className="text-lg font-bold">{formatCurrency(stock.current_price)}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
        <div>MCap: {formatMarketCap(stock.market_cap)}</div>
        <div>PE: {formatNumber(stock.pe_ratio)}</div>
        <div>ROCE: {formatNumber(stock.roce)}%</div>
        <div>ROE: {formatNumber(stock.roe)}%</div>
      </div>
    </Link>
  )
}
