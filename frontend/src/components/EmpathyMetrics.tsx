import { RadialBarChart, RadialBar, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface EmpathyMetricsProps {
  empathyMetrics?: {
    empathy?: number
    alignment?: number
    same_direction?: number
    confidence?: number
  }
  userPain?: number
  athenaPain?: number
}

export default function EmpathyMetrics({ empathyMetrics, userPain, athenaPain }: EmpathyMetricsProps) {
  if (!empathyMetrics) return null

  const gaugeData = [
    {
      name: 'Empathy',
      value: (empathyMetrics.empathy || 0) * 100,
      fill: '#3b82f6',
    },
    {
      name: 'Alignment',
      value: (empathyMetrics.alignment || 0) * 100,
      fill: '#10b981',
    },
    {
      name: 'Confidence',
      value: (empathyMetrics.confidence || 0) * 100,
      fill: '#f59e0b',
    },
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Empathy Metrics</h3>

      {/* Pain Comparison */}
      {userPain !== undefined && athenaPain !== undefined && (
        <div className="mb-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">User Pain</div>
              <div className={`text-2xl font-bold ${userPain > 0 ? 'text-green-600' : userPain < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {userPain > 0 ? '+' : ''}{userPain.toFixed(2)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Athena Pain</div>
              <div className={`text-2xl font-bold ${athenaPain > 0 ? 'text-green-600' : athenaPain < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {athenaPain > 0 ? '+' : ''}{athenaPain.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empathy Gauge */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="20%"
            outerRadius="80%"
            barSize={10}
            data={gaugeData}
            startAngle={90}
            endAngle={-270}
          >
            <RadialBar
              minAngle={15}
              label={{ position: 'insideStart', fill: '#fff' }}
              background
              dataKey="value"
            />
            <Legend
              iconSize={10}
              layout="vertical"
              verticalAlign="middle"
              align="right"
            />
            <Tooltip />
          </RadialBarChart>
        </ResponsiveContainer>
      </div>

      {/* Metrics Breakdown */}
      <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
        <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
          <div className="text-gray-600 dark:text-gray-400">Empathy</div>
          <div className="font-semibold text-blue-600 dark:text-blue-400">
            {(empathyMetrics.empathy || 0).toFixed(2)}
          </div>
        </div>
        <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded">
          <div className="text-gray-600 dark:text-gray-400">Alignment</div>
          <div className="font-semibold text-green-600 dark:text-green-400">
            {(empathyMetrics.alignment || 0).toFixed(2)}
          </div>
        </div>
        <div className="text-center p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
          <div className="text-gray-600 dark:text-gray-400">Confidence</div>
          <div className="font-semibold text-yellow-600 dark:text-yellow-400">
            {(empathyMetrics.confidence || 0).toFixed(2)}
          </div>
        </div>
        <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
          <div className="text-gray-600 dark:text-gray-400">Direction Match</div>
          <div className="font-semibold text-purple-600 dark:text-purple-400">
            {empathyMetrics.same_direction ? 'Yes' : 'No'}
          </div>
        </div>
      </div>
    </div>
  )
}

