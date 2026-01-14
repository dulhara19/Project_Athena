import { useState } from 'react'
import { WorkflowProvider } from './context/WorkflowContext'
import ChatInterface from './components/ChatInterface'
import WorkflowVisualizer from './components/WorkflowVisualizer'
import Dashboard from './pages/Dashboard'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState<'chat' | 'dashboard'>('chat')

  return (
    <WorkflowProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
        <nav className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border-b border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-white">Athena AI</h1>
                <span className="ml-2 text-sm text-gray-400">Enhanced Ego System</span>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setCurrentView('chat')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'chat'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Chat
                </button>
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'dashboard'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Dashboard
                </button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {currentView === 'chat' ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChatInterface />
              <WorkflowVisualizer />
            </div>
          ) : (
            <Dashboard />
          )}
        </main>
      </div>
    </WorkflowProvider>
  )
}

export default App

