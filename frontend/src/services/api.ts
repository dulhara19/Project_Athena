import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface UserInputRequest {
  user_id: string
  session_id: string
  text: string
}

export interface InteractionResponse {
  workflow_id: string
  user_id: string
  session_id: string
  user_input: string
  athena_response: string
  workflow_steps: any[]
  metrics: any
  ego_state: any
  crisis_mode: boolean
  timestamp: string
}

export const chatApi = {
  async sendMessage(request: UserInputRequest): Promise<InteractionResponse> {
    const response = await api.post<InteractionResponse>('/chat', request)
    return response.data
  },

  async streamMessage(request: UserInputRequest): Promise<{ workflow_id: string; websocket_url: string }> {
    const response = await api.post('/chat/stream', request)
    return response.data
  },
}

export const metricsApi = {
  async getMetrics() {
    const response = await api.get('/metrics')
    return response.data
  },

  async getResearchMetrics() {
    const response = await api.get('/metrics/research')
    return response.data
  },
}

export const egoApi = {
  async getEgoState() {
    const response = await api.get('/ego/state')
    return response.data
  },

  async resetEgo(initialStrength?: number) {
    const response = await api.post('/ego/reset', { initial_strength: initialStrength })
    return response.data
  },
}

export default api

