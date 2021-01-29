# /usr/bin/python
import os
import os.path
import tkinter as tk

# from file_rank_square import BoardCoords
from file_rank_square import board_coords

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
    def __init__(self, parent=None, is_white=True):
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        self.canvas.pack()
        self.images = {}
        for image_file_name in TILES:
            f = os.path.join(DATA_DIR, TILES[image_file_name])
            if not os.path.exists(f):
                print("Error: Cannot find image file: %s at %s - aborting" % (TILES[image_file_name], f))
                exit(-1)
            self.images[image_file_name] = tk.PhotoImage(file=f)
            # This opens each of the image files, converts the data into a form that Tkinter
            # can use, then stores that converted form in the attribute self.images
            # self.images is a dictionary, keyed by the letters we used in our model to
            # represent the pieces - ie PRNBKQ for white and prnbkq for black
            # eg self.images['N'] is a PhotoImage of a white knight
            # this means we can directly translate a board entry from the model into a picture
        self.pack()
        self.is_white = is_white

    def set_player(self, is_white):
        self.is_white = is_white

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
        file_, rank = self.flip_file_rank(file_, rank)
        # return BoardCoords(file_, rank)
        return board_coords(file_, rank)

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
        x, y = self.flip_file_rank(file_, rank)
        self.canvas.create_image(x * TILE_WIDTH, y * TILE_WIDTH, anchor=tk.NW, image=tile)

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
                if piece == '':
                    continue  # skip empty tiles
                tile = self.images[piece]
                self.draw_tile(f, r, tile)

    def draw_highlights(self, highlight_list):
        tile = self.images['highlight_tile']
        for item in highlight_list:
            # self.draw_tile(item.file, item.rank, tile)
            self.draw_tile(item["file"], item["rank"], tile)

    # reversing rank so rank 0 is the bottom (chess) rather than top (tk) for White
    # reversing file so file 0 is the right (chess) rather than top (tk) for Black
    def flip_file_rank(self, file_, rank):
        if self.is_white:
            rank = 7 - rank
        else:
            file_ = 7 - file_
        return file_, rank
