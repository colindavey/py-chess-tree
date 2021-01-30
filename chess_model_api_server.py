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

def make_state(pgn_game, pgn_node):
    board = pgn_node.board()
    state_str = {}
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
    state_str["piece_distrib"] = piece_distrib
    state_str["fen"] = board.fen()

    state_str["turn"] = 'W' if board.turn else 'B'
    state_str["legal_moves"] = [str(m) for m in board.legal_moves]

    variations = []
    for variation in pgn_node.variations:
        variations.append(variation.san())
    state_str["variations"] = variations
    state_str["comment"] = pgn_node.comment
    state_str["has_parent"] = pgn_node.parent is not None
    state_str["moves"] = pgn_node2moves(pgn_node)
    state_str["pgn_str"] = game2pgn_str(pgn_game)
    state_str["player_white"] = pgn_game.headers['White']
    state_str["player_black"] = pgn_game.headers['Black']
    state_str["root_node_str"] = make_root_node_str(pgn_game)
    if pgn_node.parent is None:
        state_str["node_str"] = state_str["root_node_str"]
    else:
        state_str["node_str"] = make_san_node_str(pgn_node)
    # state_str["game_py"] = pgn_game
    # state_str["node_py"] = pgn_node
    return state_str

def make_root_node_str(game_py):
    return 'White: ' + game_py.headers['White'] + '. Black: ' + game_py.headers['Black'] + '.' + \
        make_brief_comment_str(game_py.comment)

def make_tree_dict_recur(node_py):
    tree = {}
    if not node_py.parent is not None:
        tree["label"] = make_root_node_str(node_py)
    else: 
        tree["label"] = make_san_node_str(node_py)
    tree["children"] = []
    if node_py.is_end():
        return tree
    else:
        for variation in node_py.variations:
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

def calc_san(pgn_node, start, destination):
    uci = file_rank2square_name(start["file"], start["rank"]) + file_rank2square_name(destination["file"], destination["rank"])
    return pgn_node.board().san(chess.Move.from_uci(uci))

def get_var_from_san(pgn_node, san):
    return pgn_node.variation(pgn_node.board().parse_san(san))

def pgn_node2moves(pgn_node):
    moves = []
    tmp_node = pgn_node
    while tmp_node.parent is not None:
        moves.append(tmp_node.san())
        tmp_node = tmp_node.parent
    moves.reverse()
    return moves

def game2pgn_str(game):
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    return game.accept(exporter)

def make_san_node_str(pgn_node, init_ply_num=0):
    move_num = pgn_node.parent.board().fullmove_number
    ply_num = pgn_node.parent.board().ply()

    # assuming it's white's turn
    turn_str = str(move_num) + '.'
    # if it's black's turn
    if not pgn_node.parent.board().turn:
        turn_str += '..'
    turn_str += ' '
    str_out = turn_str + pgn_node.san() + make_brief_comment_str(pgn_node.comment)

    spaces = (ply_num-(init_ply_num+1)) * '  '
    end_str = ""
    if pgn_node.is_end():
        end_str = " *"
    print(spaces + str_out + end_str)
    return str_out

# Reports - not used or tested much
def get_numbered_moves(pgn_node):
    moves = pgn_node2moves(pgn_node)
    # add the numbers to all of white's moves
    for p in range(0, len(moves), 2):
        san = moves[p]
        moves[p] = str(p // 2 + 1) + '. ' + san
    return moves

def print_listing_vertical(pgn_node):
    moves = get_numbered_moves(pgn_node)
    num_moves = len(moves)
    for p in range(0, num_moves):
        # if it's white's move, make the 1st half of the line.
        if p % 2 == 0:
            tmpstr = moves[p]
            # if it's the last move, then there is no black bit to append. so print it now
            if p == num_moves - 1:
                print(tmpstr)
        # if it's black's move, make the 2nd half of the line and print it.
        else:
            tmpstr += '\t' + moves[p]
            print(tmpstr)

def print_listing_horizontal(pgn_node):
    moves = get_numbered_moves(pgn_node)
    num_moves = len(moves)
    tmpstr = ''
    for p in range(0, num_moves):
        tmpstr += moves[p]
        if p != num_moves - 1:
            tmpstr += ' '
    print(tmpstr)
    return tmpstr

def print_pgn_node_hybrid(pgn_node):
    print_listing_horizontal(pgn_node)
    print_pgn_node_recur(pgn_node, True)

def print_pgn_node_recur(pgn_node, initial=False, ply_num=0):
    # if pgn_node.parent is not None:
    if initial:
        if pgn_node.parent is not None:
            ply_num = pgn_node.parent.board().ply()
    else:
        make_san_node_str(pgn_node, init_ply_num=ply_num)
    if not pgn_node.is_end():
        for p in range(0, len(pgn_node.variations)):
            print_pgn_node_recur(pgn_node.variations[p], ply_num=ply_num)

# def report(state_str):
#     # print('pgn:')
#     # print(state_str.game_py)
#     # print('tree:')
#     # print_pgn_node_recur(state_str.game_py, True)
#     # print('listing:')
#     # print_listing_vertical(state_str.node_py)
#     # print('horizontal listing:')
#     # print_listing_horizontal(state_str.node_py)
#     # print('hybrid horizontal tree:')
#     # print_pgn_node_hybrid(state_str.node_py)
#     pass
