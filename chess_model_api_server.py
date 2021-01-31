# /usr/bin/python

import json
import chess
from chess import pgn
import io

from file_rank_square import file_rank2square_name

def chess_model_api_init():
    game = chess.pgn.Game()
    node = game
    return json.dumps(make_state(game, node))

def chess_model_api_make_tree(state_in):
    game, _ = calc_game_node(state_in)
    # print(print_node_tree(game))
    return json.dumps(make_tree_dict_recur(game))

def chess_model_api(operation, state_in, inputs={}):
    game, node = calc_game_node(state_in)
    inputs = json.loads(inputs)
    outputs = {}

    if operation == 'set_headers':
        if inputs['is_white']:
            game.headers["White"] = 'Me'
            game.headers["Black"] = 'Opponent'
        else:
            game.headers["White"] = 'Opponent'
            game.headers["Black"] = 'Me'

    elif operation == 'set_comment':
        node.comment = inputs['comment']

    elif operation == 'move_to':
        node = game_moves2node(game, inputs['moves'])
        # print('horizontal')
        # print(print_listing_horizontal(node))
        # print('vertical')
        # print(print_listing_vertical(node))
        # print('recur')
        # print(print_node_tree(node))

    elif operation == 'move_back_full':
        node = game

    elif operation == 'move_back':
        node = node.parent

    elif operation == 'move_add':
        start = inputs['start']
        destination = inputs['destination']
        uci = file_rank2square_name(start["file"], start["rank"]) + file_rank2square_name(destination["file"], destination["rank"])
        san = calc_san(node, start, destination)
        if node.has_variation(chess.Move.from_uci(uci)):
            added = False
            new_node = node.variation(chess.Move.from_uci(uci))
        else:
            added = True
            new_node = node.add_variation(chess.Move.from_uci(uci))
        outputs["added"] = added
        outputs["san"] = san
        outputs["move_str"] = make_san_node_str(new_node)

    elif operation == 'move_frwd':
        node = get_var_from_san(node, inputs['san'])

    elif operation == 'move_frwd_full':
        while not node.is_end():
            node = node.variations[0]

    elif operation == 'diddle_var':
        diddle_node = get_var_from_san(node, inputs['san'])
        diddle = inputs['diddle']
        if diddle == 'remove':
            node.remove_variation(diddle_node)
        elif diddle == 'promote2main':
            node.promote_to_main(diddle_node)
        elif diddle == 'promote':
            node.promote(diddle_node)
        elif diddle == 'demote':
            node.demote(diddle_node)

    return json.dumps(make_state(game, node)), json.dumps(outputs)

# Critical code

def make_brief_comment_str(comment_str):
    if comment_str != "":
        # strip out new lines
        comment_str = comment_str.replace('\n' ,' ')
        # if comment is too long, shorten it and append "..."
        max_comment_str_len = 50
        if len(comment_str) > max_comment_str_len:
            comment_str = comment_str[0:max_comment_str_len] + '...'
        comment_str = ' {' + comment_str + '}'
    return comment_str

def make_state(game, node):
    board = node.board()
    state = {}
    piece_distrib = []
    for file_ in range(0,8):
        rank_array = []
        for rank in range(0,8):
            piece = board.piece_at(chess.square(rank, file_))
            # rank_array[rank] = piece.symbol()
            piece_symbol = ''
            if piece is not None:
                piece_symbol = piece.symbol()
            rank_array.append(piece_symbol)
        piece_distrib.append(rank_array)
    state["piece_distrib"] = piece_distrib
    state["fen"] = board.fen()

    state["turn"] = 'W' if board.turn else 'B'
    state["legal_moves"] = [str(m) for m in board.legal_moves]

    variations = []
    for variation in node.variations:
        variations.append(variation.san())
    state["variations"] = variations
    state["comment"] = node.comment
    state["has_parent"] = node.parent is not None
    state["moves"] = node2moves(node)
    state["pgn_str"] = game2pgn_str(game)
    state["player_white"] = game.headers['White']
    state["player_black"] = game.headers['Black']
    state["root_node_str"] = make_root_node_str(game)
    if node.parent is None:
        state["node_str"] = state["root_node_str"]
    else:
        state["node_str"] = make_san_node_str(node)
    # state["game_py"] = game
    # state["node_py"] = node
    return state

def make_root_node_str(game):
    return 'White: ' + game.headers['White'] + '. Black: ' + game.headers['Black'] + '.' + \
        make_brief_comment_str(game.comment)

def make_tree_dict_recur(node):
    tree = {}
    if not node.parent is not None:
        tree["label"] = make_root_node_str(node)
    else: 
        tree["label"] = make_san_node_str(node)
    tree["children"] = []
    for variation in node.variations:
        tree["children"].append(make_tree_dict_recur(variation))
    return tree

def game_moves2node(game, moves):
    node = game
    for move in moves:
        node = get_var_from_san(node, move)
    return node

def calc_game_node(state):
    state = json.loads(state)
    pgn_str = io.StringIO(state["pgn_str"])
    game = chess.pgn.read_game(pgn_str)
    node = game_moves2node(game, state["moves"])
    return game, node
    # return state["game_py"], state["node_py"]

def calc_san(node, start, destination):
    uci = file_rank2square_name(start["file"], start["rank"]) + file_rank2square_name(destination["file"], destination["rank"])
    return node.board().san(chess.Move.from_uci(uci))

def get_var_from_san(node, san):
    return node.variation(node.board().parse_san(san))

def node2moves(node):
    moves = []
    tmp_node = node
    while tmp_node.parent is not None:
        moves.append(tmp_node.san())
        tmp_node = tmp_node.parent
    moves.reverse()
    return moves

def game2pgn_str(game):
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    return game.accept(exporter)

def make_san_node_str(node):
    # assuming it's white's turn
    turn_str = str(node.parent.board().fullmove_number) + '.'
    # if it's black's turn
    if not node.parent.board().turn:
        turn_str += '..'
    str_out = turn_str + ' ' +node.san() + make_brief_comment_str(node.comment)
    return str_out

#############################
# Reports
#############################

def get_numbered_moves(node):
    moves = node2moves(node)
    # add the numbers to all of white's moves
    for p in range(0, len(moves), 2):
        moves[p] = str(p // 2 + 1) + '. ' + moves[p]
    return moves

def print_listing_vertical(node):
    moves = get_numbered_moves(node)
    listing = ''
    for p, move in enumerate(moves):
        # if it's white's move, make the 1st half of the line.
        if p % 2 == 0:
            tmpstr = move
            # if it's the last move, then there is no black bit to append. so print it now
            if p == len(moves) - 1:
                listing += tmpstr
        # if it's black's move, make the 2nd half of the line and print it.
        else:
            tmpstr += '\t' + move
            if p != len(moves) - 1:
                tmpstr += '\n'
            listing += tmpstr
    return listing

def print_listing_horizontal(node):
    moves = get_numbered_moves(node)
    listing = ''
    for p, move in enumerate(moves):
        listing += move
        if p != len(moves) - 1:
            listing += ' '
    return listing

def print_node_tree(node):
    buffer = io.StringIO()
    print_node_tree_recur(node, buffer, initial=True)
    return(buffer.getvalue())

def print_node_tree_recur(node, buffer, initial=False, init_ply_num=0):
    if initial:
        if node.parent is not None:
            init_ply_num = node.parent.board().ply()+1
    else:
        san_str = make_san_node_str(node)
        ply_num = node.parent.board().ply()
        spaces = (ply_num-init_ply_num) * '  '
        # adds a * after if it's the last move
        print(spaces + san_str + (" *" if node.is_end() else ''), file=buffer)
    for variation in node.variations:
        print_node_tree_recur(variation, buffer, init_ply_num=init_ply_num)