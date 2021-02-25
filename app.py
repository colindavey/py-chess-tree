# /usr/bin/python

import json
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as tkfiledialog

from comment_editor import CommentEditor
from board_view import BoardView
from chess_listing import ChessListing
from chess_tree import ChessTree

from chess_model_api_server import chess_model_api
from chess_model_api_server import chess_model_api_init
from chess_model_api_server import chess_model_api_make_tree

#####################################
# Utility Functions - used by App only

def geo_str2list(geo_str):
    geo_str = geo_str.replace('+', ' ')
    geo_str = geo_str.replace('x', ' ')
    geo = geo_str.split(' ')
    geo = [int(i) for i in geo]
    return geo

def json_state(state_in):
    state_arg = json.dumps({
        "pgn_str" : state_in["pgn_str"], 
        "moves" : state_in["moves"]
    })
    return state_arg

def chess_model_api_client(operation, state_in, **kwargs):
    state_ret, outputs = chess_model_api(
        operation, 
        json_state(state_in), 
        json.dumps(kwargs)
    )
    return json.loads(state_ret), json.loads(outputs)

class App(object):
    def __init__(self, parent=None):
        is_white = True

        #######################################
        # Set up the TK space
        #######################################
        self.title_str = 'python chess tree, Colin Davey v alpha'
        self.parent = parent
        self.parent.title(self.title_str)

        # be prepared to close the tree window when closing main window
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        # top has board and listing/other
        self.top = tk.Frame(self.parent)
        # self.top.pack(side=TOP, fill=BOTH, expand=True)
        # self.top.pack(side=TOP, fill=BOTH)
        self.top.pack(side=tk.TOP)

        # board view
        self.left = tk.Frame(self.top)
        # self.left.pack(side=tk.LEFT, fill=BOTH, expand=True)
        self.left.pack(side=tk.LEFT)

        # right frame for vertical listing and other controls
        self.right = tk.Frame(self.top)
        self.right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # load/save
        self.right_top = tk.Frame(self.right)
        self.right_top.pack(side=tk.TOP)
        
        # W/B radio buttons
        self.right_top2 = tk.Frame(self.right)
        self.right_top2.pack(side=tk.TOP)

        # Listing
        self.right_main = tk.Frame(self.right)
        self.right_main.pack(side=tk.TOP)

        # Video control buttons
        self.right_bottom = tk.Frame(self.right)
        self.right_bottom.pack(side=tk.BOTTOM)

        # tree complex
        self.bottom = tk.Frame(self.parent)
        # self.bottom.pack(side=tk.BOTTOM)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # tree
        self.bottom_left = tk.Frame(self.bottom)
        self.bottom_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # # next table
        self.bottom_right = tk.Frame(self.bottom)
        # self.bottom_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.bottom_right.pack(side=tk.LEFT)

        #######################################
        # Create the board view (bv)
        #######################################
        self.bv = BoardView(self.left, self.move, is_white=is_white)

        #######################################
        # Create the right top widgents
        #######################################
        self.loadBtn = tk.Button(self.right_top, text="Load")
        self.loadBtn.pack(side=tk.LEFT)
        self.loadBtn.config(command=self.load_pgn)

        self.saveBtn = tk.Button(self.right_top, text="Save")
        self.saveBtn.pack(side=tk.LEFT)
        self.saveBtn.config(command=self.save_pgn)

        self.is_white = tk.IntVar()
        self.is_white.set(is_white)
        self.rb_w = tk.Radiobutton(self.right_top2, text="W", variable=self.is_white, value=1, command=self.set_player)
        self.rb_w.pack(side=tk.LEFT)
        self.rb_b = tk.Radiobutton(self.right_top2, text="B", variable=self.is_white, value=0, command=self.set_player)
        self.rb_b.pack(side=tk.LEFT)

        self.commentBtn = tk.Button(self.right_top2, text="{}")
        self.commentBtn.pack(side=tk.LEFT)
        self.commentBtn.config(command=self.handle_comment_button)

        #######################################
        # Create the chess listing (cl)
        #######################################
        self.cl = ChessListing(self.right, self.move_to_cl)

        #######################################
        # Create the "video buttons"
        #######################################
        self.backFullBtn = tk.Button(self.right_bottom, text="|<")
        self.backFullBtn.pack(side=tk.LEFT)

        self.backBtn = tk.Button(self.right_bottom, text="<")
        self.backBtn.pack(side=tk.LEFT)

        self.frwdBtn = tk.Button(self.right_bottom, text=">")
        self.frwdBtn.pack(side=tk.LEFT)

        self.frwdFullBtn = tk.Button(self.right_bottom, text=">|")
        self.frwdFullBtn.pack(side=tk.LEFT)

        self.backFullBtn.config(command=self.move_back_full)
        self.backBtn.config(command=self.move_back)
        self.frwdBtn.config(command=self.move_frwd)
        self.frwdFullBtn.config(command=self.move_frwd_full)

        #######################################
        # Create the chess tree (ct) and controls
        #######################################
        self.ct = ChessTree(self.bottom_left, self.left, self.bottom_right, 
            self.backFullBtn, self.backBtn, self.frwdBtn, self.frwdFullBtn,
            self.diddle_var, self.move_to_tree_node)

        # initialize separate comment editor window, which doesn't exist yet
        self.ce_root = None
        self.ce_tree_node_moves = None

        #######################################
        # Create the chess model (cm)
        #######################################
        self.state = json.loads(chess_model_api_init())
        self.state, _ = chess_model_api_client('set_headers', self.state, is_white=is_white)
        self.make_tree()

    #################################
    # Starting stopping and saving
    #################################
    # close the comment window when closing main window
    def on_closing(self):
        if self.ce_root is not None:
            self.ce_root.destroy()
        self.parent.destroy()

    def save_pgn(self):
        # get filename
        filename = tkfiledialog.asksaveasfilename(defaultextension='.pgn')
        if filename != '':
            f = open(filename, 'w')
            print(self.state["pgn_str"], file=f)
            f.close()
        self.parent.focus_force()

   #################################
    # Manipulates GUI
    #################################
    def update_display(self):
        self.bv.update(self.state["piece_distrib"], self.state["legal_moves"], self.state["turn"])
        self.cl.update_listing(self.state["moves"])
        self.update_ce()
        self.ct.ctc_update_display(self.state["moves"], self.state["variations"])

    def make_tree(self):
        tree_dict = json.loads(
            chess_model_api_make_tree(json_state(self.state)))
        self.ct.ctc_make_tree(self.state["variations"], tree_dict)
        self.update_display()

    #################################
    # Fits pattern
    #   give user input, results in call to chess model and change to GUI
    #################################
    #################################
    # Change model, but not board state
    #################################
    def diddle_var(self, diddle, san):
        self.state, _ = chess_model_api_client('diddle_var', self.state, diddle=diddle, san=san)
        return self.state["variations"]

    def set_player(self):
        # self.is_white is a control variable attached to the White/Black radio buttons
        is_white = self.is_white.get()
        self.bv.set_player(is_white)
        self.bv.update_display(self.state["piece_distrib"])
        self.state, _ = chess_model_api_client('set_headers', self.state, is_white=is_white)
        self.ct.ctc_update_tree_node(self.state["root_node_str"], [])

    def load_pgn(self):
        # get filename
        filename = tkfiledialog.askopenfilename(filetypes=[('pgn files', '*.pgn')])
        print("loading ", filename)
        if filename != '':
   #        # !!!Error handling
            with open(filename,"r") as f:
                self.state["pgn_str"] = f.read()
            self.state["moves"] = []
            self.state, _ = chess_model_api_client('move_back_full', self.state)
            self.set_player()
            self.make_tree()
        self.parent.focus_force()

    ##############################
    # Change model: board state (moves)
    ##############################

    # from listing click
    def move_to_cl(self, moves):
        if self.check_comment():
            self.state, _ = chess_model_api_client('move_to', self.state, moves=moves)
            self.update_display()
            self.ct.ctc_open_all(False)

    # from tree click
    def move_to_tree_node(self, moves):
        if self.check_comment():
            self.state, _ = chess_model_api_client('move_to', self.state, moves=moves)
            self.update_display()

    # from board click
    def move(self, click1, click2):
        if self.check_comment():
            self.state, outputs = chess_model_api_client('move_add', self.state, start=click1, destination=click2)
            added = outputs['added']
            san = outputs['san']
            move_str = outputs['move_str']
            if added:
                # update the tree
                self.ct.ctc_add_node_to_tree(move_str)
                # update the option menu? not necessary, since we're about to leave
            self.state, _ = chess_model_api_client('move_frwd', self.state, san=san)
            self.update_display()

    # from buttons
    def move_back_full(self):
        if self.check_comment():
            self.state, _ = chess_model_api_client('move_back_full', self.state)
            self.update_display()
            self.ct.ctc_open_all(False)

    def move_back(self):
        if self.check_comment():
            self.state, _ = chess_model_api_client('move_back', self.state)
            self.update_display()
            self.ct.ctc_open_all(False)

    def move_frwd(self):
        if self.check_comment():
            self.state, _ = chess_model_api_client('move_frwd', self.state, san=self.ct.ctc_get_next_move_str())
            self.update_display()
            self.ct.ctc_open_all(False)

    def move_frwd_full(self):
        if self.check_comment():
            self.state, _ = chess_model_api_client('move_frwd', self.state, san=self.ct.ctc_get_next_move_str())
            self.state, _ = chess_model_api_client('move_frwd_full', self.state)
            self.update_display()
            self.ct.ctc_open_all(False)

    #################################
    # Comment editing (put elsewhere?)
    #################################
    def update_ce(self):
        if self.ce_root is not None:
            comment = self.state["comment"]
            self.ce.editor.replace(1.0, tk.END, comment)
            self.ce.save_button.configure(state=tk.DISABLED)
            self.ce.editor.edit_modified(False)
            # this is only necessary in case the user makes the next node by clicking on the tree.
            # otherwise, we could just use the selected node at that time.
            self.ce_tree_node_moves = self.state['moves'] 

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

    def save_comment(self):
        comment = self.ce.editor.get(1.0, tk.END)
        comment = comment[0:-1]
        print('comment:', comment)
        self.state, _ = chess_model_api_client('set_comment', self.state, comment=comment)
        self.ce.save_button.configure(state=tk.DISABLED)
        self.ce.editor.edit_modified(False)
        self.ct.ctc_update_tree_node(self.state["node_str"], self.ce_tree_node_moves)

    def on_closing_comment_editor(self):
        self.ce_root.destroy()
        self.ce_root = None

if __name__ == "__main__":
    the_parent = tk.Tk()
    app = App(the_parent)
    tk.mainloop()