import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface PainHistoryProps {
  history?: Array<{ user_query: string; pain_status: number; timestamp?: string }>
}

export default function PainHistory({ history }: PainHistoryProps) {
  if (!history || history.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Pain History</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2">No history data available</p>
      </div>
    )
  }

  const chartData = history.map((entry, idx) => ({
    index: idx + 1,
    pain: entry.pain_status,
    label: entry.user_query.length > 20 
      ? entry.user_query.substring(0, 20) + '...' 
      : entry.user_query,
  }))

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Pain History</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="index" 
              label={{ value: 'Interaction', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              domain={[-1, 1]}
              label={{ value: 'Pain Level', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              formatter={(value: number) => value.toFixed(2)}
              labelFormatter={(label) => `Interaction ${label}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="pain"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Pain Level"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

