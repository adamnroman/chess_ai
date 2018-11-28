from game import Game

def material(board_state, weight):
    white_points = 0
    board_state = board_state.split()[0]
    piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 0}
    for piece in board_state:
        if piece.islower():
            white_points -= piece_values[piece]
        elif piece.isupper():
            white_points += piece_values[piece.lower()]
    return white_points * weight

def piece_moves(game, weight):
    white_points = 0
    turn = str(game).split()[1]
    square_values = {"e4": 0.8, "e5": 0.8, "d4": 0.8, "d5": 0.8, "c3": 0.4, "d3": 0.4, "e3": 0.4, "f3": 0.4,
                    "c6": 0.4, "d6": 0.4, "e6": 0.4, "f6": 0.4, "c5": 0.4, "c4": 0.4, "f5": 0.4, "f4": 0.4}
    possible_moves = game.get_moves()
    for move in possible_moves:
        if turn == "w":
            if move[2:4] in square_values:
                white_points += square_values[move[2:4]]
        else:
            if move[2:4] in square_values:
                white_points -= square_values[move[2:4]]
    # piece_values = {'p': 1, 'b': 4, 'n': 4, 'r': 3, 'q': 3, 'k': 0}
    # for move in game.get_moves():
    #     current_piece = game.board.get_piece(game.xy2i(move[:2]))
    #     if current_piece.islower():
    #         black_points += piece_values[current_piece]
    return white_points

def pawn_structure(board_state, weight):
    white_points = 0
    board_state, current_player = [segment for segment in board_state.split()[:2]]
    board_state = board_state.split("/")

    # convert fen into matrix:
    board_state_arr = []
    for row in board_state:
    	row_arr = []
    	for char in row:
    		if char.isdigit():
    			for i in range(int(char)):
    				row_arr.append(" ")
    		else:
    			row_arr.append(char)
    	board_state_arr.append(row_arr)

    # determine pawn to search for based on whose turn it is
    for i, row in enumerate(board_state_arr):
        for j in range(len(row)):
            if board_state_arr[i][j] == "P":
                tl = i-7, j-1
                tr = i-7, j+1
                if tl[0] >= 0 and tl[0] <= 7 and tl[1] >= 0 and tl[1] <= 7:
                    if board_state_arr[tl[0]][tl[1]] == "P":
                        white_points += 1
                if tr[0] >= 0 and tr[0] <= 7 and tr[1] >= 0 and tr[1] <= 7:
                    if board_state_arr[tr[0]][tr[1]] == "P":
                        white_points += 1
    return white_points * weight

def in_check(game, weight):
    white_points = 0
    current_status = game.status
    # Turn should be 'w' or 'b'
    turn = str(game).split(" ")[1]
    # Check or Checkmate situations
    if turn == "b":
        if current_status == 1:
            white_points += 1 * weight
        elif current_status == 2:
            white_points += 10000
    else:
        if current_status == 1:
            white_points -= 1 * weight
        elif current_status == 2:
            white_points -= 10000
    return white_points

def avoid_stalemate(game):
    white_points = 0
    turn = str(game).split()[1]
    square_values = {"e4": 0.8, "e5": 0.8, "d4": 0.8, "d5": 0.8, "c3": 0.4, "d3": 0.4, "e3": 0.4, "f3": 0.4,
                    "c6": 0.4, "d6": 0.4, "e6": 0.4, "f6": 0.4, "c5": 0.4, "c4": 0.4, "f5": 0.4, "f4": 0.4}
    possible_moves = game.get_moves()
    for move in possible_moves:
        if turn == "w":
            if move[2:4] in square_values:
                white_points += square_values[move[2:4]]
        else:
            if move[2:4] in square_values:
                white_points -= square_values[move[2:4]]
    # piece_values = {'p': 1, 'b': 4, 'n': 4, 'r': 3, 'q': 3, 'k': 0}
    # for move in game.get_moves():
    #     current_piece = game.board.get_piece(game.xy2i(move[:2]))
    #     if current_piece.islower():
    #         black_points += piece_values[current_piece]
    return white_points