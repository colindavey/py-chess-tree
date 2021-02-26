# /usr/bin/python
import tkinter as tk

from dumb_board import DumbBoard
# from file_rank_square import board_coords
from file_rank_square import board_coords2square_name
from file_rank_square import square_name2board_coords

def get_piece_color(piece):
    if piece == '':
        return ''
    elif piece.lower() == piece:
        return 'B'
    else:
        return 'W'

class SmartBoard(tk.Frame):
    def __init__(self, parent, move_cb, is_white=True):
        self.db = DumbBoard(parent, self.handle_click, is_white)
        self.piece_distrib = []
        self.move_cb = move_cb
        self.legal_moves = []
        self.click1 = []
        self.legal_dests = []
        self.turn = 'W'

    ###########################################
    # Dumb board
    ###########################################
    # public
    def bv_set_player(self, is_white):
        self.db.db_set_player(is_white)

    # public
    def bv_update(self, piece_distrib, legal_moves, turn):
        self.legal_moves = legal_moves
        self.turn = turn
        self.bv_update_display(piece_distrib)

    # public/utility function
    def bv_update_display(self, piece_distrib):
        self.piece_distrib = piece_distrib
        self.db.db_update_display(piece_distrib)
        
    # user input
    def handle_click(self, event):
        click_coords = self.db.db_get_click_location(event)
        # This update_display is necessary for when clicking multiple valid click1 squares
        self.db.db_update_display(self.piece_distrib)
        # print('click:', click_coords["file"], click_coords["rank"])

        # If clicked on piece of side w turn, then it's click1.
        #   highlight the piece and all legal moves
        if get_piece_color(self.piece_distrib[click_coords["rank"]][click_coords["file"]]) == self.turn:
            self.click1 = click_coords
            legal_dests, legal_dest_coords = self.get_legal_dests_from(click_coords)
            self.legal_dests = legal_dests

            self.db.db_draw_highlights(legal_dest_coords)
            self.db.db_draw_highlights([click_coords])

        else:
            # if we didn't just do the click1, and there is a click1 stored, then it might be the click2
            if self.click1 != []:
                click2 = click_coords
                click2_str = board_coords2square_name(click2)
                # print(click2_str, self.legal_dests)
                if click2_str in self.legal_dests:
                    self.move_cb(self.click1, click2)

            # reset
            self.click1 = []
            self.legal_dests = []

    # private
    def get_legal_dests_from(self, board_coords):
        start_coord = board_coords2square_name(board_coords)
        # filter the legal moves down to those starting from the start_coord
        legal_moves = list(filter(lambda m : m[0:2] == start_coord, self.legal_moves))
        # e.g. maps ["e2e3", "e2e4"] to ["e3", "e4"] 
        legal_dests = list(map(lambda m : m[2:], legal_moves))
        # e.g. maps ["e3", "e4"]  to [{f : 4, r : 2}, {f : 4, r : 3}]
        legal_dest_coords = list(map(lambda m : square_name2board_coords(m), legal_dests))
        return legal_dests, legal_dest_coords

