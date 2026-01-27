import { useMFAnalysis } from '../hooks/useMutualFunds'
import { formatCurrency, formatPercent, pnlColor } from '../utils/format'
import MFUploader from '../components/MFUploader'
import AllocationChart from '../components/charts/AllocationChart'

export default function MutualFunds() {
  const { data: analysis, isLoading } = useMFAnalysis()

  const allocationData = analysis?.allocation_by_category
    ? Object.entries(analysis.allocation_by_category).map(([name, value]) => ({ name, value: value as number }))
    : []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Mutual Funds</h1>

      <MFUploader />

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : analysis && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg border p-4">
              <p className="text-sm text-gray-500">Total Invested</p>
              <p className="text-xl font-bold">{formatCurrency(analysis.total_invested)}</p>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <p className="text-sm text-gray-500">Current Value</p>
              <p className="text-xl font-bold">{formatCurrency(analysis.total_current_value)}</p>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <p className="text-sm text-gray-500">Total P&L</p>
              <p className={`text-xl font-bold ${pnlColor(analysis.total_current_value - analysis.total_invested)}`}>
                {formatCurrency(analysis.total_current_value - analysis.total_invested)}
              </p>
            </div>
          </div>

          {allocationData.length > 0 && <AllocationChart data={allocationData} title="Allocation by Category" />}

          <div className="bg-white rounded-lg border overflow-hidden">
            <h3 className="px-4 py-3 font-semibold border-b">Your Holdings</h3>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Scheme</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Units</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Invested</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Current</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {analysis.holdings?.map((h: any) => (
                  <tr key={h.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm">
                      <div className="font-medium truncate max-w-[300px]">{h.scheme?.scheme_name}</div>
                      <div className="text-xs text-gray-400">{h.scheme?.category}</div>
                    </td>
                    <td className="px-4 py-2 text-sm">{h.units?.toFixed(3)}</td>
                    <td className="px-4 py-2 text-sm">{formatCurrency(h.invested_amount)}</td>
                    <td className="px-4 py-2 text-sm">{formatCurrency(h.current_value)}</td>
                    <td className={`px-4 py-2 text-sm font-medium ${pnlColor(h.pnl)}`}>{formatCurrency(h.pnl)}</td>
                    <td className="px-4 py-2 text-sm">
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        h.rating === 'good' ? 'bg-green-100 text-green-700' :
                        h.rating === 'bad' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>{h.rating || 'N/A'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {analysis.underperformers?.length > 0 && (
            <div className="bg-red-50 rounded-lg border border-red-200 p-4">
              <h3 className="font-semibold text-red-800 mb-2">Underperforming Funds</h3>
              <ul className="text-sm text-red-700 space-y-1">
                {analysis.underperformers.map((u: any) => (
                  <li key={u.id}>{u.scheme?.scheme_name} - Consider switching to a better-rated fund in the same category</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.suggestions?.length > 0 && (
            <div className="bg-green-50 rounded-lg border border-green-200 p-4">
              <h3 className="font-semibold text-green-800 mb-2">Suggested Alternatives</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {analysis.suggestions.map((s: any) => (
                  <div key={s.id} className="bg-white rounded-lg border p-3">
                    <p className="font-medium text-sm truncate">{s.scheme_name}</p>
                    <p className="text-xs text-gray-500">{s.category}</p>
                    <div className="flex justify-between mt-2 text-xs">
                      <span>5Y: {s.return_5y ? `${s.return_5y.toFixed(1)}%` : '-'}</span>
                      <span className="bg-green-100 text-green-700 px-2 rounded">{s.computed_rating}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
