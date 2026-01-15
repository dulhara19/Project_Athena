import React, { useState, useEffect } from 'react'
import { useWorkflow } from '../context/WorkflowContext'
import EmotionDisplay from './EmotionDisplay'
import CrisisAlert from './CrisisAlert'

export default function ChatInterface() {
  const { state, sendMessage, resetWorkflow } = useWorkflow()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'athena', text: string, timestamp: string }>>([])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || state.isProcessing) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message to chat
    setMessages(prev => [...prev, {
      role: 'user',
      text: userMessage,
      timestamp: new Date().toISOString(),
    }])

    // Send to backend
    await sendMessage(userMessage)

    // Wait for result and add Athena's response
    // (This will be updated via WebSocket in real implementation)
  }

  // Update messages when result arrives
  if (state.result && !messages.some(m => m.timestamp === state.result.timestamp)) {
    setMessages(prev => [...prev, {
      role: 'athena',
      text: state.result.athena_response,
      timestamp: state.result.timestamp,
    }])
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 h-[800px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Chat with Athena</h2>
        {state.isProcessing && (
          <div className="flex items-center space-x-2 text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm">Processing...</span>
          </div>
        )}
      </div>

      {/* Crisis Alert */}
      {state.result?.crisis_mode && (
        <CrisisAlert crisisData={state.result} />
      )}

      {/* Emotion Display */}
      {state.result?.metrics?.user_pain !== undefined && (
        <div className="mb-4">
          <EmotionDisplay 
            emotions={state.result.metrics?.user_emotions}
            painLevel={state.result.metrics?.user_pain}
          />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white'
              }`}
            >
              <p className="text-sm">{msg.text}</p>
              <p className="text-xs opacity-70 mt-1">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          disabled={state.isProcessing}
        />
        <button
          type="submit"
          disabled={!input.trim() || state.isProcessing}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </form>

      {state.error && (
        <div className="mt-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-200 rounded">
          Error: {state.error}
        </div>
      )}
    </div>
  )
}

