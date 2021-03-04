# /usr/bin/python
import json
import tkinter as tk
import tkinter.filedialog as tkfiledialog

from comment_editor import CommentEditor
from smart_board import SmartBoard
from chess_listing import ChessListing
from chess_tree import ChessTree

from chess_model_api_server import chess_model_api
from chess_model_api_server import chess_model_api_init
from chess_model_api_server import chess_model_api_make_tree

#####################################
# Utility Functions - used by App only

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
        self.is_white = True

        #######################################
        # Set up the TK space
        #######################################
        self.title_str = 'python chess tree, Colin Davey v alpha'
        self.parent = parent
        self.parent.title(self.title_str)

        # be prepared to close other windows (e.g. the comment editor) when closing main window
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        # top has board and listing/other
        self.top = tk.Frame(self.parent)
        self.top.pack(side=tk.TOP)

        # board view
        self.left = tk.Frame(self.top)
        self.left.pack(side=tk.LEFT)

        # right frame for vertical listing and other controls
        self.right = tk.Frame(self.top)
        self.right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # load/save
        self.right_top = tk.Frame(self.right)
        self.right_top.pack(side=tk.TOP)
        
        # Listing
        self.right_main = tk.Frame(self.right)
        self.right_main.pack(side=tk.TOP)

        # Video control buttons
        self.right_bottom = tk.Frame(self.right)
        self.right_bottom.pack(side=tk.BOTTOM)

        # tree
        self.bottom = tk.Frame(self.parent)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        #######################################
        # Create the board view (bv)
        #######################################
        self.bv = SmartBoard(self.left, self.move, is_white=self.is_white)

        #######################################
        # Create the right top widgents
        #######################################
        self.loadBtn = tk.Button(self.right_top, text="Load")
        self.loadBtn.pack(side=tk.LEFT)
        self.loadBtn.config(command=self.load_pgn)

        self.saveBtn = tk.Button(self.right_top, text="Save")
        self.saveBtn.pack(side=tk.LEFT)
        self.saveBtn.config(command=self.save_pgn)

        self.commentBtn = tk.Button(self.right_top, text="{}")
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
        self.ct = ChessTree(self.bottom, self.diddle_var, self.move_to_tree_node, self.set_player, self.is_white)

        # initialize separate comment editor window, which doesn't exist yet
        self.ce_root = None
        self.ce_tree_node_moves = None

        #######################################
        # Create the chess model (cm)
        #######################################
        self.state = json.loads(chess_model_api_init())
        self.state, _ = chess_model_api_client('set_headers', self.state, is_white=self.is_white)
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
        self.bv.bv_update(self.state["piece_distrib"], self.state["legal_moves"], self.state["turn"])
        self.cl.update_listing(self.state["moves"])
        self.update_buttons(self.state["has_parent"], self.state["variations"])
        self.update_ce()
        self.ct.ctc_update_display(self.state["moves"], self.state["variations"])

    def make_tree(self):
        tree_dict = json.loads(
            chess_model_api_make_tree(json_state(self.state)))
        self.ct.ctc_make_tree(self.state["variations"], tree_dict)
        self.update_display()

    def update_buttons(self, has_parent, variations):
        # disable back buttons if can't go back no more
        new_state = tk.NORMAL
        if not has_parent:
            new_state = tk.DISABLED
        self.backBtn.config(state=new_state)
        self.backFullBtn.config(state=new_state)

        new_state = tk.NORMAL
        if not variations:
            new_state = tk.DISABLED
        self.frwdBtn.config(state=new_state)
        self.frwdFullBtn.config(state=new_state)

    #################################
    # Fits pattern
    #   give user input, results in call to chess model and change to GUI
    #################################
    #################################
    # Change model, but not board state
    #################################
    def diddle_var(self, diddle, san):
        self.state, _ = chess_model_api_client('diddle_var', self.state, diddle=diddle, san=san)
        self.update_buttons(self.state["has_parent"], self.state["variations"])
        return self.state["variations"]

    def set_player(self, is_white):
        # is_white = self.is_white.get()
        self.is_white = is_white
        self.bv.bv_set_player(is_white)
        self.bv.bv_update_display(self.state["piece_distrib"])
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
            self.set_player(self.is_white)
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
    def handle_comment_button(self):
        if self.ce_root is None:
            self.ce_root = tk.Tk()
            self.ce = CommentEditor(self.ce_root, self.parent, self.title_str, self.save_comment, self.on_closing_comment_editor)

        self.update_ce()
        # low level tk stuff
        self.ce_root.lift()
        self.ce_root.update()

    def update_ce(self):
        if self.ce_root is not None:
            self.ce.update_comment(self.state["comment"])
            # this is necessary in case the user makes the next node by clicking on the tree.
            # otherwise, we could just use the selected node at that time.
            self.ce_tree_node_moves = self.state['moves'] 

    def check_comment(self):
        ret_val = True
        if self.ce_root is not None:
            ret_val = self.ce.check_comment()
        return ret_val

    def save_comment(self):
        self.state, _ = chess_model_api_client('set_comment', self.state, comment=self.ce.get_comment())
        self.ct.ctc_update_tree_node(self.state["node_str"], self.ce_tree_node_moves)

    def on_closing_comment_editor(self):
        if self.check_comment():
            self.ce_root.destroy()
            self.ce_root = None

if __name__ == "__main__":
    the_parent = tk.Tk()
    app = App(the_parent)
    tk.mainloop()