# /usr/bin/python
import tkinter as tk
import tkinter.ttk as tktree

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
                # !!!range
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
