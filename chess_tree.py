# /usr/bin/python

import tkinter as tk
from tkinter import *
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


# BASED ON
# Representing a chess set in Python
# Part 2
# Brendan Scott
# 27 April 2013
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
        # self.vp = 'W'
        # self.vp = 'B'

    def set_player(self, val):
        self.vp = color_bool2char(val)

    def get_click_location(self, event):
        # Handle a click received.  The x,y location of the click on the canvas is at
        # (event.x, event.y)
        # translate the event coordinates (ie the x,y of where the click occurred)
        # into a position on the chess board

        f = event.x // TILE_WIDTH
        if f == 8:
            f = 7
        # the / operator is called integer division
        # it returns the number of times TILE_WIDTH goes into event.x ignoring any remainder
        # eg: 2/2 = 1, 3/2 = 1, 11/5 = 2 and so on
        # so, it should return a number between 0 (if x < TILE_WIDTH) though to 7
        r = event.y // TILE_WIDTH
        if r == 8:
            r = 7
        # reversing rank/file as necessary for W/B
        r = self.flip_y_r(r)
        f = self.flip_x_f(f)
        return BoardLocation(f, r)

    def update_display(self, cm):
        """ draw an empty board then draw each of the
        pieces in the board over the top"""

        # first draw the empty board
        # then draw the pieces
        # if the order was reversed, the board would be drawn over the pieces
        # so we couldn't see them
        self.clear_canvas()
        self.draw_empty_board()
        self.draw_pieces(cm)

    def clear_canvas(self):
        """ delete everything from the canvas"""
        items = self.canvas.find_all()
        for i in items:
            self.canvas.delete(i)

    def draw_tile(self, f, r, tile):
        # reversing rank/file as necessary for W/B
        x = self.flip_x_f(f) * TILE_WIDTH
        y = self.flip_y_r(r) * TILE_WIDTH
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

    def draw_pieces(self, cm):
        for r in range(0, 8):
            for f in range(0, 8):
                piece = cm.get_piece_at(BoardLocation(f, r))
                if piece == EMPTY_SQUARE:
                    continue  # skip empty tiles
                tile = self.images[piece]
                self.draw_tile(f, r, tile)

    def draw_highlights(self, highlight_list):
        tile = self.images['highlight_tile']
        for p in range(0, len(highlight_list)):
            f = highlight_list[p].f
            r = highlight_list[p].r
            self.draw_tile(f, r, tile)

    # reversing rank so rank 0 is the bottom (chess) rather than top (tk) for White
    def flip_y_r(self, in_val):
        out_val = in_val
        if self.vp == 'W':
            out_val = 7 - out_val
        return out_val

    # reversing file so file 0 is the right (chess) rather than top (tk) for Black
    def flip_x_f(self, in_val):
        out_val = in_val
        if self.vp == 'B':
            out_val = 7 - out_val
        return out_val


class BoardLocation(object):
    def __init__(self, f, r):
        self.f = f
        self.r = r

#####################################
# Utility Functions


def geo_str2list(geo_str):
    geo_str = geo_str.replace('+', ' ')
    geo_str = geo_str.replace('x', ' ')
    geo = geo_str.split(' ')
    geo = [int(i) for i in geo]
    return geo

def game_node2moves(game_node):
    moves = []
    tmp_node = game_node
    while tmp_node.parent is not None:
        moves.append(tmp_node.san())
        tmp_node = tmp_node.parent
    moves.reverse()
    return moves

def get_numbered_moves(game_node):
    moves = game_node2moves(game_node)
    # add the numbers to all of white's moves
    for p in range(0, len(moves), 2):
        san = moves[p]
        moves[p] = str(p // 2 + 1) + '. ' + san
    return moves

def print_listing_vertical(game_node):
    moves = get_numbered_moves(game_node)
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


def print_listing_horizontal(game_node):
    moves = get_numbered_moves(game_node)
    num_moves = len(moves)
    tmpstr = ''
    for p in range(0, num_moves):
        tmpstr += moves[p]
        if p != num_moves - 1:
            tmpstr += ' '
    print(tmpstr)
    return tmpstr


def get_plie_num(game_node):
    move_num = game_node.parent.board().fullmove_number
    plie_num = (move_num - 1) * 2
    if not game_node.parent.board().turn:
        plie_num += 1
    return plie_num

def make_brief_comment_str(game_node):
    comment_str = game_node.comment
    if comment_str != "":
        # strip out new lines
        comment_str = comment_str.replace('\n' ,' ')
        # if comment is too long, shorten it and append "..."
        max_comment_str_len = 50
        if len(comment_str) > max_comment_str_len:
            comment_str = comment_str[0:max_comment_str_len] + '...'
        comment_str = ' {' + comment_str + '}'
    return comment_str

def print_game_node(game_node, init_plie_num=0):
    move_num = game_node.parent.board().fullmove_number
    plie_num = get_plie_num(game_node)
    # assuming it's white's turn
    turn_str = str(move_num) + '.'
    # if it's black's turn
    if not game_node.parent.board().turn:
        turn_str += '..'
    turn_str += ' '
    spaces = ''
    for q in range(0, plie_num-(init_plie_num+1)):
        spaces += '  '
    end_str = ""
    if game_node.is_end():
        end_str = " *"
    comment_str = make_brief_comment_str(game_node)
    str_out = turn_str + game_node.san() + comment_str
    print(spaces + str_out + end_str)
    return str_out


def print_game_node_hybrid(game_node):
    print_listing_horizontal(game_node)
    print_game_node_recur(game_node, True)


def print_game_node_recur(game_node, initial=False, plie_num=0):
    # if game_node.parent is not None:
    if initial:
        if game_node.parent is not None:
            plie_num = get_plie_num(game_node)
    else:
        print_game_node(game_node, init_plie_num=plie_num)
    if not game_node.is_end():
        for p in range(0, len(game_node.variations)):
            print_game_node_recur(game_node.variations[p], plie_num=plie_num)


def get_piece_color(piece):
    if piece == EMPTY_SQUARE:
        return ' '
    elif piece.lower() == piece:
        return 'B'
    else:
        return 'W'

def color_bool2char(bool_in):
    if bool_in:
        return 'W'
    else:
        return 'B'

# file and rank inds to square name (e.g. "a1")
def fr2str(file, rank):
    # return chess.FILE_NAMES[file] + chess.RANK_NAMES[rank]
    return chess.SQUARE_NAMES[chess.square(file, rank)]


class PChessGameModel(object):
    def __init__(self, vp):
        """create a chess board with pieces positioned for a new game
        row ordering is reversed from normal chess representations
        but corresponds to a top left screen coordinate
        """
        # board model
        self.board = chess.Board()
        # pgn model
        self.game = chess.pgn.Game()
        self.node = self.game
        self.set_headers(vp)

    def set_headers(self, vp):
        if vp == 'W':
            self.game.headers["White"] = 'Me'
            self.game.headers["Black"] = 'Opponent'
        else:
            self.game.headers["White"] = 'Opponent'
            self.game.headers["Black"] = 'Me'

    def get_legal_moves_from(self, bl):
        # board model
        piece = self.board.piece_at(chess.square(bl.f, bl.r))
        dest_list = []
        if piece is not None:
            if piece.color == self.board.turn:
                start_fr = fr2str(bl.f, bl.r)
                legal_moves = self.board.legal_moves
                print('legal moves:')
                for f in range(0, 8):
                    for r in range(0, 8):
                        if not (f == bl.f and r == bl.r):
                            tmp_fr = fr2str(f, r)
                            if chess.Move.from_uci(start_fr + tmp_fr) in legal_moves:
                                print(tmp_fr)
                                dest_list.append(BoardLocation(f, r))
        return dest_list

    def get_piece_at(self, bl):
        # board model
        piece = self.board.piece_at(chess.square(bl.f, bl.r))
        # !!! This works. Do I need board at all? Just use game/nodes?
        # piece = self.node.board().piece_at(chess.square(f, r))
        piece_symbol = EMPTY_SQUARE
        if piece is not None:
            piece_symbol = piece.symbol()
        return piece_symbol

    def get_turn_color(self):
        # board model
        return color_bool2char(self.board.turn)

    ###########################
    # moves
    ###########################

    def move_back_full(self):
        # board model
        self.board = chess.Board()
        # pgn model
        self.node = self.game
        self.report()

    def move_back(self):
        # board model
        self.board.pop()

        # pgn model
        self.node = self.node.parent
        self.report()

    def move_frwd(self, san):
        p = self.get_var_ind_from_san(san)
        # board model
        self.board.push_san(san)
        # pgn model
        self.node = self.node.variations[p]
        self.report()

    # def move_frwd_full(self):
    #     # p = self.get_var_ind_from_san(san)
    #     # # board model
    #     # self.board.push_san(san)
    #     # # pgn model
    #     # self.node = self.node.variations[p]
    #     # self.report()
    #     pass

    def move_to(self, moves):
        # board model
        self.board = chess.Board()

        # pgn model
        self.node = self.game

        for p in range(0, len(moves)):
            # pgn model
            ind = self.get_var_ind_from_san(moves[p])
            # self.node = self.node.variation(chess.Move.from_uci(uci))
            self.node = self.node.variation(ind)
            # board model
            self.board.push_san(moves[p])
        self.report()

    # def move(self, start, destination):
    #     print('move:', start.f, start.r, destination.f, destination.r)
    #     uci = fr2str(start.f, start.r) + fr2str(destination.f, destination.r)
    #
    #     # board model
    #     self.board.push_uci(uci)
    #
    #     # pgn model
    #     if self.node.parent is None and len(self.game.variations) == 0:
    #         self.node = self.game.add_variation(chess.Move.from_uci(uci))
    #     else:
    #         if not self.node.has_variation(chess.Move.from_uci(uci)):
    #             self.node = self.node.add_variation(chess.Move.from_uci(uci))
    #         else:
    #             self.node = self.node.variation(chess.Move.from_uci(uci))
    #     self.report()

    def move_add(self, start, destination):
        print('move:', start.f, start.r, destination.f, destination.r)
        uci = fr2str(start.f, start.r) + fr2str(destination.f, destination.r)

        # pgn model
        # !!!redundant test? len(self.game.variations) == 0 implies self.node.parent is None?
        if self.node.parent is None and len(self.game.variations) == 0:
            # self.node = self.game.add_variation(chess.Move.from_uci(uci))
            node = self.game.add_variation(chess.Move.from_uci(uci))
        else:
            # self.node = self.node.add_variation(chess.Move.from_uci(uci))
            node = self.node.add_variation(chess.Move.from_uci(uci))
        return print_game_node(node)

    def move_exists(self, start, destination):
        uci = fr2str(start.f, start.r) + fr2str(destination.f, destination.r)
        return self.node.has_variation(chess.Move.from_uci(uci))

    def san(self, start, destination):
        uci = fr2str(start.f, start.r) + fr2str(destination.f, destination.r)
        return self.node.board().san(chess.Move.from_uci(uci))

    # ##############################
    # pgn model only below here
    # ##############################

    def get_comment(self):
        return self.node.comment

    def set_comment(self, comment):
        self.node.comment = comment

    def diddle_var(self, diddle, san):
        print(diddle + 'Var')
        p = self.get_var_ind_from_san(san)
        if diddle == 'remove':
            self.node.remove_variation(self.node.variations[p].move)
        elif diddle == 'promote2main':
            self.node.promote_to_main(self.node.variations[p].move)
        elif diddle == 'promote':
            self.node.promote(self.node.variations[p].move)
        elif diddle == 'demote':
            self.node.demote(self.node.variations[p].move)
        self.report()

    # Assumes Var exists, should never get here if it doesn't. Intended for getting variation from san in dropdown menu
    def get_var_ind_from_san(self, san):
        for p in range(0, len(self.node.variations)):
            # !!!can/should I use board in variations instead?
            # If can, then should. I think self.node.board().san
            if san == self.board.san(self.node.variations[p].move):
                return p

    def report(self):
        # print('pgn:')
        # print(self.game)
        # print('tree:')
        # print_game_node_recur(self.game, True)
        # print('listing:')
        # print_listing_vertical(self.node)
        # print('horizontal listing:')
        # print_listing_horizontal(self.node)
        # print('hybrid horizontal tree:')
        # print_game_node_hybrid(self.node)
        pass

    def save_pgn(self, filename):
        f = open(filename, 'w')
        print(self.game, file=f)
        f.close()
        # f = open(filename+'.epd', 'w')
        # epd = self.node.board().epd()
        # print(epd, file=f)
        # f.close()
        # print(epd)

    def load_pgn(self, filename):
        f = open(filename)
        # !!!Is setting to None necessary or useful? Thinking memory leak.
        self.game = None
        self.game = chess.pgn.read_game(f)
        print(self.game)
        f.close()
        # !!!Error handling
        # board model
        # !!!Is setting to None necessary or useful? Thinking memory leak.
        self.board = None
        self.board = chess.Board()
        # pgn model
        self.node = self.game


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

    def update_next_move_option_menu(self, cm, next_move_str=''):
        # reconfigure the listbox of next moves based on the current node
        # empty the listbox
        self.next_move_str.set('')
        self.nextMoveOMen['menu'].delete(0, 'end')
        # fill new_vals with moves from the available variations
        new_vals = []
        for p in range(0, len(cm.node.variations)):
            new_vals.append(cm.node.variations[p].san())
        # fill the listbox with the new_vals
        for val in new_vals:
            # !!!maybe do self.next_move_str.set(val) ?
            self.nextMoveOMen['menu'].add_command(label=val, command=tk._setit(self.next_move_str, val))
        # if there are variations, set it to the first one
        if len(new_vals) > 0:
            if next_move_str != '':
                self.next_move_str.set(next_move_str)
            else:
                self.next_move_str.set(new_vals[0])
        # else:
        #     self.nextMoveOMen['menu'].add_command(label='<none>')
        #     self.next_move_str.set('')


    def update_display(self, cm):
        self.update_next_move_option_menu(cm)

        # diable back button if can't go back no more
        new_state = tk.NORMAL
        # if cm.node.board().fullmove_number == 1 and cm.node.board().turn:
        if cm.node.parent is None:
            new_state = tk.DISABLED
        self.backBtn.config(state=new_state)
        self.backFullBtn.config(state=new_state)

        # diable all the buttons if there are no variations
        # because of above, len(new_vals) == 0 is equiv to no variations
        new_state = tk.NORMAL
        if len(cm.node.variations) == 0:
            new_state = tk.DISABLED
        self.frwdBtn.config(state=new_state)
        self.frwdFullBtn.config(state=new_state)
        self.removeVarBtn.config(state=new_state)
        self.promote2MainVarBtn.config(state=new_state)
        self.promoteVarBtn.config(state=new_state)
        self.demoteVarBtn.config(state=new_state)

        # self.horzListLabel.configure(text=print_listing_horizontal(cm.node))


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

class ChessTree(tk.Frame):
    def __init__(self, parent=None, do_grid=False):
        tk.Frame.__init__(self, parent)

        # For built-in, Grid doesn't work, Pack does.
        #   Grid dies before ap shows up
        # However, on separate window, the opposite.
        #   Pack fails on Tree button with
        # "'Controller' object has no attribute 'pack'"
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
        self.tree_game_node_recur(game, initial_node, True)

    def tree_game_node_recur(self, game_node, parent, initial=False):
        # if game_node.parent is not None:
        if not initial:
            the_str = print_game_node(game_node)
            parent = self.tree.insert(parent, "end", text=the_str, open=True, tags='all')
        if not game_node.is_end():
            for p in range(0, len(game_node.variations)):
                self.tree_game_node_recur(game_node.variations[p], parent)

    # tree changes due to clicks or key presses allow actions on tree selection changes
    # otherwise not
    # prevents handle_tree_select from running unless it was a direct result of a click,
    # or key press as opposed to programatically
    def handle_tree_click(self, event):
        self.tree_clicked = True

    def update_tree_node(self, game_node, tree_node):
        if game_node.parent is None:
            the_str = self.get_init_node_str(game_node) + ' ' + make_brief_comment_str(game_node)
        else:
            the_str = print_game_node(game_node)
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
                # get the plie num from the beginning of the string
                # e.g. 1. vs 1...
                dotind = tmptxt.find('.')
                move_num = int(tmptxt[0:dotind])
                plie_num = (move_num - 1) * 2
                # if it's black's turn
                if tmptxt[dotind+1] == '.':
                    plie_num += 1
                plie_num += 1
                # bumping up the depth width because seems to work better
                x = x + (plie_num * 20.5)
                # x = x + (plie_num * 21)
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
            # this bit is candidate for turning into a routine
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

class Controller(object):
    def __init__(self, parent=None, model=None):
        self.title_str = 'python chess tree, Colin Davey v alpha'
        self.parent = parent
        self.parent.title(self.title_str)

        # be prepared to close the tree window when closing main window
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        vp = 'W'

        # we have create both a model and a view within the controller
        # the controller doesn't inherit from either model or view

        # Create the chess model (cm)
        if model is None:
            self.cm = PChessGameModel(vp)
        else:
            self.cm = model

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

    def open_all(self):
        self.ct.open_all(True)

    def close_all_but_current(self):
        self.ct.open_all(False)

    def run(self):
        self.update_display()
        tk.mainloop()

    def set_player(self):
        vp = self.vp.get()
        self.bv.set_player(vp)
        self.bv.update_display(self.cm)
        vpchar = color_bool2char(vp)
        self.cm.set_headers(vpchar)
        self.ct.update_tree_node(self.cm.game, self.ct.get_root_node())

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

    def load_pgn(self):
        # get filename
        filename = filedialog.askopenfilename(filetypes=[('pgn files', '*.pgn')])
        print("*** Filename1: ", filename)
        if filename != '':
            print("*** Filename2: ", filename)
            self.cm.load_pgn(filename)
            # self.vp is a control variable attached to the White/Black radio buttons
            vp = self.vp.get()
            vpchar = color_bool2char(vp)
            self.cm.set_headers(vpchar)
            self.update_display()
            self.make_tree_builtin()
        # put the focus back on the tree so keyboard works.
        self.parent.lift()
        # self.ct.tree.focus_force()
        self.ct.tree.focus_set()

    def save_pgn(self):
        # get filename
        filename = filedialog.asksaveasfilename(defaultextension='.pgn')
        if filename != '':
            self.cm.save_pgn(filename)

    def handle_cl_click(self, event):
        moves = self.cl.handle_click(event)
        print(moves)
        if len(moves) > 0:
            self.cm.move_to(moves)
            self.update_display()
            self.close_all_but_current()

    def handle_bv_click(self, event):
        click_location = self.bv.get_click_location(event)
        piece = self.cm.get_piece_at(click_location)
        print('click:', click_location.f, click_location.r, piece)

        click1_b = False
        self.bv.update_display(self.cm)

        # If clicked on piece of side w turn, then it's click1.
        #   highlight the piece and all legal moves
        if self.cm.get_turn_color() == get_piece_color(piece):
            self.click1 = click_location
            self.legal_dests = self.cm.get_legal_moves_from(click_location)
            click1_b = True

            # highlight the legal move squares and the clicked square
            highlight_list = self.legal_dests
            highlight_list.append(self.click1)
            self.bv.draw_highlights(highlight_list)

        click2_b = False
        # if we didn't just do the click1, and there is a click1 stored, then it might be the click2
        if (not click1_b) and (self.click1 != []):
            click2 = click_location
            for ind in range(0, len(self.legal_dests)):
                if click2.f == self.legal_dests[ind].f and click2.r == self.legal_dests[ind].r:
                    self.move(self.click1, click2)
                    self.click1 = []
                    self.legal_dests = []
                    click2_b = True
                    break

        # if it wasn't a click1 or click2, then reset
        if not click1_b and not click2_b:
            self.click1 = []
            self.legal_dests = []

    def remove_var(self):
        self.diddle_var('remove')
        self.c.update_display(self.cm)

    def promote2main_var(self):
        self.diddle_var('promote2main')

    def promote_var(self):
        self.diddle_var('promote')

    def demote_var(self):
        self.diddle_var('demote')

    def save_comment(self):
        node = self.cm.node
        # node = self.ce.node
        comment = self.ce.editor.get(1.0, END)
        comment = comment[0:-1]
        print('comment:', comment)
        # self.cm.set_comment(comment)
        # funky addressing member of cm node directly, but probably can't be helped...
        node.comment = comment
        self.ce.save_button.configure(state=tk.DISABLED)
        self.ce.editor.edit_modified(False)
        self.ct.update_tree_node(node, self.ce.tree_node)

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
    # moves
    ##############################

    # from board click
    def move(self, click1, click2):
        if self.check_comment():
            # self.cm.move(click1, click2)
            if not self.cm.move_exists(click1, click2):
                move_str = self.cm.move_add(click1, click2)
                # update the tree
                self.ct.add_move_to_tree(move_str)
                # update the option menu? not necessary, since we're about to leave
            san = self.cm.san(click1, click2)
            self.cm.move_frwd(san)
            self.update_display()

    # from tree click
    def move_to_tree_node(self):
        if self.ct.handle_tree_select():
            if self.check_comment():
                # get the moves from the beginning of the game to the selected tree node
                moves = self.ct.get_tree_moves()
                self.cm.move_to(moves)
                self.update_display()

    # from buttons
    def move_back_full(self):
        if self.check_comment():
            self.cm.move_back_full()
            self.update_display()
            self.close_all_but_current()

    def move_back(self):
        if self.check_comment():
            self.cm.move_back()
            self.update_display()
            self.close_all_but_current()

    def move_frwd(self):
        if self.check_comment():
            self.cm.move_frwd(self.c.next_move_str.get())
            self.update_display()
            self.close_all_but_current()

    def move_frwd_full(self):
        if self.check_comment():
            # get the moves from the beginning of the game to the selected tree node,
            # which is assumed to be the current game node
            moves = self.ct.get_tree_moves()
            # get the moves from the current game node to the end and append
            # !!!move this code to the game model class
            node = self.cm.node
            while not node.is_end():
                node = node.variations[0]
                moves.append(node.san())
            self.cm.move_to(moves)
            self.update_display()
            self.close_all_but_current()

    ##############################
    # END moves
    ##############################

    def diddle_var(self, diddle):
        san = self.c.next_move_str.get()
        self.cm.diddle_var(diddle, san)
        self.diddle_var_tree(diddle)
        # self.c.update_display(self.cm)
        if diddle == 'remove':
            san = ''
        self.c.update_next_move_option_menu(self.cm, san)

    def update_display(self):
        self.bv.update_display(self.cm)
        self.c.update_display(self.cm)
        # make sure the appropriate tree node is selected based on the current move
        # and the appropriate variation of the move is secondary selected
        moves = game_node2moves(self.cm.node)
        next_move = self.c.next_move_str.get()
        # for built-in
        self.ct.update_tree(moves, next_move)
        self.cl.update_listing(moves)
        self.update_ce()
        self.ct.horz_scrollbar_magic()

    def update_ce(self):
        if self.ce_root is not None:
            comment = self.cm.get_comment()
            self.ce.editor.replace(1.0, END, comment)
            self.ce.save_button.configure(state=tk.DISABLED)
            self.ce.editor.edit_modified(False)
            # this is only necessary in case the user makes the next node by clicking on the tree.
            # otherwise, we could just use the selected node at that time.
            self.ce.tree_node = self.ct.get_selected_node()

    def make_tree_builtin(self):
        # new tree for built-in
        self.ct.make_tree(self.cm.game)
        self.ct.horz_scrollbar_magic()

    # # make sure the appropriate tree node is selected based on the current move
    # # and the appropriate variation of the move is secondary selected
    # def update_tree(self):
    #     moves = game_node2moves(self.cm.node)
    #     next_move = self.c.next_move_str.get()
    #     # for built-in
    #     self.ct.update_tree(moves, next_move)

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
    c = Controller(the_parent)
    c.run()
