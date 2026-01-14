import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { chatApi } from '../services/api'

interface WorkflowStep {
  step_number: number
  step_name: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  data?: any
  error?: string
  timestamp: string
}

interface WorkflowState {
  workflowId: string | null
  steps: WorkflowStep[]
  currentStep: number
  progress: number
  isProcessing: boolean
  result: any | null
  error: string | null
}

interface WorkflowContextType {
  state: WorkflowState
  sendMessage: (userInput: string, userId?: string, sessionId?: string) => Promise<void>
  resetWorkflow: () => void
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined)

export function WorkflowProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WorkflowState>({
    workflowId: null,
    steps: [],
    currentStep: 0,
    progress: 0,
    isProcessing: false,
    result: null,
    error: null,
  })

  const handleMessage = useCallback((data: any) => {
    if (data.type === 'workflow_progress') {
      const progress = data.progress
      setState(prev => ({
        ...prev,
        steps: progress.steps || [],
        currentStep: progress.current_step || 0,
        progress: progress.progress_percentage || 0,
      }))
    } else if (data.type === 'workflow_complete') {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        result: data.result,
        progress: 100,
      }))
    } else if (data.type === 'workflow_error') {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        error: data.error,
      }))
    }
  }, [])

  const { connect, disconnect } = useWebSocket({
    workflowId: state.workflowId || undefined,
    onMessage: handleMessage,
  })

  const sendMessage = useCallback(async (
    userInput: string,
    userId: string = 'user123',
    sessionId: string = 'session1'
  ) => {
    setState(prev => ({
      ...prev,
      isProcessing: true,
      error: null,
      result: null,
      steps: [],
      progress: 0,
    }))

    try {
      // Start streaming workflow
      const streamResponse = await chatApi.streamMessage({
        user_id: userId,
        session_id: sessionId,
        text: userInput,
      })

      setState(prev => ({
        ...prev,
        workflowId: streamResponse.workflow_id,
      }))

      // Connect WebSocket for real-time updates
      connect()
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        error: error.message || 'Failed to send message',
      }))
    }
  }, [connect])

  const resetWorkflow = useCallback(() => {
    disconnect()
    setState({
      workflowId: null,
      steps: [],
      currentStep: 0,
      progress: 0,
      isProcessing: false,
      result: null,
      error: null,
    })
  }, [disconnect])

  return (
    <WorkflowContext.Provider value={{ state, sendMessage, resetWorkflow }}>
      {children}
    </WorkflowContext.Provider>
  )
}

export function useWorkflow() {
  const context = useContext(WorkflowContext)
  if (context === undefined) {
    throw new Error('useWorkflow must be used within a WorkflowProvider')
  }
  return context
}

