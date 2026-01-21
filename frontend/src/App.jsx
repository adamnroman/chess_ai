import { useState } from 'react'
import ChessGame from './components/ChessGame'
import './App.css'

function App() {
  const [gameMode, setGameMode] = useState(null)

  if (!gameMode) {
    return (
      <div className="app">
        <div className="welcome-screen">
          <h1>Chess AI</h1>
          <p>Challenge a powerful minimax-based chess engine</p>
          <div className="mode-selection">
            <button
              className="mode-button"
              onClick={() => setGameMode('player')}
            >
              Play vs AI
            </button>
            <button
              className="mode-button secondary"
              onClick={() => setGameMode('ai')}
            >
              Watch AI vs AI
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Chess AI</h1>
        <button className="back-button" onClick={() => setGameMode(null)}>
          New Game
        </button>
      </header>
      <ChessGame mode={gameMode} />
    </div>
  )
}

export default App
