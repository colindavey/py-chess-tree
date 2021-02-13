# /usr/bin/python

import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as tktree

# !!!git this for tooltips
# import wckToolTips

class ChessTree(tk.Frame):
    def __init__(self, parent, move_to_tree_node_cb):
        tk.Frame.__init__(self, parent)

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
        self.tree = tktree.Treeview(parent, show='tree')
        xsb = tktree.Scrollbar(parent, orient='horizontal', command=self.tree.xview)
        ysb = tktree.Scrollbar(parent, orient='vertical', command=self.tree.yview)
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
        self.tree_clicked = False
        # self.tree.configure(takefocus=1)        
        self.move_to_tree_node_cb = move_to_tree_node_cb

    # tree changes due to clicks or key presses allow actions on tree selection changes
    # otherwise not
    # prevents handle_node_select from running unless it was a direct result of a click,
    # or key press as opposed to programatically
    def handle_tree_click(self, event):
        self.tree_clicked = True

    def handle_node_select(self, event):
        if self.tree_clicked:
            self.move_to_tree_node_cb(self.get_tree_moves())
            self.tree_clicked = False

    def make_tree(self, variations, tree_dict):
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

    # get the moves from the beginning of the game to the selected tree node
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
            for item in items:
                bbox = self.tree.bbox(item, column='#0')
                if bbox != '':
                    # the x value
                    x = bbox[0]
                    # # temporary kludge
                    # num_levels = (x - 2)//20
                    # x = ((num_levels + 4) * 20) + 2
                    tmptxt = self.tree.item(item, 'text')
                    tw = self.font.measure(tmptxt)
                    # twa = self.font_actual.measure(tmptxt)
                    w = x + tw
                    # if bbox[0] + bbox[2] > w:
                    #     w = bbox[0] + bbox[2]
                    #     print('***override')
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

    def update_tree_node(self, str, tree_node):
        selected_node = tree_node
        self.tree.item(selected_node, text=str)

    def get_node_with_move(self, tree_node, move):
        print('* get_node_with_move', move, len(self.tree.get_children(tree_node)))
        # Should always find move, ie, should only call this if move exists.
        for child in self.tree.get_children(tree_node):
            tmptext = self.tree.item(child, 'text')
            tmptext_bits = tmptext.split(' ')
            tmptext = tmptext_bits[1]
            if tmptext == move:
                return child
        # print('  *** finished loop')
        # return child

    def update_tree(self, moves, next_move):
        # select the node of the current move by traversing through the moves.
        # the premise is that all the moves are in the tree
        tree_node = self.get_root_node()
        for move in moves:
            # should always pass this if, since the premise is that all moves are in the tree
            if len(self.tree.get_children(tree_node)) > 0:
                tree_node = self.get_node_with_move(tree_node, move)

        self.tree.selection_set(tree_node)
        # self.tree.see(tree_node)
        print("*** from update_tree")
        self.update_tree_selection_2ndary(next_move)

    def update_tree_selection_2ndary(self, next_move):
        print("** update_tree_selection_2ndary", next_move)
        # untag the previous selection variation
        # premise is that there is at most one
        tagged_ids = self.tree.tag_has("sel_var")
        if len(tagged_ids) > 0:
            self.tree.item(tagged_ids[0], tags='all')
        if next_move == '':
            return

        # get the selected node of the tree
        selected_node = self.get_selected_node()

        # tag the new selection variation
        childrenIDs = self.tree.get_children(selected_node)
        if len(childrenIDs) > 0:
            tree_node = self.get_node_with_move(selected_node, next_move)
            self.tree.item(tree_node, tags=['sel_var', 'all'])

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

    def add_node_to_tree(self, san_str):
        # get the selected node of the tree
        selected_node = self.get_selected_node()
        # add the current move at the end of the selected node's children
        self.tree.insert(selected_node, "end", text=san_str, open=True, tags='all')

    def open_all(self, bool_in):
        items = self.tree.tag_has('all')
        for item in items:
            self.tree.item(item, open=bool_in)
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