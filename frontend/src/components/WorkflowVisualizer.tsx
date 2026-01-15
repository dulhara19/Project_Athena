import { useWorkflow } from '../context/WorkflowContext'

const STEP_NAMES: Record<string, string> = {
  emotion_analysis: 'Emotion Analysis',
  user_pain_calculation: 'User Pain Calculation',
  mbti_detection: 'MBTI Detection',
  ego_impact_analysis: 'Ego Impact Analysis',
  athena_pain_calculation: 'Athena Pain Calculation',
  empathy_metrics: 'Empathy Metrics',
  response_generation: 'Response Generation',
  personality_adaptation: 'Personality Adaptation',
  crisis_check: 'Crisis Check',
}

export default function WorkflowVisualizer() {
  const { state } = useWorkflow()

  const getStepStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500'
      case 'processing':
        return 'bg-blue-500 animate-pulse'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-300 dark:bg-gray-600'
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 h-[800px] flex flex-col">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">
        Workflow Visualization
      </h2>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>Progress</span>
          <span>{Math.round(state.progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${state.progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="flex-1 overflow-y-auto space-y-3">
        {Array.from({ length: 9 }, (_, i) => i + 1).map((stepNum) => {
          const step = state.steps.find(s => s.step_number === stepNum)
          const stepName = step?.step_name || `step_${stepNum}`
          const status = step?.status || 'pending'
          const displayName = STEP_NAMES[stepName] || stepName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

          return (
            <div
              key={stepNum}
              className={`p-4 rounded-lg border-2 transition-all ${
                status === 'completed'
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                  : status === 'processing'
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : status === 'error'
                  ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${getStepStatusColor(status)}`} />
                  <span className="font-semibold text-gray-800 dark:text-white">
                    {stepNum}. {displayName}
                  </span>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {status}
                </span>
              </div>

              {step?.data && (
                <div className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  {step.data.message && <p>{step.data.message}</p>}
                  {step.data.pain_level !== undefined && (
                    <p>Pain Level: {step.data.pain_level.toFixed(2)}</p>
                  )}
                  {step.data.mbti && (
                    <p>MBTI: {step.data.mbti.mbti || 'Detecting...'}</p>
                  )}
                  {step.data.dimension_impacts && (
                    <div className="mt-2">
                      <p className="font-medium">Ego Dimension Impacts:</p>
                      <ul className="list-disc list-inside ml-2">
                        {Object.entries(step.data.dimension_impacts).map(([dim, impact]: [string, any]) => (
                          <li key={dim}>
                            {dim}: {impact > 0 ? '+' : ''}{impact.toFixed(2)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {step?.error && (
                <div className="mt-2 text-sm text-red-600 dark:text-red-400">
                  Error: {step.error}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Current Step Indicator */}
      {state.currentStep > 0 && (
        <div className="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            Current Step: {state.currentStep} of 9
          </p>
        </div>
      )}
    </div>
  )
}

