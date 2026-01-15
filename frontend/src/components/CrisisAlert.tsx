interface CrisisAlertProps {
  crisisData?: {
    crisis_mode?: boolean
    crisis_response?: string
  }
}

export default function CrisisAlert({ crisisData }: CrisisAlertProps) {
  if (!crisisData?.crisis_mode) return null

  return (
    <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/30 border-2 border-red-500 rounded-lg">
      <div className="flex items-center space-x-2 mb-2">
        <span className="text-2xl">🛑</span>
        <h4 className="text-lg font-bold text-red-800 dark:text-red-200">Crisis Mode Activated</h4>
      </div>
      <p className="text-sm text-red-700 dark:text-red-300 mb-2">
        Athena has detected signs of distress. Specialized support is being provided.
      </p>
      {crisisData.crisis_response && (
        <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded border border-red-300 dark:border-red-700">
          <p className="text-sm text-gray-800 dark:text-gray-200">
            {crisisData.crisis_response}
          </p>
        </div>
      )}
      <div className="mt-3 text-xs text-red-600 dark:text-red-400">
        <p className="font-semibold">Crisis Support Resources:</p>
        <p>CCCline1333 - Languages: Sinhala, Tamil, English - Hours: 24x7</p>
      </div>
    </div>
  )
}

