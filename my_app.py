#!/usr/local/bin python3

from flask import Flask, render_template, request, redirect, session
from jinja2 import Environment, PackageLoader
from chess_ai import Game_Engine


app = Flask(__name__)
app.secret_key = '12345'

@app.route('/', methods=['GET', 'POST'])
def start_game():
    session['piece_styles'] = {'r': u'&#9820', 'n': u'&#9822', 'b': u'&#9821', 'q': u'&#9819', 'k': u'&#9818', 'p': u'&#9823', 'P': u'&#9817', 'R': u'&#9814', 'N': u'&#9816', 'B': u'&#9815', 'Q': u'&#9813', 'K': u'&#9812', '-': ''}
    if request.method == 'GET':
        return render_template('welcome.html')
    else:
        session['fen'] = request.form['fen']
        if session['fen'] == '':
            session['fen'] = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        return redirect('/game')

@app.route('/game', methods=['GET', 'POST'])
def homepage():
    if request.method == 'GET':
        fen = session['fen']
        game_engine = Game_Engine(session['fen'])
        game = game_engine.game
        ai2=game_engine.computer2
        if game.status < 2:
            if str(game).split()[1] =='w':
                recommended_move = ai2.make_move(str(game))
        board_layout = list(fen.split()[0])
        for indy in range(len(board_layout)):
            if board_layout[indy].isdigit():
                board_layout[indy] = int(board_layout[indy]) * '-'
        board_layout = ''.join(board_layout)
        board_layout = board_layout.split('/')
        piece_styles = {'r': u'&#9820', 'n': u'&#9822', 'b': u'&#9821', 'q': u'&#9819', 'k': u'&#9818', 'p': u'&#9823', 'P': u'&#9817', 'R': u'&#9814', 'N': u'&#9816', 'B': u'&#9815', 'Q': u'&#9813', 'K': u'&#9812', '-': ''}
        return render_template('homepage3.html', board_layout=board_layout, piece_styles=piece_styles, valid_move_check="Adam's AI recommends the move: " + recommended_move)
    else:
        player_algebraic_move = request.form['move']
        submit = request.form.get('comp_move')
        game_engine = Game_Engine(session['fen'])
        game = game_engine.game
        ai = game_engine.computer
        if game.status < 2:
            if str(game).split()[1] == 'w':
                if player_algebraic_move in game.get_moves():
                    game.apply_move(player_algebraic_move)
                else:
                    fen = session['fen']
                    board_layout = list(fen.split()[0])
                    for indy in range(len(board_layout)):
                        if board_layout[indy].isdigit():
                            board_layout[indy] = int(board_layout[indy]) * '-'
                    board_layout = ''.join(board_layout).split('/')
                    piece_styles = {'r': u'&#9820', 'n': u'&#9822', 'b': u'&#9821', 'q': u'&#9819', 'k': u'&#9818', 'p': u'&#9823', 'P': u'&#9817', 'R': u'&#9814', 'N': u'&#9816', 'B': u'&#9815', 'Q': u'&#9813', 'K': u'&#9812', '-': ''}
                    return render_template('homepage3.html', board_layout=board_layout, piece_styles=piece_styles, valid_move_check='Please enter a valid move')
            elif str(game).split()[1] == 'b':
                ai_algebraic_move = ai.make_move(str(game))
                game.apply_move(ai_algebraic_move)
            session['fen'] = str(game)
            fen = session['fen']
            board_layout = list(fen.split()[0])
            for indy in range(len(board_layout)):
                if board_layout[indy].isdigit():
                    board_layout[indy] = int(board_layout[indy]) * '-'
            board_layout = ''.join(board_layout).split('/')
            piece_styles = {'r': u'&#9820', 'n': u'&#9822', 'b': u'&#9821', 'q': u'&#9819', 'k': u'&#9818', 'p': u'&#9823', 'P': u'&#9817', 'R': u'&#9814', 'N': u'&#9816', 'B': u'&#9815', 'Q': u'&#9813', 'K': u'&#9812', '-': ''}
            return render_template('homepage3.html', board_layout=board_layout, piece_styles=piece_styles)
        return render_template("/game_over")

@app.route('/ai', methods=['GET', 'POST'])
def aivsai():
    if request.method == 'POST':
        game_engine = Game_Engine(session['fen'])
        game = game_engine.game
        ai = game_engine.computer
        ai2 = game_engine.computer2
        if ai2.game.status < 2 and ai2.game.status < 2:
            if str(game).split()[1] == 'w':
                ai2_move = ai2.make_move(str(game))
                game.apply_move(ai2_move)
            elif str(game).split()[1] == 'b':
                ai_move = ai.make_move(str(game))
                game.apply_move(ai_move)
            else:
                print('1 or 2 not working')
                print(str(game))
            session['fen'] = str(game)
            fen = session['fen']
            board_layout = list(fen.split()[0])
            for indy in range(len(board_layout)):
                if board_layout[indy].isdigit():
                    board_layout[indy] = int(board_layout[indy]) * '-'
            board_layout = ''.join(board_layout).split('/')
            return render_template('ai.html',board_layout=board_layout, piece_styles=session['piece_styles'])
        elif ai.game.status >=2:
            with open('moves_cache_white.txt', 'r') as m:
                win_moves = m.read()
            with open('wins_cache.txt','a') as w:
                w.write(win_moves)
            return render_template('game_over.html')
        elif ai2.game.status >=2:
            with open('moves_cache_white.txt', 'w') as mc:
                mc.write('\n')
            return render_template('game_over.html')
                

    else:
        fen = session['fen']
        board_layout = list(fen.split()[0])
        for indy in range(len(board_layout)):
            if board_layout[indy].isdigit():
                board_layout[indy] = int(board_layout[indy]) * '-'
        board_layout = ''.join(board_layout).split('/')
        return render_template('ai.html',board_layout=board_layout, piece_styles=session['piece_styles'])




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


