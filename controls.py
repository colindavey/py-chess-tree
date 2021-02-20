# /usr/bin/python

import tkinter as tk
import tkinter.ttk as tktree

class Controls(tk.Frame):
    def __init__(self, button_parent, table_parent, backFullBtn, backBtn, frwdBtn, frwdFullBtn):

        self.backFullBtn = backFullBtn
        self.backBtn = backBtn
        self.frwdBtn = frwdBtn
        self.frwdFullBtn = frwdFullBtn

        tk.Frame.__init__(self, button_parent, table_parent)

        self.closeBtn = tk.Button(self, text="C")
        self.closeBtn.pack(side=tk.LEFT)

        self.openBtn = tk.Button(self, text="O")
        self.openBtn.pack(side=tk.LEFT)

        # next_move_str is a tk "control variable"
        # see http://effbot.org/tkinterbook/variable.htm
        # http://stackoverflow.com/questions/3876229/how-to-run-a-code-whenever-a-tkinter-widget-value-changes/3883495#3883495
        self.next_move_str = tk.StringVar(self)
        self.nextMoveOMen = tk.OptionMenu(self, self.next_move_str, [])
        # self.nextMoveOMen.config(width=7)
        self.nextMoveOMen.config(width=0)
        # self.nextMoveOMen.pack(side=LEFT, fill=X, expand=True)
        self.nextMoveOMen.pack(side=tk.LEFT)

        self.removeVarBtn = tk.Button(self, text="x")
        self.removeVarBtn.pack(side=tk.LEFT)

        self.promote2MainVarBtn = tk.Button(self, text="^^")
        self.promote2MainVarBtn.pack(side=tk.LEFT)

        self.promoteVarBtn = tk.Button(self, text="^")
        self.promoteVarBtn.pack(side=tk.LEFT)

        self.demoteVarBtn = tk.Button(self, text="v")
        self.demoteVarBtn.pack(side=tk.LEFT)

        # show="tree" turns off the heading
        self.table = tktree.Treeview(table_parent, show="tree")
        # self.table = tktree.Treeview(table_parent)
        ysb = tktree.Scrollbar(table_parent, orient='vertical', command=self.table.yview)
        self.table.configure(yscroll=ysb.set)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.table['columns'] = ('move')
        self.table['displaycolumns'] = ('')
        self.table.column("#0", width=100, stretch=tk.NO)
        self.table.column('move', anchor='w', width=100, stretch=tk.NO)
        self.table.configure(selectmode='browse')
        self.table.insert('', 'end', text='one', values='two')
        self.table.insert('', 'end', text='three', values='four')
        self.table.bind("<Button-1>", self.handle_click)
    
        self.pack()

    def handle_click(self, event):
        clickedRow = self.table.identify_row(event.y)
        values = self.table.item(clickedRow, 'values')
        text = self.table.item(clickedRow, 'text')
        print(values, text)

    def update_display(self, has_parent, variations, next_move_str=''):
        self.update_next_move_option_menu(variations, next_move_str)
        print('update_display', variations)
        self.update_buttons(has_parent, variations)

    def update_buttons(self, has_parent, variations):
        # diable all the buttons if there are no variations
        new_state = tk.NORMAL
        if len(variations) == 0:
            new_state = tk.DISABLED
        self.removeVarBtn.config(state=new_state)
        self.promote2MainVarBtn.config(state=new_state)
        self.promoteVarBtn.config(state=new_state)
        self.demoteVarBtn.config(state=new_state)

       # diable back button if can't go back no more
        new_state = tk.NORMAL
        if not has_parent:
            new_state = tk.DISABLED
        self.backBtn.config(state=new_state)
        self.backFullBtn.config(state=new_state)

        # diable all the buttons if there are no variations
        new_state = tk.NORMAL
        if len(variations) == 0:
            new_state = tk.DISABLED
        self.frwdBtn.config(state=new_state)
        self.frwdFullBtn.config(state=new_state)

# This logic didn't work for various reasons, but keeping for reference
# One issue was doesn't get invoked when uses changes menu selection via menu
        # # diable all the buttons if there are no variations
        # # because of above, len(variations) == 0 is equiv to no variations
        # new_state = tk.NORMAL
        # if len(variations) == 0:
        #     new_state = tk.DISABLED
        #     self.removeVarBtn.config(state=new_state)
        #     self.promote2MainVarBtn.config(state=new_state)
        #     self.promoteVarBtn.config(state=new_state)
        #     self.demoteVarBtn.config(state=new_state)
        # else:
        #     if next_move_str == '':
        #         next_move_str = variations[0]
        #     self.removeVarBtn.config(state=new_state)
        #     new_state = tk.NORMAL
        #     if variations[0] == next_move_str:
        #         new_state = tk.DISABLED
        #     self.promote2MainVarBtn.config(state=new_state)
        #     self.promoteVarBtn.config(state=new_state)

        #     new_state = tk.NORMAL
        #     if variations[-1] == next_move_str:
        #         new_state = tk.DISABLED
        #     self.demoteVarBtn.config(state=new_state)

        # new_state = tk.NORMAL
        # if len(variations) == 0:
        #     new_state = tk.DISABLED
        # self.frwdBtn.config(state=new_state)
        # self.frwdFullBtn.config(state=new_state)

        # # diable back buttons if can't go back no more
        # new_state = tk.NORMAL
        # if not has_parent:
        #     new_state = tk.DISABLED
        # self.backBtn.config(state=new_state)
        # self.backFullBtn.config(state=new_state)

    ###################################
    # Private
    ###################################
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

        for child in self.table.get_children(''):
            self.table.delete(child)
        for variation in variations:
            self.table.insert('', 'end', text=variation, values=variation)
