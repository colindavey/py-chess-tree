# /usr/bin/python

import io
import tkinter as tk
from tkinter import PhotoImage
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
# from tkinter import font
import tkinter.font as tkfont

import os
import os.path
import chess
from chess import pgn
# !!!git this for tooltips
# import wckToolTips

from comment_editor import *
#try this:
# from comment_editor import CommentEditor
# import comment_editor

#####################################
# Game Model Utility Functions

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

# Critical code
def make_state_str(pgn_game, pgn_node):
    board = pgn_node.board()
    state_str = {}
    piece_distrib = []
    for file_ in range(0,8):
        rank_array = []
        for rank in range(0,8):
            piece = board.piece_at(chess.square(rank, file_))
            # rank_array[rank] = piece.symbol()
            piece_symbol = EMPTY_SQUARE
            if piece is not None:
                piece_symbol = piece.symbol()
            rank_array.append(piece_symbol)
        piece_distrib.append(rank_array)
    state_str["piece_distrib"] = piece_distrib
    state_str["fen"] = board.fen()
    state_str["turn"] = color_bool2char(board.turn)
    state_str["legal_moves"] = [str(m) for m in board.legal_moves]

    variations = []
    for variation in pgn_node.variations:
        variations.append(variation.san())
    state_str["variations"] = variations
    state_str["comment"] = pgn_node.comment
    state_str["has_parent"] = pgn_node.parent is not None
    state_str["moves"] = pgn_node2moves(pgn_node)
    state_str["pgn_str"] = game2pgn_str(pgn_game)

    state_str["game_py"] = pgn_game
    state_str["node_py"] = pgn_node
    return state_str

def set_headers(game, vp):
    if vp == 'W':
        game.headers["White"] = 'Me'
        game.headers["Black"] = 'Opponent'
    else:
        game.headers["White"] = 'Opponent'
        game.headers["Black"] = 'Me'
    return game

def init_pgn_state(game, vp):
    game = set_headers(game, vp)
    node = game
    return make_state_str(game, node) 

def game_moves2node(game, moves):
    node = game
    for p in range(0, len(moves)):
        ind = get_var_ind_from_san(node, moves[p])
        node = node.variation(ind)
    return node

def calc_game_node(state_str):
    pgn_str = io.StringIO(state_str["pgn_str"])
    game = chess.pgn.read_game(pgn_str)
    node = game_moves2node(game, state_str["moves"])
    return game, node
    # return state_str["game_py"], state_str["node_py"]

def calc_san(pgn_node, start, destination):
    uci = file_rank2str(start.file, start.rank) + file_rank2str(destination.file, destination.rank)
    return pgn_node.board().san(chess.Move.from_uci(uci))

# Assumes Var exists, should never get here if it doesn't. Intended for getting variation from san in dropdown menu
def get_var_ind_from_san(pgn_node, san):
    for p in range(0, len(pgn_node.variations)):
        if san == pgn_node.board().san(pgn_node.variations[p].move):
            return p

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
    spaces = ''
    for q in range(0, ply_num-(init_ply_num+1)):
        spaces += '  '
    end_str = ""
    if pgn_node.is_end():
        end_str = " *"
    comment_str = make_brief_comment_str(pgn_node.comment)
    str_out = turn_str + pgn_node.san() + comment_str
    print(spaces + str_out + end_str)
    return str_out

class ChessModelAPI(object):
    def __init__(self):
        pass

    def init_state(self, vp):
        game = chess.pgn.Game()
        return init_pgn_state(game, vp)

    def load_pgn(self, filename, vp):
        f = open(filename)
        game = chess.pgn.read_game(f)
        # !!!Error handling
        f.close()
        return init_pgn_state(game, vp)

    ###########################
    # moves
    ###########################

    def move_to(self, state_str, moves):
        game, node = calc_game_node(state_str)
        node = game_moves2node(game, moves)
        return make_state_str(game, node)

    def move_back_full(self, state_str):
        game, node = calc_game_node(state_str)
        node = game
        return make_state_str(game, node)

    def move_back(self, state_str):
        game, node = calc_game_node(state_str)
        node = node.parent
        return make_state_str(game, node)

    def move_frwd(self, state_str, san):
        game, node = calc_game_node(state_str)
        ind = get_var_ind_from_san(node, san)
        node = node.variations[ind]
        return make_state_str(game, node)

    def move_frwd_full(self, state_str):
        game, node = calc_game_node(state_str)
        while not node.is_end():
            node = node.variations[0]
        return make_state_str(game, node)

    def set_comment(self, state_str, comment):
        game, node = calc_game_node(state_str)
        node.comment = comment
        return make_state_str(game, node)

    def diddle_var(self, state_str, diddle, san):
        game, node = calc_game_node(state_str)
        print(diddle + 'Var')
        ind = get_var_ind_from_san(node, san)
        if diddle == 'remove':
            node.remove_variation(node.variations[ind].move)
        elif diddle == 'promote2main':
            node.promote_to_main(node.variations[ind].move)
        elif diddle == 'promote':
            node.promote(node.variations[ind].move)
        elif diddle == 'demote':
            node.demote(node.variations[ind].move)
        return make_state_str(game, node)

    ####################################
    # Doesn't change board state
    ####################################

    def move_add(self, state_str, start, destination):
        game, node = calc_game_node(state_str)
        print('move:', start.file, start.rank, destination.file, destination.rank)
        uci = file_rank2str(start.file, start.rank) + file_rank2str(destination.file, destination.rank)
        san = calc_san(node, start, destination)
        if node.has_variation(chess.Move.from_uci(uci)):
            added = False
            new_node = node.variation(chess.Move.from_uci(uci))
        else:
            added = True
            new_node = node.add_variation(chess.Move.from_uci(uci))
            # node.add_variation(chess.Move.from_uci(uci))
        return make_state_str(game, node), added, san, make_san_node_str(new_node)

    def set_headers(self, state_str, vp):
        game, node = calc_game_node(state_str)
        game = set_headers(game, vp)
        return make_state_str(game, node)

    def save_pgn(self, state_str, filename):
        f = open(filename, 'w')
        print(state_str["game_py"], file=f)
        f.close()

####################################
# GUI BOARD
####################################
# BASED ON
# Representing a chess set in Python
# Part 2
# Brendan Scott
# 27 April 2013
#
# create a chess board with pieces positioned for a new game
# row ordering is reversed from normal chess representations
# but corresponds to a top left screen coordinate
#
# Dark square on a1
# Requires there to be a directory called
# chess_data in the current directory, and for that
# data directory to have a copy of all the images


# column_reference = "1 2 3 4 5 6 7 8".split(" ")
column_reference = "a b c d e f g h".split(" ")
EMPTY_SQUARE = " "

TILE_WIDTH = 60
# We have used a tile width of 60 because the images we are used are 60x60 pixels
# The original svg files were obtained from
# http://commons.wikimedia.org/wiki/Category:SVG_chess_pieces/Standard_transparent
# after downloading they were batch converted to png, then gif files.  Bash one liners
# to do this:
# for i in $(ls *.svg); do inkscape -e ${i%.svg}.png -w 60 -h 60 $i ; done
# for i in $(ls *.png); do convert $i  ${i%.png}.gif ; done
# white and black tiles were created in inkscape

BOARD_WIDTH = 8 * TILE_WIDTH
BOARD_HEIGHT = BOARD_WIDTH
DATA_DIR = "chess_data"
TILES = {"black_tile": "black_tile.gif",
         "B": "chess_b451.gif",
         "b": "chess_b45.gif",
         "highlight_tile": "highlight_tile.gif",
         "k": "chess_k45.gif",
         "K": "chess_k451.gif",
         "n": "chess_n45.gif",
         "N": "chess_n451.gif",
         "p": "chess_p45.gif",
         "P": "chess_p451.gif",
         "q": "chess_q45.gif",
         "Q": "chess_q451.gif",
         "r": "chess_r45.gif",
         "R": "chess_r451.gif",
         "white_tile": "white_tile.gif"
         }


class BoardView(tk.Frame):
    def __init__(self, parent=None, vp='W'):
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        self.canvas.pack()
        self.images = {}
        for image_file_name in TILES:
            f = os.path.join(DATA_DIR, TILES[image_file_name])
            if not os.path.exists(f):
                print("Error: Cannot find image file: %s at %s - aborting" % (TILES[image_file_name], f))
                exit(-1)
            self.images[image_file_name] = PhotoImage(file=f)
            # This opens each of the image files, converts the data into a form that Tkinter
            # can use, then stores that converted form in the attribute self.images
            # self.images is a dictionary, keyed by the letters we used in our model to
            # represent the pieces - ie PRNBKQ for white and prnbkq for black
            # eg self.images['N'] is a PhotoImage of a white knight
            # this means we can directly translate a board entry from the model into a picture
        self.pack()
        self.vp = vp

    def set_player(self, vp):
        self.vp = vp

    def get_click_location(self, event):
        # Handle a click received.  The x,y location of the click on the canvas is at
        # (event.x, event.y)
        # translate the event coordinates (ie the x,y of where the click occurred)
        # into a position on the chess board

        file_ = event.x // TILE_WIDTH
        if file_ == 8:
            file_ = 7
        # the / operator is called integer division
        # it returns the number of times TILE_WIDTH goes into event.x ignoring any remainder
        # eg: 2/2 = 1, 3/2 = 1, 11/5 = 2 and so on
        # so, it should return a number between 0 (if x < TILE_WIDTH) though to 7
        rank = event.y // TILE_WIDTH
        if rank == 8:
            rank = 7
        # reversing rank/file as necessary for W/B
        rank = self.flip_y_rank(rank)
        file_ = self.flip_x_file(file_)
        return BoardCoords(file_, rank)

    def update_display(self, piece_distrib):
        """ draw an empty board then draw each of the
        pieces in the board over the top"""

        # first draw the empty board
        # then draw the pieces
        # if the order was reversed, the board would be drawn over the pieces
        # so we couldn't see them
        self.clear_canvas()
        self.draw_empty_board()
        self.draw_pieces(piece_distrib)

    def clear_canvas(self):
        """ delete everything from the canvas"""
        items = self.canvas.find_all()
        for i in items:
            self.canvas.delete(i)

    def draw_tile(self, file_, rank, tile):
        # reversing rank/file as necessary for W/B
        x = self.flip_x_file(file_) * TILE_WIDTH
        y = self.flip_y_rank(rank) * TILE_WIDTH
        self.canvas.create_image(x, y, anchor=tk.NW, image=tile)

    def draw_empty_board(self):
        for r in range(0, 8):
            first_tile_white = (r % 2)
            if first_tile_white:
                remainder = 1
            else:
                remainder = 0
            for f in range(0, 8):
                if f % 2 == remainder:
                    # f %2 is the remainder after dividing f by 2
                    # so f%2 will always be either 0 (no remainder- even numbers) or
                    # 1 (remainder 1 - odd numbers)
                    # this tests whether the number f is even or odd
                    tile = self.images['black_tile']
                else:
                    tile = self.images['white_tile']
                self.draw_tile(f, r, tile)

    def draw_pieces(self, piece_distrib):
        for r in range(0, 8):
            for f in range(0, 8):
                piece = piece_distrib[r][f]
                if piece == EMPTY_SQUARE:
                    continue  # skip empty tiles
                tile = self.images[piece]
                self.draw_tile(f, r, tile)

    def draw_highlights(self, highlight_list):
        tile = self.images['highlight_tile']
        for item in highlight_list:
            self.draw_tile(item.file, item.rank, tile)

    # reversing rank so rank 0 is the bottom (chess) rather than top (tk) for White
    def flip_y_rank(self, in_val):
        out_val = in_val
        if self.vp == 'W':
            out_val = 7 - out_val
        return out_val

    # reversing file so file 0 is the right (chess) rather than top (tk) for Black
    def flip_x_file(self, in_val):
        out_val = in_val
        if self.vp == 'B':
            out_val = 7 - out_val
        return out_val

#####################################
# Utility Functions

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

def color_bool2char(bool_in):
    if bool_in:
        return 'W'
    else:
        return 'B'

def get_piece_color(piece):
    if piece == EMPTY_SQUARE:
        return ' '
    elif piece.lower() == piece:
        return 'B'
    else:
        return 'W'

# file and rank inds to square name (e.g. "a1")
def file_rank2str(file_, rank):
    return chr(ord('a')+file_) + chr(ord('1')+rank)

class BoardCoords(object):
    def __init__(self, file_, rank):
        self.file = file_
        self.rank = rank

def geo_str2list(geo_str):
    geo_str = geo_str.replace('+', ' ')
    geo_str = geo_str.replace('x', ' ')
    geo = geo_str.split(' ')
    geo = [int(i) for i in geo]
    return geo

class ChessListing(tk.Frame):
    def __init__(self, parent=None, do_grid=False):
        tk.Frame.__init__(self, parent)
        self.table = ttk.Treeview(parent)
        ysb = ttk.Scrollbar(parent, orient='vertical', command=self.table.yview)
        self.table.configure(yscroll=ysb.set)
        ysb.pack(side=RIGHT, fill=Y)
        self.table.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.pack()

        self.table['columns'] = ('w', 'b')
        self.table.heading("#0", text='#', anchor='center')
        self.table.column("#0", width=5)
        self.table.heading('w', text='W')
        self.table.column('w', anchor='center', width=12)
        self.table.heading('b', text='B')
        self.table.column('b', anchor='center', width=12)
        self.table.configure(selectmode='none')

    def update_listing(self, moves):
        children = self.table.get_children('')
        for child in children:
            self.table.delete(child)
        for p in range(0, len(moves), 2):
            wm = moves[p]
            bm = ''
            if p < len(moves)-1:
                bm = moves[p+1]
            self.table.insert('', 'end', text=str(p // 2 + 1) + ".", values=(wm, bm))

    def handle_click(self, event):
        # get the row and column clicked on. row and col aren't numbers
        # they are tree things, with rows like I00B and cols like #1
        row = self.table.identify_row(event.y)
        col = self.table.identify_column(event.x)
        moves = []
        # make sure we have clicked in an actual cell
        # if not clicked in the column with the numbers (e.g. '1.')
        # and haven't clicked outside of the actual rows
        if col != '#0' and row != '':
            # get the text from the cell clicked on
            values = self.table.item(row, 'values')
            value = values[0]
            if col == '#2':
                value = values[1]
            # if the cell wasn't empty (the rightmost column of the last move with no move by black)
            if value != '':
                # get all the rows
                items = self.table.get_children('')
                # go through all the rows building up the moves stop when we get to the clicked-on move
                for p in range(0, len(items)):
                    values = self.table.item(items[p], 'values')
                    # add the first move of the row
                    moves.append(values[0])
                    # if we're not at the last row, then add the move
                    if items[p] != row:
                        moves.append(values[1])
                    else:
                        # break on the last row, adding black's move if that's what was clicked on
                        if col == '#2': # and values[1] != '':
                            moves.append(values[1])
                        break
        return moves

class Controls(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)

        self.backFullBtn = tk.Button(self, text="|<")
        self.backFullBtn.pack(side=LEFT)

        self.backBtn = tk.Button(self, text="<")
        self.backBtn.pack(side=LEFT)

        # next_move_str is a tk "control variable"
        # see http://effbot.org/tkinterbook/variable.htm
        # http://stackoverflow.com/questions/3876229/how-to-run-a-code-whenever-a-tkinter-widget-value-changes/3883495#3883495
        self.next_move_str = tk.StringVar(self)
        self.nextMoveOMen = tk.OptionMenu(self, self.next_move_str, [])
        # self.nextMoveOMen.config(width=7)
        self.nextMoveOMen.config(width=0)
        # self.nextMoveOMen.pack(side=LEFT, fill=X, expand=True)
        self.nextMoveOMen.pack(side=LEFT)

        self.frwdBtn = tk.Button(self, text=">")
        self.frwdBtn.pack(side=LEFT)

        self.frwdFullBtn = tk.Button(self, text=">|")
        self.frwdFullBtn.pack(side=LEFT)

        self.removeVarBtn = tk.Button(self, text="x")
        self.removeVarBtn.pack(side=LEFT)

        self.promote2MainVarBtn = tk.Button(self, text="^^")
        self.promote2MainVarBtn.pack(side=LEFT)

        self.promoteVarBtn = tk.Button(self, text="^")
        self.promoteVarBtn.pack(side=LEFT)

        self.demoteVarBtn = tk.Button(self, text="v")
        self.demoteVarBtn.pack(side=LEFT)

        # self.treeBtn = tk.Button(self, text="Tree")
        # self.treeBtn.pack(side=LEFT)

        self.commentBtn = tk.Button(self, text="{}")
        self.commentBtn.pack(side=LEFT)

        self.closeBtn = tk.Button(self, text="C")
        self.closeBtn.pack(side=LEFT)

        self.openBtn = tk.Button(self, text="O")
        self.openBtn.pack(side=LEFT)

        self.pack()

    def update_next_move_option_menu(self, variations, next_move_str=''):
        # reconfigure the listbox of next moves based on the current node
        # empty the listbox
        self.next_move_str.set('')
        self.nextMoveOMen['menu'].delete(0, 'end')
        # fill the listbox with the variations
        for variation in variations:
            # !!!maybe do self.next_move_str.set(variation) ?
            self.nextMoveOMen['menu'].add_command(label=variation, command=tk._setit(self.next_move_str, variation))
        # if there are variations, set it to the first one
        if len(variations) > 0:
            if next_move_str != '':
                self.next_move_str.set(next_move_str)
            else:
                self.next_move_str.set(variations[0])
        # else:
        #     self.nextMoveOMen['menu'].add_command(label='<none>')
        #     self.next_move_str.set('')

    def update_display(self, has_parent, variations):
        self.update_next_move_option_menu(variations)

        # diable back button if can't go back no more
        new_state = tk.NORMAL
        if not has_parent:
            new_state = tk.DISABLED
        self.backBtn.config(state=new_state)
        self.backFullBtn.config(state=new_state)

        # diable all the buttons if there are no variations
        # because of above, len(variations) == 0 is equiv to no variations
        new_state = tk.NORMAL
        if len(variations) == 0:
            new_state = tk.DISABLED
        self.frwdBtn.config(state=new_state)
        self.frwdFullBtn.config(state=new_state)
        self.removeVarBtn.config(state=new_state)
        self.promote2MainVarBtn.config(state=new_state)
        self.promoteVarBtn.config(state=new_state)
        self.demoteVarBtn.config(state=new_state)

class ChessTree(tk.Frame):
    def __init__(self, parent=None, do_grid=False):
        tk.Frame.__init__(self, parent)

        # For built-in, Grid doesn't work, Pack does.
        #   Grid dies before ap shows up
        # However, on separate window, the opposite.
        #   Pack fails on Tree button with
        # "'App' object has no attribute 'pack'"
        ####################
        if do_grid:
            Grid.columnconfigure(parent, 0, weight=1)
            Grid.rowconfigure(parent, 0, weight=1)
        ####################
        self.tree = ttk.Treeview(parent, show='tree')
        xsb = ttk.Scrollbar(parent, orient='horizontal', command=self.tree.xview)
        ysb = ttk.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        # self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.configure(xscroll=xsb.set)
        self.tree.configure(yscroll=ysb.set)
        ####################
        if do_grid:
            # This line needed to get horizontal scrollbar to sort of work
            # self.tree.pack(expand=1, fill=BOTH)
            # self.tree.grid(expand=1, fill=BOTH)

            self.tree.grid(row=0, column=0, sticky=W+E+N+S)
            xsb.grid(row=1, column=0, sticky='ew')
            ysb.grid(row=0, column=1, sticky='ns')
        else:
            xsb.pack(side=BOTTOM, fill=X)
            ysb.pack(side=RIGHT, fill=Y)
            self.tree.pack(side=BOTTOM, fill=BOTH, expand=True)
            self.pack()
        ####################

        # any tree node with tag sel_var will now automatically turn light gray
        self.tree.tag_configure('sel_var', background='#aaa') # light gray
        font_family = "Helvetica"
        # font_family = "courier"
        font_size = 12
        self.font = tkfont.Font(family=font_family, size=font_size)
        # self.font_actual_struct = self.font.actual()
        self.tree.tag_configure('all', font=(font_family, font_size))

        # tree changes due to clicks or key presses allow actions on tree selection changes
        # otherwise no
        self.tree.bind("<Button-1>", self.handle_tree_click)
        self.tree.bind("<Key>", self.handle_tree_click)
        self.tree_clicked = False
        # self.tree.configure(takefocus=1)

    def get_init_node_str(self, game):
        return 'White: ' + game.headers['White'] + '. Black: ' + game.headers['Black'] + '.'

    def make_tree(self, game):
        # empty tree
        children = self.tree.get_children('')
        for child in children:
            self.tree.delete(child)
        # insert initial tree node, and pass it in as 2nd parameter
        initial_node = self.tree.insert('', "end", text=self.get_init_node_str(game), open=True, tags='all')
        self.tree_pgn_node_recur(game, initial_node, True)

    def tree_pgn_node_recur(self, pgn_node, parent, initial=False):
        # if pgn_node.parent is not None:
        if not initial:
            the_str = make_san_node_str(pgn_node)
            parent = self.tree.insert(parent, "end", text=the_str, open=True, tags='all')
        if not pgn_node.is_end():
            for p in range(0, len(pgn_node.variations)):
                self.tree_pgn_node_recur(pgn_node.variations[p], parent)

    # tree changes due to clicks or key presses allow actions on tree selection changes
    # otherwise not
    # prevents handle_tree_select from running unless it was a direct result of a click,
    # or key press as opposed to programatically
    def handle_tree_click(self, event):
        self.tree_clicked = True

    def update_tree_node(self, pgn_node, tree_node):
        if pgn_node.parent is None:
            the_str = self.get_init_node_str(pgn_node) + ' ' + make_brief_comment_str(pgn_node.comment)
        else:
            the_str = make_san_node_str(pgn_node)
        # selected_node = self.get_selected_node()
        selected_node = tree_node
        self.tree.item(selected_node, text=the_str)

    def handle_tree_select(self):
        if self.tree_clicked:
            self.tree_clicked = False
            return True
        else:
            return False

    def get_tree_moves(self):
        moves = []
        # selitems = self.tree.selection()
        # tmp_node = selitems[0]
        tmp_node = self.get_selected_node()
        #!!!test for root node being initital, rather than''
        while self.tree.parent(tmp_node) != '':
            tmptext = self.tree.item(tmp_node, 'text')
            tmptext_bits = tmptext.split(' ')
            tmptext = tmptext_bits[1]
            moves.append(tmptext)
            tmp_node = self.tree.parent(tmp_node)
        moves.reverse()
        return moves

    def horz_scrollbar_magic(self):
        # uses magic numbers 2 and 20, which I found to be the x offset of the root item
        # and the amount it increases for each level depth
        items = self.tree.tag_has('all')
        max_w = 0
        for q in range(0, len(items)):
            item = items[q]
            tmptxt = self.tree.item(item, 'text')
            tw = self.font.measure(tmptxt)
            x = 2
            # if it's not the root node representing the starting position
            if self.tree.parent(item) != '':
                # get the ply num from the beginning of the string
                # e.g. 1. vs 1...
                dotind = tmptxt.find('.')
                move_num = int(tmptxt[0:dotind])
                ply_num = (move_num - 1) * 2
                # if it's black's turn
                if tmptxt[dotind+1] == '.':
                    ply_num += 1
                ply_num += 1
                # bumping up the depth width because seems to work better
                x = x + (ply_num * 20.5)
                # x = x + (ply_num * 21)
            w = x + tw
            if w > max_w:
                max_w = w
            # print(x, w, max_w, tmptxt)
        self.tree.column('#0', minwidth=int(max_w))

    def horz_scrollbar_magic_bbox(self):
        # magic to get horizontal scroll bar to work
        # get the width of the top item and set the minwidth of the tree to the width
        # all items will have the same width, so arbitrarily looking at the first one.
        # if using the column parameter, then each item has a different width
        # bbox = self.tree.bbox(all_items[p], column='#0')
        top_items = self.tree.get_children('')
        if len(top_items) > 0:
            # returns a 4tuple if the item is visible, empty string otherwise
            bbox = self.tree.bbox(top_items[0])
            items = self.tree.tag_has('all')

            # font = self.tree.configure('font')
            # font = self.tree.tag_configure('all', 'font')
            # font = self.tree.tag_configure('all', 'background')
            # font = self.tree.tag_configure('sel_var', 'font')
            # print('font', font, len(items))
            max_w = 0
            w = 0
            # if bbox != '':
            #     max_w = bbox[2]
            for q in range(0, len(items)):
                bbox = self.tree.bbox(items[q], column='#0')
                if bbox != '':
                    # the x value
                    x = bbox[0]
                    # # temporary kludge
                    # num_levels = (x - 2)//20
                    # x = ((num_levels + 4) * 20) + 2
                    tmptxt = self.tree.item(items[q], 'text')
                    tw = self.font.measure(tmptxt)
                    # twa = self.font_actual.measure(tmptxt)
                    w = x + tw
                    # if bbox[0] + bbox[2] > w:
                    #     w = bbox[0] + bbox[2]
                    #     print('override!!!')
                    if w > max_w:
                        max_w = w
                    # print(x, tw, twa, w, max_w, tmptxt)
                    print(x, tw, w, max_w, bbox[2], tmptxt)
            print('max_w', max_w)
            # adding a fudge factor found empirically
            fudge = 15
            max_w +- fudge
            self.tree.column('#0', minwidth=max_w)
            # This works to tighten the columns back down, but needs this routine to
            # happen on vertical scroll, or stuff disappears
            # if self.tree.column('#0', option='width') > max_w:
            #     self.tree.column('#0', width=max_w)

            # self.tree.column('#0', minwidth=max_w)
            # self.tree.column('#0', minwidth=1000)
            # self.tree.column('#0', minwidth=520)

    def update_tree(self, moves, next_move):
        # select the node of the current move by traversing through the moves.
        # the premise is that all the moves are in the tree
        tree_node = self.get_root_node()
        for p in range(0, len(moves)):
            tmp_next_move = moves[p]
            # !!!this bit is candidate for turning into a routine
            childrenIDs = self.tree.get_children(tree_node)
            # should always pass this if, since the premise is that all moves are in the tree
            if len(childrenIDs) > 0:
                for q in range(0, len(childrenIDs)):
                    tmptext = self.tree.item(childrenIDs[q], 'text')
                    tmptext_bits = tmptext.split(' ')
                    tmptext = tmptext_bits[1]

                    if tmptext == tmp_next_move:
                        break
                tree_node = childrenIDs[q]
        self.tree.selection_set(tree_node)
        # self.tree.see(tree_node)
        self.update_tree_selection_2ndary(next_move)

    def update_tree_selection_2ndary(self, next_move):
        # untag the previous selection variation
        # premise is that there is at most one
        tagged_ids = self.tree.tag_has("sel_var")
        if len(tagged_ids) > 0:
            self.tree.item(tagged_ids[0], tags='all')

        # get the selected node of the tree
        selected_node = self.get_selected_node()

        # tag the new selection variation
        # !!!this bit is candidate for turning into a routine
        childrenIDs = self.tree.get_children(selected_node)
        if len(childrenIDs) > 0:
            for q in range(0, len(childrenIDs)):
                tmptext = self.tree.item(childrenIDs[q], 'text')
                tmptext_bits = tmptext.split(' ')
                tmptext = tmptext_bits[1]

                if tmptext == next_move:
                    break
            self.tree.item(childrenIDs[q], tags=['sel_var', 'all'])
            # self.tree.see(childrenIDs[q])

    def diddle_var_tree(self, diddle):
        sel_secondary_items = self.tree.tag_has("sel_var")
        if len(sel_secondary_items) > 0:
            sel_secondary_item = sel_secondary_items[0]

        index = self.tree.index(sel_secondary_item)

        if diddle == 'remove':
            self.tree.delete(sel_secondary_item)
        else:
            # get the selected node of the tree
            selected_node = self.get_selected_node()
            if diddle == 'promote2main':
                new_index = 0
            elif diddle == 'promote':
                new_index = index - 1
            elif diddle == 'demote':
                new_index = index + 1
            self.tree.move(sel_secondary_item, selected_node, new_index)

    def add_move_to_tree(self, san_str):
        # get the selected node of the tree
        selected_node = self.get_selected_node()
        # add the current move at the end of the selected node's children
        self.tree.insert(selected_node, "end", text=san_str, open=True, tags='all')

    def open_all(self, bool_in):
        items = self.tree.tag_has('all')
        for q in range(0, len(items)):
            self.tree.item(items[q], open=bool_in)
        # if closing, make sure that it's at least open to the current move
        if not bool_in:
            node = self.get_selected_node()
            self.tree.see(node)
            self.tree.item(node, open=True)

    def get_selected_node(self):
        selected_node = self.get_root_node()
        sel_items = self.tree.selection()
        if len(sel_items) > 0:
            selected_node = sel_items[0]
        return selected_node

    # get the initial position node
    # assumes exactly one initial node, representing the starting position
    def get_root_node(self):
        rootIDs = self.tree.get_children('')
        return rootIDs[0]

class App(object):
    def __init__(self, parent=None):
        self.title_str = 'python chess tree, Colin Davey v alpha'
        self.parent = parent
        self.parent.title(self.title_str)

        # be prepared to close the tree window when closing main window
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        vp = 'W'

        # we have create both a model and a view within the controller
        # the controller doesn't inherit from either model or view

        # Create the chess model (cm)
        self.cm = ChessModelAPI()

        self.state_str = self.cm.init_state(vp)

        self.top = Frame(self.parent)
        # self.top.pack(side=TOP, fill=BOTH, expand=True)
        # self.top.pack(side=TOP, fill=BOTH)
        self.top.pack(side=TOP)

        self.left = Frame(self.top)
        # self.left.pack(side=LEFT, fill=BOTH, expand=True)
        self.left.pack(side=LEFT)

        # Create the board view (bv)
        self.bv = BoardView(self.left, vp=vp)

        # Create the controls (c)
        # self.c = Controls(self.parent)
        self.c = Controls(self.left)

        # Configure board view
        # this binds the handle_click method to the view's canvas for left button down
        self.bv.canvas.bind("<Button-1>", self.handle_bv_click)

        # Configure controls
        self.c.backFullBtn.config(command=self.move_back_full)
        self.c.backBtn.config(command=self.move_back)
        self.c.frwdBtn.config(command=self.move_frwd)
        self.c.frwdFullBtn.config(command=self.move_frwd_full)

        self.c.removeVarBtn.config(command=self.remove_var)
        self.c.promote2MainVarBtn.config(command=self.promote2main_var)
        self.c.promoteVarBtn.config(command=self.promote_var)
        self.c.demoteVarBtn.config(command=self.demote_var)

        self.c.commentBtn.config(command=self.handle_comment_button)
        self.c.next_move_str.trace('w', self.next_move_str_trace)

        self.c.openBtn.config(command=self.open_all)
        self.c.closeBtn.config(command=self.close_all_but_current)

        # start of right frame for vertical listing
        self.right = Frame(self.top)
        self.right.pack(side=LEFT, fill=BOTH, expand=True)

        self.right_top = Frame(self.right)
        self.right_top.pack(side=TOP)
        self.loadBtn = tk.Button(self.right_top, text="Load")
        self.loadBtn.pack(side=LEFT)
        self.saveBtn = tk.Button(self.right_top, text="Save")
        self.saveBtn.pack(side=LEFT)

        self.loadBtn.config(command=self.load_pgn)
        self.saveBtn.config(command=self.save_pgn)

        self.right_top2 = Frame(self.right)
        self.right_top2.pack(side=TOP)

        self.vp = IntVar()
        if vp == 'W':
            self.vp.set(1)
        else:
            self.vp.set(0)

        self.rb_w = Radiobutton(self.right_top2, text="White", variable=self.vp, value=1, command=self.set_player)
        self.rb_w.pack(side=LEFT)
        self.rb_b = Radiobutton(self.right_top2, text="Black", variable=self.vp, value=0, command=self.set_player)
        self.rb_b.pack(side=LEFT)

        # self.cl = tk.Label(self.right, text='Game listing will go here.', bg='#eee')
        # self.cl.pack(side=TOP, fill=BOTH, expand=True)
        self.cl = ChessListing(self.right)
        self.cl.table.bind("<Button-1>", self.handle_cl_click)

        # Create the chess tree (ct)
        self.bottom = Frame(self.parent)
        self.bottom.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.ct = ChessTree(self.bottom)
        self.ct.tree.bind("<<TreeviewSelect>>", self.handle_tree_select_builtin)
        # new tree for built-in
        self.make_tree_builtin()
        # initialize separate windows, which don't exist yet
        self.ce_root = None

        # initialize some variables
        self.click1 = []
        self.legal_dests = []
        # self.click1_b = False

    def load_pgn(self):
        # get filename
        filename = filedialog.askopenfilename(filetypes=[('pgn files', '*.pgn')])
        print("loading ", filename)
        if filename != '':
            # self.vp is a control variable attached to the White/Black radio buttons
            vp = color_bool2char(self.vp.get())
            self.state_str = self.cm.load_pgn(filename, vp)
            print(self.state_str["game_py"])
            self.update_display()
            self.make_tree_builtin()
        # put the focus back on the tree so keyboard works.
        self.parent.lift()
        # self.ct.tree.focus_force()
        self.ct.tree.focus_set()

    def open_all(self):
        self.ct.open_all(True)

    def close_all_but_current(self):
        self.ct.open_all(False)

    def run(self):
        self.update_display()
        tk.mainloop()

    def set_player(self):
        # self.vp is a control variable attached to the White/Black radio buttons
        vp = color_bool2char(self.vp.get())
        self.bv.set_player(vp)
        self.bv.update_display(self.state_str["piece_distrib"])
        self.state_str = self.cm.set_headers(self.state_str, vp)
        self.ct.update_tree_node(self.state_str["game_py"], self.ct.get_root_node())

    # close the comment window when closing main window
    def on_closing(self):
        if self.ce_root is not None:
            self.ce_root.destroy()
        self.parent.destroy()

    def handle_comment_button(self):
        if self.ce_root is None:
            self.ce_root = Tk()
            self.ce_root.title(self.title_str + '. Comment editor')
            self.ce_root.protocol("WM_DELETE_WINDOW", self.on_closing_comment_editor)
            self.ce = CommentEditor(self.ce_root)

            screenw = self.parent.winfo_screenwidth()
            screenh = self.parent.winfo_screenheight()
            self.ce_root.update_idletasks()
            # geo = [w, h, x, y]
            ce_geo = geo_str2list(self.ce_root.geometry())
            parent_geo = geo_str2list(self.parent.geometry())
            # put left of ce against right of parent
            ce_geo[2] = parent_geo[2] + parent_geo[0]
            # if right of ce off screen, then
            if ce_geo[2] + ce_geo[0] > screenw:
                # put right of ce against right of screen
                ce_geo[2] = screenw - ce_geo[0]
            self.ce_root.geometry("%dx%d+%d+%d" % tuple(ce_geo))
            # don't let it get too small for the button to show
            self.ce_root.minsize(width=ce_geo[0], height=ce_geo[1])

            self.ce.save_button.config(command=self.save_comment)

        self.update_ce()
        # low level tk stuff
        self.ce_root.lift()
        self.ce_root.update()

    def save_pgn(self):
        # get filename
        filename = filedialog.asksaveasfilename(defaultextension='.pgn')
        if filename != '':
            self.cm.save_pgn(self.state_str, filename)

    def handle_cl_click(self, event):
        moves = self.cl.handle_click(event)
        print(moves)
        if len(moves) > 0:
            self.state_str = self.cm.move_to(self.state_str, moves)
            self.update_display()
            self.close_all_but_current()

    def handle_bv_click(self, event):
        self.bv.update_display(self.state_str["piece_distrib"])

        click_location = self.bv.get_click_location(event)
        print('click:', click_location.file, click_location.rank)

        # If clicked on piece of side w turn, then it's click1.
        #   highlight the piece and all legal moves
        valid_click, legal_dests = self.get_legal_dests_from(click_location)
        if valid_click:
            self.click1 = click_location
            self.legal_dests = legal_dests

            self.bv.draw_highlights(self.legal_dests)
            self.bv.draw_highlights([click_location])

        else:
            # if we didn't just do the click1, and there is a click1 stored, then it might be the click2
            if self.click1 != []:
                click2 = click_location
                for dest in self.legal_dests:
                    if click2.file == dest.file and click2.rank == dest.rank:
                        self.move(self.click1, click2)
                        break

            # reset
            self.click1 = []
            self.legal_dests = []

    def get_legal_dests_from(self, board_coords):
        if get_piece_color(self.state_str["piece_distrib"][board_coords.rank][board_coords.file]) != self.state_str["turn"]:
            return False, []
        start_coord = file_rank2str(board_coords.file, board_coords.rank)
        legal_moves = list(filter(lambda m : m[0:2] == start_coord, self.state_str["legal_moves"]))
        # maps e.g. ["e2e3", "e2e4"] to ["e3", "e4"] to [{f : 4, r : 2}, {f : 4, r : 3}]
        dest_list = list(map(
            lambda m : BoardCoords(ord(m[2]) - ord('a'), ord(m[3]) - ord('1')),
            legal_moves))
        return True, dest_list

    def remove_var(self):
        self.diddle_var('remove')
        self.c.update_display(self.state_str["has_parent"], self.state_str["variations"])

    def promote2main_var(self):
        self.diddle_var('promote2main')

    def promote_var(self):
        self.diddle_var('promote')

    def demote_var(self):
        self.diddle_var('demote')

    def check_comment(self):
        ret_val = True
        if self.ce_root is not None:
            print('edited ', self.ce.editor.edit_modified())
            if self.ce.editor.edit_modified():
                resp = messagebox.askyesnocancel('Save comment?', 'The comment has been edited. Save?')
                if resp is None:
                    ret_val = False
                elif resp is True:
                    self.save_comment()
        return ret_val

    ##############################
    # change board state
    ##############################
    def save_comment(self):
        comment = self.ce.editor.get(1.0, END)
        comment = comment[0:-1]
        print('comment:', comment)
        self.state_str = self.cm.set_comment(self.state_str, comment)
        self.ce.save_button.configure(state=tk.DISABLED)
        self.ce.editor.edit_modified(False)
        self.ct.update_tree_node(self.state_str["node_py"], self.ce.tree_node)

    def diddle_var(self, diddle):
        san = self.c.next_move_str.get()
        self.state_str = self.cm.diddle_var(self.state_str, diddle, san)
        self.diddle_var_tree(diddle)
        # self.c.update_display(self.state_str["has_parent"], self.state_str["variations"])
        if diddle == 'remove':
            san = ''
        self.c.update_next_move_option_menu(self.state_str["variations"], san)

    # moves

    # from tree click
    def move_to_tree_node(self):
        if self.ct.handle_tree_select():
            if self.check_comment():
                # get the moves from the beginning of the game to the selected tree node
                moves = self.ct.get_tree_moves()
                self.state_str = self.cm.move_to(self.state_str, moves)
                self.update_display()

    # from buttons
    def move_back_full(self):
        if self.check_comment():
            self.state_str = self.cm.move_back_full(self.state_str)
            self.update_display()
            self.close_all_but_current()

    def move_back(self):
        if self.check_comment():
            self.state_str = self.cm.move_back(self.state_str)
            self.update_display()
            self.close_all_but_current()

    # from board click
    def move(self, click1, click2):
        if self.check_comment():
            self.state_str, added, san, move_str = self.cm.move_add(self.state_str, click1, click2)
            if added:
                # update the tree
                self.ct.add_move_to_tree(move_str)
                # update the option menu? not necessary, since we're about to leave
            self.state_str = self.cm.move_frwd(self.state_str, san)
            self.update_display()

    def move_frwd(self):
        if self.check_comment():
            self.state_str = self.cm.move_frwd(self.state_str, self.c.next_move_str.get())
            self.update_display()
            self.close_all_but_current()

    def move_frwd_full(self):
        if self.check_comment():
            self.state_str = self.cm.move_frwd_full(self.state_str)
            self.update_display()
            self.close_all_but_current()

    # END moves

    ##############################
    # END change board state
    ##############################

    def update_display(self):
        self.bv.update_display(self.state_str["piece_distrib"])
        self.c.update_display(self.state_str["has_parent"], self.state_str["variations"])
        # make sure the appropriate tree node is selected based on the current move
        # and the appropriate variation of the move is secondary selected
        next_move = self.c.next_move_str.get()
        # for built-in
        self.ct.update_tree(self.state_str["moves"], next_move)
        self.cl.update_listing(self.state_str["moves"])
        self.update_ce()
        self.ct.horz_scrollbar_magic()

    def update_ce(self):
        if self.ce_root is not None:
            comment = self.state_str["comment"]
            self.ce.editor.replace(1.0, END, comment)
            self.ce.save_button.configure(state=tk.DISABLED)
            self.ce.editor.edit_modified(False)
            # this is only necessary in case the user makes the next node by clicking on the tree.
            # otherwise, we could just use the selected node at that time.
            self.ce.tree_node = self.ct.get_selected_node()

    def make_tree_builtin(self):
        # new tree for built-in
        self.ct.make_tree(self.state_str["game_py"])
        self.ct.horz_scrollbar_magic()

    # when the next move menu changes, next_move_str changes bringing control to here.
    # this routine updates the tree.
    # we don't use the last three parameters
    def next_move_str_trace(self, a, b, c):
        next_move = self.c.next_move_str.get()
        # for built-in
        self.ct.update_tree_selection_2ndary(next_move)

    # for built-in
    def handle_tree_select_builtin(self, event):
        self.move_to_tree_node()

    # change the tree to reflect a change in the chess model
    def diddle_var_tree(self, diddle):
        # for built-in
        self.ct.diddle_var_tree(diddle)
        next_move_str = self.c.next_move_str.get()
        self.c.next_move_str.set(next_move_str)

    def on_closing_comment_editor(self):
        self.ce_root.destroy()
        self.ce_root = None


if __name__ == "__main__":
    # if not os.path.exists(DATA_DIR):
    #     ''' basic check - if there are files missing from the data directory, the
    #     program will still fail '''
    #     # dl = raw_input("Cannot find chess images directory.  Download from website? (Y/n)")
    #     dl = input("Cannot find chess images directory.  Download from website? (Y/n)")
    #     if dl.lower() == "n":
    #         print("No image files found, quitting.")
    #         exit(0)
    #     print("Creating directory: %s" % os.path.join(os.getcwd(), DATA_DIR))
    #     import urllib
    #
    #     os.mkdir(DATA_DIR)
    #     url_format = "http://python4kids.files.wordpress.com/2013/04/%s"
    #     for k, v in TILES.items():
    #         url = url_format % v
    #         target_filename = os.path.join(DATA_DIR, v)
    #         print("Downloading file: %s" % v)
    #         urllib.request.urlretrieve(url, target_filename)

    the_parent = tk.Tk()
    app = App(the_parent)
    app.run()
