import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface Props {
  data: { name: string; value: number }[]
  title?: string
}

export default function PnLChart({ data, title }: Props) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {title && <h3 className="font-semibold text-gray-900 mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value">
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.value >= 0 ? '#16a34a' : '#dc2626'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
