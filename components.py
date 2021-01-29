# /usr/bin/python

import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as tktree

import os
import os.path
# !!!git this for tooltips
# import wckToolTips

from file_rank_square import BoardCoords

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
            self.draw_tile(item.file, item.rank, tile)

    # reversing rank so rank 0 is the bottom (chess) rather than top (tk) for White
    # reversing file so file 0 is the right (chess) rather than top (tk) for Black
    def flip_file_rank(self, file_, rank):
        if self.is_white:
            rank = 7 - rank
        else:
            file_ = 7 - file_
        return file_, rank

class ChessListing(tk.Frame):
    def __init__(self, parent=None, do_grid=False):
        tk.Frame.__init__(self, parent)
        self.table = tktree.Treeview(parent)
        ysb = tktree.Scrollbar(parent, orient='vertical', command=self.table.yview)
        self.table.configure(yscroll=ysb.set)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
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
        self.backFullBtn.pack(side=tk.LEFT)

        self.backBtn = tk.Button(self, text="<")
        self.backBtn.pack(side=tk.LEFT)

        # next_move_str is a tk "control variable"
        # see http://effbot.org/tkinterbook/variable.htm
        # http://stackoverflow.com/questions/3876229/how-to-run-a-code-whenever-a-tkinter-widget-value-changes/3883495#3883495
        self.next_move_str = tk.StringVar(self)
        self.nextMoveOMen = tk.OptionMenu(self, self.next_move_str, [])
        # self.nextMoveOMen.config(width=7)
        self.nextMoveOMen.config(width=0)
        # self.nextMoveOMen.pack(side=LEFT, fill=X, expand=True)
        self.nextMoveOMen.pack(side=tk.LEFT)

        self.frwdBtn = tk.Button(self, text=">")
        self.frwdBtn.pack(side=tk.LEFT)

        self.frwdFullBtn = tk.Button(self, text=">|")
        self.frwdFullBtn.pack(side=tk.LEFT)

        self.removeVarBtn = tk.Button(self, text="x")
        self.removeVarBtn.pack(side=tk.LEFT)

        self.promote2MainVarBtn = tk.Button(self, text="^^")
        self.promote2MainVarBtn.pack(side=tk.LEFT)

        self.promoteVarBtn = tk.Button(self, text="^")
        self.promoteVarBtn.pack(side=tk.LEFT)

        self.demoteVarBtn = tk.Button(self, text="v")
        self.demoteVarBtn.pack(side=tk.LEFT)

        # self.treeBtn = tk.Button(self, text="Tree")
        # self.treeBtn.pack(side=tk.LEFT)

        self.commentBtn = tk.Button(self, text="{}")
        self.commentBtn.pack(side=tk.LEFT)

        self.closeBtn = tk.Button(self, text="C")
        self.closeBtn.pack(side=tk.LEFT)

        self.openBtn = tk.Button(self, text="O")
        self.openBtn.pack(side=tk.LEFT)

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
            tk.Grid.columnconfigure(parent, 0, weight=1)
            tk.Grid.rowconfigure(parent, 0, weight=1)
        ####################
        self.tree = tktree.Treeview(parent, show='tree')
        xsb = tktree.Scrollbar(parent, orient='horizontal', command=self.tree.xview)
        ysb = tktree.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        # self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.configure(xscroll=xsb.set)
        self.tree.configure(yscroll=ysb.set)
        ####################
        if do_grid:
            # This line needed to get horizontal scrollbar to sort of work
            # self.tree.pack(expand=1, fill=BOTH)
            # self.tree.grid(expand=1, fill=BOTH)

            self.tree.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
            xsb.grid(row=1, column=0, sticky='ew')
            ysb.grid(row=0, column=1, sticky='ns')
        else:
            xsb.pack(side=tk.BOTTOM, fill=tk.X)
            ysb.pack(side=tk.RIGHT, fill=tk.Y)
            self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
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

    def make_tree(self, variations, tree_dict):
        print(tree_dict)
        # empty tree
        children = self.tree.get_children('')
        for child in children:
            self.tree.delete(child)

        self.tree_pgn_node_recur(tree_dict, '')

        self.tree.selection_set(self.get_root_node())
        # self.tree.see(tree_node)
        if len(variations) > 0:
            print("*** from make_tree")
            self.update_tree_selection_2ndary(variations[0])

    def tree_pgn_node_recur(self, dict_node, parent):
        parent = self.tree.insert(parent, "end", text=dict_node["label"], open=True, tags='all')
        for child in dict_node["children"]:
            self.tree_pgn_node_recur(child, parent)

    # def make_tree(self, game, root_node_str, variations, tree_dict):
    #     print(tree_dict)
    #     # empty tree
    #     children = self.tree.get_children('')
    #     for child in children:
    #         self.tree.delete(child)
    #     # insert initial tree node, and pass it in as 2nd parameter
    #     initial_node = self.tree.insert('', "end", text=root_node_str, open=True, tags='all')
    #     self.tree_pgn_node_recur(game, initial_node, True)

    #     self.tree.selection_set(self.get_root_node())
    #     # self.tree.see(tree_node)
    #     if len(variations) > 0:
    #         self.update_tree_selection_2ndary(variations[0])

    # def tree_pgn_node_recur(self, pgn_node, parent, initial=False):
    #     # if pgn_node.parent is not None:
    #     if not initial:
    #         the_str = make_san_node_str(pgn_node)
    #         parent = self.tree.insert(parent, "end", text=the_str, open=True, tags='all')
    #     if not pgn_node.is_end():
    #         for variation in pgn_node.variations:
    #             self.tree_pgn_node_recur(variation, parent)

    # tree changes due to clicks or key presses allow actions on tree selection changes
    # otherwise not
    # prevents handle_tree_select from running unless it was a direct result of a click,
    # or key press as opposed to programatically
    def handle_tree_click(self, event):
        self.tree_clicked = True

    def update_tree_node(self, str, tree_node):
        selected_node = tree_node
        self.tree.item(selected_node, text=str)

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

    def get_node_with_move(self, tree_node, move):
        # print('* get_node_with_move', move)
        for child in self.tree.get_children(tree_node):
            tmptext = self.tree.item(child, 'text')
            tmptext_bits = tmptext.split(' ')
            tmptext = tmptext_bits[1]
            if tmptext == move:
                # !!!why doesn't the return work here? 
                return child
                # break
        print('*  get_node_with_move finished loop')
        return child
        # pass

    def update_tree(self, moves, next_move):
        # select the node of the current move by traversing through the moves.
        # the premise is that all the moves are in the tree
        tree_node = self.get_root_node()
        for p in range(0, len(moves)):
            tmp_next_move = moves[p]
            childrenIDs = self.tree.get_children(tree_node)
            # should always pass this if, since the premise is that all moves are in the tree
            if len(childrenIDs) > 0:
                tree_node = self.get_node_with_move(tree_node, tmp_next_move)
        self.tree.selection_set(tree_node)
        # self.tree.see(tree_node)
        print("*** from update_tree")
        self.update_tree_selection_2ndary(next_move)

    def update_tree_selection_2ndary(self, next_move):
        # untag the previous selection variation
        # premise is that there is at most one
        print("** update_tree_selection_2ndary", next_move)
        tagged_ids = self.tree.tag_has("sel_var")
        if len(tagged_ids) > 0:
            self.tree.item(tagged_ids[0], tags='all')

        # get the selected node of the tree
        selected_node = self.get_selected_node()

        # tag the new selection variation
        childrenIDs = self.tree.get_children(selected_node)
        if len(childrenIDs) > 0:
            tree_node = self.get_node_with_move(selected_node, next_move)
            self.tree.item(tree_node, tags=['sel_var', 'all'])
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