interface Column {
  key: string
  label: string
  format?: (v: any) => string
}

interface Props {
  columns: Column[]
  data: Record<string, any>[]
  title?: string
}

export default function MetricsTable({ columns, data, title }: Props) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {title && <h3 className="px-4 py-3 font-semibold text-gray-900 border-b">{title}</h3>}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th key={col.key} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50">
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-2 text-sm text-gray-700 whitespace-nowrap">
                    {col.format ? col.format(row[col.key]) : row[col.key] ?? '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
