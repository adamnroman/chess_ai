import { useState, useEffect, useCallback, useRef } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'

// API URL - uses proxy in development, direct URL in production
const API_URL = import.meta.env.VITE_API_URL || ''

const STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

function ChessGame({ mode }) {
  const [game, setGame] = useState(new Chess())
  const [fen, setFen] = useState(STARTING_FEN)
  const [moveHistory, setMoveHistory] = useState([])
  const [status, setStatus] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [isGameOver, setIsGameOver] = useState(false)
  const [error, setError] = useState(null)
  const aiIntervalRef = useRef(null)

  // Convert our move format (e2e4) to chess.js format
  const convertMoveFormat = (move) => {
    if (!move || move.length < 4) return null
    return {
      from: move.slice(0, 2),
      to: move.slice(2, 4),
      promotion: move.length > 4 ? move[4] : undefined
    }
  }

  // Convert chess.js move to our API format
  const toApiFormat = (from, to, promotion) => {
    return from + to + (promotion || '')
  }

  // Make API call to get AI move
  const getAiMove = useCallback(async (currentFen) => {
    try {
      const response = await fetch(`${API_URL}/api/ai-move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fen: currentFen })
      })
      const data = await response.json()
      return data
    } catch (err) {
      console.error('AI move error:', err)
      throw err
    }
  }, [])

  // Make player move and get AI response
  const makePlayerMove = useCallback(async (currentFen, move) => {
    try {
      const response = await fetch(`${API_URL}/api/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fen: currentFen, move })
      })
      const data = await response.json()
      return data
    } catch (err) {
      console.error('Move error:', err)
      throw err
    }
  }, [])

  // Handle piece drop (player move)
  const onDrop = useCallback(async (sourceSquare, targetSquare, piece) => {
    if (isThinking || isGameOver) return false
    if (mode === 'ai') return false // No manual moves in AI vs AI mode

    // Check if it's player's turn (white)
    if (game.turn() !== 'w') return false

    // Check for pawn promotion
    const promotion = piece[1] === 'P' && targetSquare[1] === '8' ? 'q' : undefined

    // Try the move locally first
    const gameCopy = new Chess(game.fen())
    try {
      const result = gameCopy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion
      })
      if (!result) return false
    } catch {
      return false
    }

    setIsThinking(true)
    setError(null)

    const moveStr = toApiFormat(sourceSquare, targetSquare, promotion)

    try {
      const data = await makePlayerMove(fen, moveStr)

      if (data.success) {
        const newGame = new Chess(data.fen)
        setGame(newGame)
        setFen(data.fen)

        // Update move history
        const newMoves = [...moveHistory]
        newMoves.push({ color: 'w', move: moveStr })
        if (data.aiMove) {
          newMoves.push({ color: 'b', move: data.aiMove })
        }
        setMoveHistory(newMoves)

        // Update status
        if (data.isGameOver) {
          setIsGameOver(true)
          setStatus(data.statusText)
        } else if (data.statusText) {
          setStatus(data.statusText)
        } else {
          setStatus('')
        }
      } else {
        setError(data.error || 'Invalid move')
      }
    } catch (err) {
      setError('Failed to connect to server')
    }

    setIsThinking(false)
    return true
  }, [game, fen, moveHistory, isThinking, isGameOver, mode, makePlayerMove])

  // AI vs AI mode
  useEffect(() => {
    if (mode !== 'ai' || isGameOver || isThinking) return

    const makeAiMove = async () => {
      setIsThinking(true)
      try {
        const data = await getAiMove(fen)

        if (data.success && data.aiMove) {
          const newGame = new Chess(data.fen)
          setGame(newGame)
          setFen(data.fen)

          const turn = fen.split(' ')[1]
          setMoveHistory(prev => [...prev, { color: turn, move: data.aiMove }])

          if (data.isGameOver) {
            setIsGameOver(true)
            setStatus(data.statusText)
          } else if (data.statusText) {
            setStatus(data.statusText)
          } else {
            setStatus('')
          }
        }
      } catch (err) {
        setError('Failed to connect to server')
      }
      setIsThinking(false)
    }

    // Add delay between AI moves for visibility
    aiIntervalRef.current = setTimeout(makeAiMove, 1000)

    return () => {
      if (aiIntervalRef.current) {
        clearTimeout(aiIntervalRef.current)
      }
    }
  }, [mode, fen, isGameOver, isThinking, getAiMove])

  // Reset game
  const resetGame = () => {
    setGame(new Chess())
    setFen(STARTING_FEN)
    setMoveHistory([])
    setStatus('')
    setIsThinking(false)
    setIsGameOver(false)
    setError(null)
    if (aiIntervalRef.current) {
      clearTimeout(aiIntervalRef.current)
    }
  }

  // Get board square styles for last move highlight
  const getSquareStyles = () => {
    const styles = {}
    if (moveHistory.length > 0) {
      const lastMove = moveHistory[moveHistory.length - 1].move
      if (lastMove && lastMove.length >= 4) {
        const from = lastMove.slice(0, 2)
        const to = lastMove.slice(2, 4)
        styles[from] = { backgroundColor: 'rgba(255, 255, 0, 0.4)' }
        styles[to] = { backgroundColor: 'rgba(255, 255, 0, 0.4)' }
      }
    }
    return styles
  }

  // Format move for display
  const formatMove = (move, index) => {
    const moveNum = Math.floor(index / 2) + 1
    if (index % 2 === 0) {
      return `${moveNum}. ${move.move}`
    }
    return move.move
  }

  return (
    <div className="chess-game">
      <div className="game-container">
        <div className="board-section">
          <div className="board-wrapper">
            <Chessboard
              position={fen}
              onPieceDrop={onDrop}
              boardWidth={480}
              customSquareStyles={getSquareStyles()}
              animationDuration={200}
              arePiecesDraggable={!isThinking && !isGameOver && mode === 'player'}
            />
          </div>

          {isThinking && (
            <div className="thinking-indicator">
              <div className="spinner"></div>
              <span>AI is thinking...</span>
            </div>
          )}

          {status && (
            <div className={`game-status ${isGameOver ? 'game-over' : ''}`}>
              {status}
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>

        <div className="side-panel">
          <div className="game-info">
            <h3>Game Info</h3>
            <p><strong>Mode:</strong> {mode === 'player' ? 'Player vs AI' : 'AI vs AI'}</p>
            <p><strong>Turn:</strong> {game.turn() === 'w' ? 'White' : 'Black'}</p>
            <p><strong>Moves:</strong> {Math.floor(moveHistory.length / 2) + (moveHistory.length % 2)}</p>
          </div>

          <div className="move-history">
            <h3>Move History</h3>
            <div className="moves-list">
              {moveHistory.length === 0 ? (
                <p className="no-moves">No moves yet</p>
              ) : (
                <div className="moves-grid">
                  {moveHistory.map((move, index) => (
                    <span
                      key={index}
                      className={`move ${move.color === 'w' ? 'white-move' : 'black-move'}`}
                    >
                      {formatMove(move, index)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="controls">
            <button className="control-button" onClick={resetGame}>
              Reset Game
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChessGame
