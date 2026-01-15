import { useEffect, useState } from 'react'
import { metricsApi, egoApi } from '../services/api'
import EgoSystemDisplay from '../components/EgoSystemDisplay'
import EmpathyMetrics from '../components/EmpathyMetrics'
import PainHistory from '../components/PainHistory'
import MBTIDisplay from '../components/MBTIDisplay'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)
  const [egoState, setEgoState] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [metricsData, egoData] = await Promise.all([
        metricsApi.getMetrics(),
        egoApi.getEgoState(),
      ])
      setMetrics(metricsData)
      setEgoState(egoData)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Research Dashboard</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Ego System */}
          <div className="lg:col-span-2">
            <EgoSystemDisplay egoState={egoState} />
          </div>

          {/* Empathy Metrics */}
          <div>
            <EmpathyMetrics empathyMetrics={metrics?.empathy_metrics} />
          </div>

          {/* MBTI Display */}
          <div>
            <MBTIDisplay mbti={metrics?.mbti} />
          </div>

          {/* Pain History */}
          <div className="lg:col-span-2">
            <PainHistory history={[]} />
          </div>
        </div>

        {/* Metrics Summary */}
        {metrics && (
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-white">System Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-600 dark:text-gray-400">Interactions</div>
                <div className="text-2xl font-bold text-blue-600">{metrics.interaction_count || 0}</div>
              </div>
              <div>
                <div className="text-gray-600 dark:text-gray-400">Ego Strength</div>
                <div className="text-2xl font-bold text-green-600">
                  {egoState?.ego_strength ? (egoState.ego_strength * 100).toFixed(1) + '%' : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-gray-600 dark:text-gray-400">Consistency</div>
                <div className="text-2xl font-bold text-purple-600">
                  {egoState?.consistency ? (egoState.consistency * 100).toFixed(1) + '%' : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-gray-600 dark:text-gray-400">Trend</div>
                <div className="text-2xl font-bold text-orange-600 capitalize">
                  {egoState?.evolution_trend || 'N/A'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

