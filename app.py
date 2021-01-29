# /usr/bin/python
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as tkfiledialog

from comment_editor import CommentEditor
from board_view import BoardView
from controls import Controls
from chess_listing import ChessListing
from chess_tree import ChessTree
from chess_model_api import ChessModelAPI

from file_rank_square import file_rank2square_name
from file_rank_square import square_name2file_rank

#####################################
# Utility Functions - used by App only

def get_piece_color(piece):
    if piece == '':
        return ''
    elif piece.lower() == piece:
        return 'B'
    else:
        return 'W'

def geo_str2list(geo_str):
    geo_str = geo_str.replace('+', ' ')
    geo_str = geo_str.replace('x', ' ')
    geo = geo_str.split(' ')
    geo = [int(i) for i in geo]
    return geo

class App(object):
    def __init__(self, parent=None):
        self.title_str = 'python chess tree, Colin Davey v alpha'
        self.parent = parent
        self.parent.title(self.title_str)

        # be prepared to close the tree window when closing main window
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        is_white = True

        # we have create both a model and a view within the controller
        # the controller doesn't inherit from either model or view

        # Create the chess model (cm)
        self.cm = ChessModelAPI()

        self.state_str = self.cm.init_state(is_white)

        self.top = tk.Frame(self.parent)
        # self.top.pack(side=TOP, fill=BOTH, expand=True)
        # self.top.pack(side=TOP, fill=BOTH)
        self.top.pack(side=tk.TOP)

        self.left = tk.Frame(self.top)
        # self.left.pack(side=tk.LEFT, fill=BOTH, expand=True)
        self.left.pack(side=tk.LEFT)

        # Create the board view (bv)
        self.bv = BoardView(self.left, is_white=is_white)

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
        self.right = tk.Frame(self.top)
        self.right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_top = tk.Frame(self.right)
        self.right_top.pack(side=tk.TOP)
        self.loadBtn = tk.Button(self.right_top, text="Load")
        self.loadBtn.pack(side=tk.LEFT)
        self.saveBtn = tk.Button(self.right_top, text="Save")
        self.saveBtn.pack(side=tk.LEFT)

        self.loadBtn.config(command=self.load_pgn)
        self.saveBtn.config(command=self.save_pgn)

        self.right_top2 = tk.Frame(self.right)
        self.right_top2.pack(side=tk.TOP)

        self.is_white = tk.IntVar()
        self.is_white.set(is_white)

        self.rb_w = tk.Radiobutton(self.right_top2, text="White", variable=self.is_white, value=1, command=self.set_player)
        self.rb_w.pack(side=tk.LEFT)
        self.rb_b = tk.Radiobutton(self.right_top2, text="Black", variable=self.is_white, value=0, command=self.set_player)
        self.rb_b.pack(side=tk.LEFT)

        # self.cl = tk.Label(self.right, text='Game listing will go here.', bg='#eee')
        # self.cl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.cl = ChessListing(self.right)
        self.cl.table.bind("<Button-1>", self.handle_cl_click)

        # Create the chess tree (ct)
        self.bottom = tk.Frame(self.parent)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.ct = ChessTree(self.bottom)
        self.ct.tree.bind("<<TreeviewSelect>>", self.handle_tree_select_builtin)

        # new tree for built-in
        tree_dict = self.cm.make_tree(self.state_str)
        self.make_tree_builtin(tree_dict)
        # initialize separate windows, which don't exist yet

        self.ce_root = None

        # initialize some variables
        self.click1 = []
        self.legal_dests = []

    def open_all(self):
        self.ct.open_all(True)

    def close_all_but_current(self):
        self.ct.open_all(False)

    def run(self):
        self.update_display()
        tk.mainloop()

    def set_player(self):
        # self.is_white is a control variable attached to the White/Black radio buttons
        is_white = self.is_white.get()
        self.bv.set_player(is_white)
        self.bv.update_display(self.state_str["piece_distrib"])
        self.state_str = self.cm.set_headers(self.state_str, is_white)
        self.ct.update_tree_node(self.state_str["root_node_str"], self.ct.get_root_node())

    # close the comment window when closing main window
    def on_closing(self):
        if self.ce_root is not None:
            self.ce_root.destroy()
        self.parent.destroy()

    def handle_comment_button(self):
        if self.ce_root is None:
            self.ce_root = tk.Tk()
            self.ce_root.title(self.title_str + '. Comment editor')
            self.ce_root.protocol("WM_DELETE_WINDOW", self.on_closing_comment_editor)
            self.ce = CommentEditor(self.ce_root)

            screenw = self.parent.winfo_screenwidth()
            # screenh = self.parent.winfo_screenheight()
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
        start_coord = file_rank2square_name(board_coords.file, board_coords.rank)
        legal_moves = list(filter(lambda m : m[0:2] == start_coord, self.state_str["legal_moves"]))
        # maps e.g. ["e2e3", "e2e4"] to ["e3", "e4"] to [{f : 4, r : 2}, {f : 4, r : 3}]
        dest_list = list(map(
            lambda m : square_name2file_rank(m[2:]),
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
        comment = self.ce.editor.get(1.0, tk.END)
        comment = comment[0:-1]
        print('comment:', comment)
        self.state_str = self.cm.set_comment(self.state_str, comment)
        self.ce.save_button.configure(state=tk.DISABLED)
        self.ce.editor.edit_modified(False)
        self.ct.update_tree_node(self.state_str["node_str"], self.ce.tree_node)

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
            self.ce.editor.replace(1.0, tk.END, comment)
            self.ce.save_button.configure(state=tk.DISABLED)
            self.ce.editor.edit_modified(False)
            # this is only necessary in case the user makes the next node by clicking on the tree.
            # otherwise, we could just use the selected node at that time.
            self.ce.tree_node = self.ct.get_selected_node()

    def make_tree_builtin(self, tree_dict):
        # new tree for built-in
        self.ct.make_tree(self.state_str["variations"], tree_dict)
        self.ct.horz_scrollbar_magic()

    # when the next move menu changes, next_move_str changes bringing control to here.
    # this routine updates the tree.
    # we don't use the last three parameters
    def next_move_str_trace(self, a, b, c):
        next_move = self.c.next_move_str.get()
        # for built-in
        print("*** from next_move_str_trace")
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

    def load_pgn(self):
        # get filename
        filename = tkfiledialog.askopenfilename(filetypes=[('pgn files', '*.pgn')])
        print("loading ", filename)
        if filename != '':
   #        # !!!Error handling
            with open(filename,"r") as f:
                self.state_str["pgn_str"] = f.read()
            self.state_str["moves"] = []
            self.state_str = self.cm.move_back_full(self.state_str)
            self.set_player()

            tree_dict = self.cm.make_tree(self.state_str)

            self.update_display()
            self.make_tree_builtin(tree_dict)
        # put the focus back on the tree so keyboard works.
        self.parent.lift()
        # self.ct.tree.focus_force()
        self.ct.tree.focus_set()

    def save_pgn(self):
        # get filename
        filename = tkfiledialog.asksaveasfilename(defaultextension='.pgn')
        if filename != '':
            f = open(filename, 'w')
            print(self.state_str["pgn_str"], file=f)
            f.close()
            # This no doubt won't work without "import chess"
            # f = open(filename+"2", 'w')
            # print(self.state_str["game_py"], file=f)
            # f.close()

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