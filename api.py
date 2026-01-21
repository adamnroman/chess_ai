"""
Chess AI API Server
Flask backend with CORS support for the React frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from chess_ai import Game_Engine

app = Flask(__name__)
CORS(app)

# Game status constants
STATUS_NORMAL = 0
STATUS_CHECK = 1
STATUS_CHECKMATE = 2
STATUS_STALEMATE = 3

def get_game_status_text(status, turn):
    """Convert game status code to human-readable text"""
    if status == STATUS_CHECKMATE:
        winner = "Black" if turn == 'w' else "White"
        return f"Checkmate! {winner} wins!"
    elif status == STATUS_STALEMATE:
        return "Stalemate! It's a draw."
    elif status == STATUS_CHECK:
        return "Check!"
    return ""

@app.route('/api/move', methods=['POST'])
def make_move():
    """
    Make a player move and get AI response

    Request body:
        - fen: Current board position in FEN notation
        - move: Player's move in algebraic notation (e.g., 'e2e4')

    Returns:
        - success: Boolean indicating if move was valid
        - fen: New board position after moves
        - aiMove: The AI's response move
        - status: Game status code (0=normal, 1=check, 2=checkmate, 3=stalemate)
        - statusText: Human readable status
        - turn: Current turn ('w' or 'b')
        - legalMoves: List of legal moves for current position
    """
    data = request.get_json()
    fen = data.get('fen')
    player_move = data.get('move')

    if not fen:
        return jsonify(success=False, error="FEN position required"), 400

    try:
        game_engine = Game_Engine(fen)
        game = game_engine.game
        ai = game_engine.computer

        # Check if player move was provided
        if player_move:
            # Validate and apply player move
            legal_moves = game.get_moves()
            if player_move not in legal_moves:
                return jsonify(
                    success=False,
                    error="Invalid move",
                    legalMoves=legal_moves
                ), 400

            game.apply_move(player_move)

        ai_move = None

        # If it's AI's turn (black) and game not over
        if game.status < STATUS_CHECKMATE:
            current_turn = str(game).split()[1]
            if current_turn == 'b':
                ai_move = ai.make_move(str(game))
                game.apply_move(ai_move)

        new_fen = str(game)
        current_turn = new_fen.split()[1]
        legal_moves = game.get_moves() if game.status < STATUS_CHECKMATE else []

        return jsonify(
            success=True,
            fen=new_fen,
            aiMove=ai_move,
            status=game.status,
            statusText=get_game_status_text(game.status, current_turn),
            turn=current_turn,
            legalMoves=legal_moves,
            isGameOver=game.status >= STATUS_CHECKMATE
        )

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/ai-move', methods=['POST'])
def get_ai_move():
    """
    Get AI move for current position (used for AI vs AI mode)

    Request body:
        - fen: Current board position in FEN notation

    Returns:
        - success: Boolean
        - fen: New board position after AI move
        - aiMove: The AI's move
        - status: Game status code
        - statusText: Human readable status
    """
    data = request.get_json()
    fen = data.get('fen')

    if not fen:
        return jsonify(success=False, error="FEN position required"), 400

    try:
        game_engine = Game_Engine(fen)
        game = game_engine.game
        current_turn = fen.split()[1]

        if game.status >= STATUS_CHECKMATE:
            return jsonify(
                success=True,
                fen=fen,
                aiMove=None,
                status=game.status,
                statusText=get_game_status_text(game.status, current_turn),
                isGameOver=True
            )

        # Use appropriate AI based on turn
        if current_turn == 'w':
            ai = game_engine.computer2  # White AI
        else:
            ai = game_engine.computer   # Black AI

        ai_move = ai.make_move(str(game))
        game.apply_move(ai_move)

        new_fen = str(game)
        new_turn = new_fen.split()[1]

        return jsonify(
            success=True,
            fen=new_fen,
            aiMove=ai_move,
            status=game.status,
            statusText=get_game_status_text(game.status, new_turn),
            turn=new_turn,
            isGameOver=game.status >= STATUS_CHECKMATE
        )

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/new-game', methods=['POST'])
def new_game():
    """
    Start a new game

    Request body (optional):
        - fen: Custom starting position (defaults to standard starting position)

    Returns:
        - success: Boolean
        - fen: Starting position
        - legalMoves: List of legal moves
    """
    data = request.get_json() or {}
    fen = data.get('fen', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    try:
        game_engine = Game_Engine(fen)
        game = game_engine.game
        legal_moves = game.get_moves()

        return jsonify(
            success=True,
            fen=fen,
            legalMoves=legal_moves,
            turn='w',
            status=game.status
        )

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/validate', methods=['POST'])
def validate_position():
    """
    Validate a FEN string and return game state
    """
    data = request.get_json()
    fen = data.get('fen')

    if not fen:
        return jsonify(success=False, error="FEN position required"), 400

    try:
        game_engine = Game_Engine(fen)
        game = game_engine.game
        current_turn = fen.split()[1]

        return jsonify(
            success=True,
            valid=True,
            fen=str(game),
            status=game.status,
            statusText=get_game_status_text(game.status, current_turn),
            turn=current_turn,
            legalMoves=game.get_moves() if game.status < STATUS_CHECKMATE else []
        )

    except Exception as e:
        return jsonify(success=False, valid=False, error=str(e)), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify(status="ok", message="Chess AI API is running")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
