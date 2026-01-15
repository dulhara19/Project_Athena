# Athena Frontend Documentation

## Overview

React-based frontend with TypeScript, providing live visualization of the Athena AI agent workflow.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── ChatInterface.tsx
│   │   ├── WorkflowVisualizer.tsx
│   │   ├── EmotionDisplay.tsx
│   │   ├── EgoSystemDisplay.tsx
│   │   ├── EmpathyMetrics.tsx
│   │   ├── PainHistory.tsx
│   │   ├── MBTIDisplay.tsx
│   │   └── CrisisAlert.tsx
│   ├── pages/            # Page components
│   │   └── Dashboard.tsx
│   ├── context/          # React context
│   │   └── WorkflowContext.tsx
│   ├── hooks/            # Custom hooks
│   │   └── useWebSocket.ts
│   ├── services/         # API services
│   │   └── api.ts
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
```

## Components

### ChatInterface

Main chat interface for user interaction.

**Props**: None (uses WorkflowContext)

**Features**:
- User input form
- Message history
- Real-time status indicators
- Emotion display integration
- Crisis alert integration

### WorkflowVisualizer

Real-time visualization of workflow steps.

**Props**: None (uses WorkflowContext)

**Features**:
- Step-by-step progress display
- Progress bar
- Step status indicators
- Step details panel

### EmotionDisplay

Visualization of user emotions.

**Props**:
- `emotions?: Record<string, number>`
- `painLevel?: number`
- `vad?: { valence, arousal, dominance }`

**Features**:
- Emotion pie chart
- Pain level gauge
- VAD scores display

### EgoSystemDisplay

Multi-dimensional ego visualization.

**Props**:
- `egoState?: { dimensions, strength, fragility, consistency }`
- `dimensionImpacts?: Record<string, number>`

**Features**:
- Ego strength meter
- Dimension health bars
- Dimension impact visualization

### EmpathyMetrics

Empathy metrics visualization.

**Props**:
- `empathyMetrics?: { empathy, alignment, same_direction, confidence }`
- `userPain?: number`
- `athenaPain?: number`

**Features**:
- Empathy gauge (radial chart)
- Pain comparison
- Metrics breakdown

### PainHistory

Historical pain level visualization.

**Props**:
- `history?: Array<{ user_query, pain_status, timestamp }>`

**Features**:
- Pain timeline chart
- Interactive tooltips

### MBTIDisplay

MBTI personality visualization.

**Props**:
- `mbti?: { mbti, axis_scores, confidence }`

**Features**:
- MBTI radar chart
- Confidence display

### CrisisAlert

Crisis mode alert component.

**Props**:
- `crisisData?: { crisis_mode, crisis_response }`

**Features**:
- Crisis detection alert
- Support resources

## State Management

### WorkflowContext

Global state management for workflow.

**State**:
- `workflowId`: Current workflow ID
- `steps`: Array of workflow steps
- `currentStep`: Current step number
- `progress`: Progress percentage
- `isProcessing`: Processing status
- `result`: Final result
- `error`: Error message

**Methods**:
- `sendMessage(userInput, userId, sessionId)`: Send message and start workflow
- `resetWorkflow()`: Reset workflow state

## WebSocket Integration

Uses `socket.io-client` for WebSocket communication.

**Connection**: Automatically connects when workflow starts

**Events**:
- `workflow_progress`: Progress updates
- `workflow_complete`: Completion event
- `workflow_error`: Error event

## Styling

Uses TailwindCSS for styling with dark mode support.

**Theme Colors**:
- Primary: Blue (#3b82f6)
- Success: Green (#10b981)
- Error: Red (#ef4444)
- Warning: Yellow (#f59e0b)

## Building for Production

```bash
npm run build
```

Output in `dist/` directory.

## Development

```bash
npm run dev      # Start dev server
npm run lint     # Run linter
npm run preview  # Preview production build
```

