import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts'

interface MBTIDisplayProps {
  mbti?: {
    mbti?: string
    axis_scores?: Record<string, number>
    confidence?: number
  }
}

export default function MBTIDisplay({ mbti }: MBTIDisplayProps) {
  if (!mbti) return null

  const axisScores = mbti.axis_scores || {}
  
  const radarData = [
    {
      axis: 'E',
      score: axisScores.E || 0.5,
    },
    {
      axis: 'I',
      score: axisScores.I || 0.5,
    },
    {
      axis: 'S',
      score: axisScores.S || 0.5,
    },
    {
      axis: 'N',
      score: axisScores.N || 0.5,
    },
    {
      axis: 'T',
      score: axisScores.T || 0.5,
    },
    {
      axis: 'F',
      score: axisScores.F || 0.5,
    },
    {
      axis: 'J',
      score: axisScores.J || 0.5,
    },
    {
      axis: 'P',
      score: axisScores.P || 0.5,
    },
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">MBTI Personality</h3>
      
      {mbti.mbti && (
        <div className="text-center mb-4">
          <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{mbti.mbti}</div>
          {mbti.confidence !== undefined && (
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Confidence: {(mbti.confidence * 100).toFixed(1)}%
            </div>
          )}
        </div>
      )}

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="axis" />
            <PolarRadiusAxis angle={90} domain={[0, 1]} />
            <Radar
              name="MBTI Scores"
              dataKey="score"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.6}
            />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

