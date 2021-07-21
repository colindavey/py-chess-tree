# /usr/bin/python

import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as tktree
from tkinter import messagebox

# !!!git this for tooltips
# import wckToolTips

class ChessTree(tk.Frame):
    # def __init__(self, tree_parent, button_left_parent, button_right_parent, table_parent, 
    def __init__(self, parent, diddle_var_cb, move_to_tree_node_cb, set_player_cb, is_white):
        # tk.Frame.__init__(self, tree_parent, button_parent, table_parent)
        # tk.Frame.__init__(self, button_parent, table_parent)
        # tk.Frame.__init__(self, button_parent)
        tk.Frame.__init__(self, parent)

        # tree_parent, button_left_parent, button_right_parent, table_parent
        self.top_parent = tk.Frame(parent)
        self.top_parent.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=True)

        self.button_left_parent = tk.Frame(self.top_parent)
        self.button_left_parent.pack(side=tk.LEFT, anchor=tk.W)

        self.button_right_parent = tk.Frame(self.top_parent)
        self.button_right_parent.pack(side=tk.RIGHT, anchor=tk.E)

        # tree
        self.tree_parent = tk.Frame(parent)
        self.tree_parent.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # # next table
        self.table_parent = tk.Frame(parent)
        # self.bottom_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.table_parent.pack(side=tk.LEFT)

        ####################################
        # Buttons
        ####################################

        self.is_white = tk.IntVar()
        self.is_white.set(is_white)
        self.rb_w = tk.Radiobutton(self.button_left_parent, text="W", variable=self.is_white, value=1, command=self.set_player)
        self.rb_w.pack(side=tk.LEFT)
        self.rb_b = tk.Radiobutton(self.button_left_parent, text="B", variable=self.is_white, value=0, command=self.set_player)
        self.rb_b.pack(side=tk.LEFT)

        self.closeBtn = tk.Button(self.button_left_parent, text="C")
        self.closeBtn.pack(side=tk.LEFT)
        self.closeBtn.config(command=lambda: self.ctc_open_all(False))

        self.openBtn = tk.Button(self.button_left_parent, text="O")
        self.openBtn.pack(side=tk.LEFT)
        self.openBtn.config(command=lambda: self.ctc_open_all(True))

        self.removeVarBtn = tk.Button(self.button_right_parent, text="x")
        self.removeVarBtn.pack(side=tk.LEFT)
        self.removeVarBtn.config(command=lambda: self.ctc_diddle_var('remove'))

        self.promote2MainVarBtn = tk.Button(self.button_right_parent, text="^^")
        self.promote2MainVarBtn.pack(side=tk.LEFT)
        self.promote2MainVarBtn.config(command=lambda: self.ctc_diddle_var('promote2main'))

        self.promoteVarBtn = tk.Button(self.button_right_parent, text="^")
        self.promoteVarBtn.pack(side=tk.LEFT)
        self.promoteVarBtn.config(command=lambda: self.ctc_diddle_var('promote'))

        self.demoteVarBtn = tk.Button(self.button_right_parent, text="v")
        self.demoteVarBtn.pack(side=tk.LEFT)
        self.demoteVarBtn.config(command=lambda: self.ctc_diddle_var('demote'))

        ####################################
        # Table
        ####################################
        # show="tree" turns off the heading
        self.table = tktree.Treeview(self.table_parent, show="tree")
        # self.table = tktree.Treeview(table_parent)
        ysb = tktree.Scrollbar(self.table_parent, orient='vertical', command=self.table.yview)
        self.table.configure(yscroll=ysb.set)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.table['columns'] = ('move')
        self.table['displaycolumns'] = ('')
        self.table.column("#0", width=100, stretch=tk.NO)
        self.table.column('move', anchor='w', width=100, stretch=tk.NO)
        self.table.configure(selectmode='browse')
        self.table.bind("<ButtonRelease-1>", self.handle_table_click)
        
        ####################################
        # Tree
        ####################################
        # For built-in, Grid doesn't work, Pack does.
        #   Grid dies before ap shows up
        # However, on separate window, the opposite.
        #   Pack fails on Tree button with
        # "'App' object has no attribute 'pack'"
        ####################
        # if do_grid:
        #     tk.Grid.columnconfigure(parent, 0, weight=1)
        #     tk.Grid.rowconfigure(parent, 0, weight=1)
        ####################
        self.tree = tktree.Treeview(self.tree_parent, show='tree')
        xsb = tktree.Scrollbar(self.tree_parent, orient='horizontal', command=self.tree.xview)
        ysb = tktree.Scrollbar(self.tree_parent, orient='vertical', command=self.tree.yview)
        # self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.configure(xscroll=xsb.set)
        self.tree.configure(yscroll=ysb.set)
        ####################
        # if do_grid:
        #     # This line needed to get horizontal scrollbar to sort of work
        #     # self.tree.pack(expand=1, fill=BOTH)
        #     # self.tree.grid(expand=1, fill=BOTH)

        #     self.tree.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        #     xsb.grid(row=1, column=0, sticky='ew')
        #     ysb.grid(row=0, column=1, sticky='ns')
        # else:
        #     xsb.pack(side=tk.BOTTOM, fill=tk.X)
        #     ysb.pack(side=tk.RIGHT, fill=tk.Y)
        #     self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        #     self.pack()
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
        self.tree.bind("<<TreeviewSelect>>", self.handle_node_select)
        # self.tree.configure(takefocus=1)

        self.tree_clicked = False
        self.move_to_tree_node_cb = move_to_tree_node_cb
        self.diddle_var_cb = diddle_var_cb
        self.set_player_cb = set_player_cb

    ###################################
    # User input
    ###################################
    def handle_table_click(self, event):
        clickedRow = self.table.identify_row(event.y)
        values = self.table.item(clickedRow, 'values')
        next_move = self.table.item(clickedRow, 'text')
        self.update_tree_selection_2ndary(next_move)

    def set_player(self):
        # self.is_white is a control variable attached to the White/Black radio buttons
        self.set_player_cb(self.is_white.get())

    ###########################
    #
    # tree changes due to clicks or key presses allow actions on tree selection changes
    # otherwise not
    # prevents handle_node_select from running unless it was a direct result of a click,
    # or key press as opposed to programatically
    def handle_tree_click(self, event):
        self.tree_clicked = True
        if str(self.tree['selectmode']) == 'none':
            messagebox.showinfo(message="Can't click tree while comment editor is open.")

    def handle_node_select(self, event):
        if self.tree_clicked:
            self.move_to_tree_node_cb(self.get_tree_moves())
            self.tree_clicked = False

    # get the moves from the beginning of the game to the selected tree node
    def get_tree_moves(self):
        moves = []
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
    #
    ###########################

    ###########################
    #
    # Table and tree
    def ctc_diddle_var(self, diddle):
        san = self.get_next_move_str_from_table()
        # Diddle the model (callback that calls the api)
        variations = self.diddle_var_cb(diddle, san)

        # Diddle the table
        if diddle == 'remove':
            san = ''
        self.update_table_variations(variations, san)

        # Diddle the tree
        self.diddle_var_tree(diddle)
        next_move = self.get_next_move_str_from_table()
        self.update_tree_selection_2ndary(next_move)

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
    #
    ###########################

    #################################
    # Public
    #################################
    # Tree
    def ctc_add_node_to_tree(self, san_str):
        # get the selected node of the tree
        selected_node = self.get_selected_node()
        # add the current move at the end of the selected node's children
        self.tree.insert(selected_node, "end", text=san_str, open=True, tags='all')

    # Tree
    def ctc_update_tree_node(self, node_str, moves):
        self.tree.item(self.get_node_from_moves(moves), text=node_str)

    # Tree
    def ctc_open_all(self, bool_in):
        items = self.tree.tag_has('all')
        for item in items:
            self.tree.item(item, open=bool_in)
        # if closing, make sure that it's at least open to the current move
        if not bool_in:
            node = self.get_selected_node()
            self.tree.see(node)
            self.tree.item(node, open=True)

    # Table
    def ctc_get_next_move_str(self):
        return self.get_next_move_str_from_table()

    # Table and tree
    def ctc_enable(self, val):
        if val:
            self.tree.configure(selectmode="extended")
            # self.table.configure(selectmode='browse')
        else:
            self.tree.configure(selectmode="none")
            # self.table.configure(selectmode='none')

    ###########################
    #
    # Table and tree
    def ctc_update_display(self, moves, variations):
        self.update_table_variations(variations)
        # make sure the appropriate tree node is selected based on the current move
        # and the appropriate variation of the move is secondary selected
        next_move = self.get_next_move_str_from_table()
        self.update_tree_selection(moves, next_move)

    def update_tree_selection(self, moves, next_move):
        tree_node = self.get_node_from_moves(moves)
        self.tree.selection_set(tree_node)
        # self.tree.see(tree_node)
        self.update_tree_selection_2ndary(next_move)
        self.horz_scrollbar_magic()

    def horz_scrollbar_magic(self):
        # uses magic numbers 2 and 20, which I found to be the x offset of the root item
        # and the amount it increases for each level depth
        items = self.tree.tag_has('all')
        max_w = 0
        for item in items:
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
    #
    ###########################

    ###########################
    #
    # Tree
    def ctc_make_tree(self, variations, tree_dict):
        # update the table
        self.update_table_variations(variations, '')
        # empty tree
        children = self.tree.get_children('')
        for child in children:
            self.tree.delete(child)
        # fill the tree
        self.tree_pgn_node_recur(tree_dict, '')
        # handle tree selection
        self.tree.selection_set(self.get_root_node())
        # self.tree.see(tree_node)
        if len(variations) > 0:
            self.update_tree_selection_2ndary(variations[0])

    def tree_pgn_node_recur(self, dict_node, parent):
        parent = self.tree.insert(parent, "end", text=dict_node["label"], open=True, tags='all')
        for child in dict_node["children"]:
            self.tree_pgn_node_recur(child, parent)
    #
    ###########################

    ###################################
    # Private
    ###################################
    ###################################
    # Table utility functions
    ###################################

    def update_table_variations(self, variations, next_move_str=''):
        # replace the table with the variations based on the current node
        for child in self.table.get_children(''):
            self.table.delete(child)
        for variation in variations:
            item = self.table.insert('', 'end', text=variation, values=variation)

        if len(variations) > 0:
            if next_move_str == '':
                next_move_str = variations[0]
            self.select_table_item(next_move_str)

    def select_table_item(self, next_move_str):
        for row in self.table.get_children(''):
            if self.table.item(row, 'text') == next_move_str:
                self.table.selection_set(row)
                break

    def get_next_move_str_from_table(self):
        return self.table.item(self.table.selection(), 'text')

    ###################################
    # Tree utility functions
    ###################################

    ##########################################
    #
    def update_tree_selection_2ndary(self, next_move):
        # untag the previous selection variation
        # premise is that there is at most one
        tagged_ids = self.tree.tag_has("sel_var")
        if len(tagged_ids) > 0:
            self.tree.item(tagged_ids[0], tags='all')
        if next_move != '':
            # get the selected node of the tree
            selected_node = self.get_selected_node()
            # tag the new selection variation
            childrenIDs = self.tree.get_children(selected_node)
            if len(childrenIDs) > 0:
                variation_node = self.get_node_with_move(selected_node, next_move)
                self.tree.item(variation_node, tags=['sel_var', 'all'])
        self.update_buttons()

    def update_buttons(self):
        node = self.get_selected_node()
        has_parent = self.tree.parent(node) != ''
        has_variations = len(self.tree.get_children(node)) > 0

        # diable all the buttons if there are no variations
        # because of above, len(variations) == 0 is equiv to no variations
        new_state = tk.NORMAL
        if not has_variations:
            new_state = tk.DISABLED
            self.removeVarBtn.config(state=new_state)
            self.promote2MainVarBtn.config(state=new_state)
            self.promoteVarBtn.config(state=new_state)
            self.demoteVarBtn.config(state=new_state)
        else:
            variations = self.table.get_children('')
            selected_variation = self.table.selection()[0]

            self.removeVarBtn.config(state=new_state)
            new_state = tk.NORMAL
            if selected_variation == variations[0]:
                new_state = tk.DISABLED
            self.promote2MainVarBtn.config(state=new_state)
            self.promoteVarBtn.config(state=new_state)

            new_state = tk.NORMAL
            if selected_variation == variations[-1]:
                new_state = tk.DISABLED
            self.demoteVarBtn.config(state=new_state)
    #
    ##########################################

    # get the initial position node
    # assumes exactly one initial node, representing the starting position
    def get_root_node(self):
        rootIDs = self.tree.get_children('')
        return rootIDs[0]

    def get_selected_node(self):
        selected_node = self.get_root_node()
        sel_items = self.tree.selection()
        if len(sel_items) > 0:
            selected_node = sel_items[0]
        return selected_node

    def get_node_from_moves(self, moves):
        # select the node of the current move by traversing through the moves.
        # the premise is that all the moves are in the tree
        tree_node = self.get_root_node()
        for move in moves:
            # should always pass this if, since the premise is that all moves are in the tree
            if len(self.tree.get_children(tree_node)) > 0:
                tree_node = self.get_node_with_move(tree_node, move)
        return tree_node

    def get_node_with_move(self, tree_node, move):
        # Should always find move, ie, should only call this if move exists.
        for child in self.tree.get_children(tree_node):
            tmptext = self.tree.item(child, 'text')
            tmptext_bits = tmptext.split(' ')
            tmptext = tmptext_bits[1]
            if tmptext == move:
                return child
        # print('  *** finished loop')
        # return child

    # def horz_scrollbar_magic_bbox(self):
    #     # magic to get horizontal scroll bar to work
    #     # get the width of the top item and set the minwidth of the tree to the width
    #     # all items will have the same width, so arbitrarily looking at the first one.
    #     # if using the column parameter, then each item has a different width
    #     # bbox = self.tree.bbox(all_items[p], column='#0')
    #     top_items = self.tree.get_children('')
    #     if len(top_items) > 0:
    #         # returns a 4tuple if the item is visible, empty string otherwise
    #         bbox = self.tree.bbox(top_items[0])
    #         items = self.tree.tag_has('all')

    #         # font = self.tree.configure('font')
    #         # font = self.tree.tag_configure('all', 'font')
    #         # font = self.tree.tag_configure('all', 'background')
    #         # font = self.tree.tag_configure('sel_var', 'font')
    #         # print('font', font, len(items))
    #         max_w = 0
    #         w = 0
    #         # if bbox != '':
    #         #     max_w = bbox[2]
    #         for item in items:
    #             bbox = self.tree.bbox(item, column='#0')
    #             if bbox != '':
    #                 # the x value
    #                 x = bbox[0]
    #                 # # temporary kludge
    #                 # num_levels = (x - 2)//20
    #                 # x = ((num_levels + 4) * 20) + 2
    #                 tmptxt = self.tree.item(item, 'text')
    #                 tw = self.font.measure(tmptxt)
    #                 # twa = self.font_actual.measure(tmptxt)
    #                 w = x + tw
    #                 # if bbox[0] + bbox[2] > w:
    #                 #     w = bbox[0] + bbox[2]
    #                 #     print('***override')
    #                 if w > max_w:
    #                     max_w = w
    #                 # print(x, tw, twa, w, max_w, tmptxt)
    #                 print(x, tw, w, max_w, bbox[2], tmptxt)
    #         print('max_w', max_w)
    #         # adding a fudge factor found empirically
    #         fudge = 15
    #         max_w +- fudge
    #         self.tree.column('#0', minwidth=max_w)
    #         # This works to tighten the columns back down, but needs this routine to
    #         # happen on vertical scroll, or stuff disappears
    #         # if self.tree.column('#0', option='width') > max_w:
    #         #     self.tree.column('#0', width=max_w)

    #         # self.tree.column('#0', minwidth=max_w)
    #         # self.tree.column('#0', minwidth=1000)
    #         # self.tree.column('#0', minwidth=520)
