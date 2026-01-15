import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface EmotionDisplayProps {
  emotions?: Record<string, number>
  painLevel?: number
  vad?: { valence: number; arousal: number; dominance: number }
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']

export default function EmotionDisplay({ emotions, painLevel, vad }: EmotionDisplayProps) {
  // Prepare data for pie chart
  const emotionData = emotions
    ? Object.entries(emotions)
        .map(([name, value]) => ({ name, value: Number(value) }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 6)
    : []

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Emotion Analysis</h3>
      
      {painLevel !== undefined && (
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Pain Level</span>
            <span className="font-semibold">{painLevel.toFixed(2)}</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                painLevel > 0 ? 'bg-green-500' : painLevel < 0 ? 'bg-red-500' : 'bg-gray-400'
              }`}
              style={{
                width: `${Math.abs(painLevel) * 100}%`,
                marginLeft: painLevel < 0 ? 'auto' : '0',
              }}
            />
          </div>
        </div>
      )}

      {vad && (
        <div className="mb-4 grid grid-cols-3 gap-2 text-sm">
          <div className="text-center">
            <div className="text-gray-600 dark:text-gray-400">Valence</div>
            <div className="font-semibold">{vad.valence.toFixed(2)}</div>
          </div>
          <div className="text-center">
            <div className="text-gray-600 dark:text-gray-400">Arousal</div>
            <div className="font-semibold">{vad.arousal.toFixed(2)}</div>
          </div>
          <div className="text-center">
            <div className="text-gray-600 dark:text-gray-400">Dominance</div>
            <div className="font-semibold">{vad.dominance.toFixed(2)}</div>
          </div>
        </div>
      )}

      {emotionData.length > 0 && (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={emotionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {emotionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

