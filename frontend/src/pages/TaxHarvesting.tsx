import { useAnalyzeTaxHarvest, useTaxHarvestSummary, useUpdateRecommendation } from '../hooks/useTaxHarvest'
import { formatCurrency, pnlColor } from '../utils/format'

export default function TaxHarvesting() {
  const { data: summary, isLoading } = useTaxHarvestSummary()
  const analyze = useAnalyzeTaxHarvest()
  const updateRec = useUpdateRecommendation()

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Tax-Loss Harvesting</h1>
        <button onClick={() => analyze.mutate()}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700"
          disabled={analyze.isPending}>
          {analyze.isPending ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
        Tax rates: STCG 20% (held &lt;1 year), LTCG 12.5% (held &gt;1 year). Consider wash sale rules - avoid repurchasing the same stock within 30 days of selling for tax loss purposes.
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : summary && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg border p-4">
              <p className="text-sm text-gray-500">Total Unrealized Loss</p>
              <p className="text-xl font-bold text-loss">{formatCurrency(summary.total_unrealized_loss)}</p>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <p className="text-sm text-gray-500">Estimated Tax Saving</p>
              <p className="text-xl font-bold text-gain">{formatCurrency(summary.total_estimated_tax_saving)}</p>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <p className="text-sm text-gray-500">STCG Harvestable</p>
              <p className="text-xl font-bold">{formatCurrency(summary.stcg_harvestable)}</p>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <p className="text-sm text-gray-500">LTCG Harvestable</p>
              <p className="text-xl font-bold">{formatCurrency(summary.ltcg_harvestable)}</p>
            </div>
          </div>

          <div className="bg-white rounded-lg border overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Qty</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Buy Price</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">CMP</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Loss</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tax Saving</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {summary.recommendations?.map((r: any) => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-medium">{r.stock_symbol}</td>
                    <td className="px-4 py-2 text-sm">{r.quantity}</td>
                    <td className="px-4 py-2 text-sm">{formatCurrency(r.buy_price)}</td>
                    <td className="px-4 py-2 text-sm">{formatCurrency(r.current_price)}</td>
                    <td className="px-4 py-2 text-sm text-loss">{formatCurrency(r.unrealized_loss)}</td>
                    <td className="px-4 py-2 text-sm text-gain">{formatCurrency(r.estimated_tax_saving)}</td>
                    <td className="px-4 py-2 text-sm">
                      <span className={`px-2 py-0.5 rounded text-xs ${r.is_short_term ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'}`}>
                        {r.is_short_term ? 'STCG' : 'LTCG'}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm space-x-2">
                      <button onClick={() => updateRec.mutate({ id: r.id, status: 'acted' })}
                        className="text-green-600 hover:underline text-xs">Harvest</button>
                      <button onClick={() => updateRec.mutate({ id: r.id, status: 'dismissed' })}
                        className="text-gray-400 hover:underline text-xs">Dismiss</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
