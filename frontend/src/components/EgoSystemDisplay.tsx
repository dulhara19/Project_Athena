import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface EgoSystemDisplayProps {
  egoState?: {
    dimensions?: Record<string, Record<string, number>>
    strength?: number
    fragility?: number
    consistency?: number
  }
  dimensionImpacts?: Record<string, number>
}

export default function EgoSystemDisplay({ egoState, dimensionImpacts }: EgoSystemDisplayProps) {
  // Prepare dimension health data
  const dimensionData = egoState?.dimensions
    ? Object.entries(egoState.dimensions).map(([name, subDims]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        health: Object.values(subDims).reduce((a, b) => a + b, 0) / Object.keys(subDims).length,
      }))
    : []

  // Prepare impact data
  const impactData = dimensionImpacts
    ? Object.entries(dimensionImpacts).map(([name, impact]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        impact: Number(impact),
      }))
    : []

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow space-y-6">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Ego System</h3>

      {/* Ego Strength Meter */}
      {egoState?.strength !== undefined && (
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-600 dark:text-gray-400">Ego Strength</span>
            <span className="font-semibold">{(egoState.strength * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all"
              style={{ width: `${egoState.strength * 100}%` }}
            />
          </div>
          {egoState.consistency !== undefined && (
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Consistency: {(egoState.consistency * 100).toFixed(1)}%
            </div>
          )}
        </div>
      )}

      {/* Dimension Health */}
      {dimensionData.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Dimension Health
          </h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={dimensionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="health" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Dimension Impacts */}
      {impactData.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Current Impact
          </h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={impactData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[-1, 1]} />
              <Tooltip />
              <Bar dataKey="impact" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

