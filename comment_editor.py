# /usr/bin/python
import tkinter as tk
from tkinter import messagebox

def geo_str2list(geo_str):
    geo_str = geo_str.replace('+', ' ')
    geo_str = geo_str.replace('x', ' ')
    geo = geo_str.split(' ')
    geo = [int(i) for i in geo]
    return geo

class CommentEditor(tk.Frame):
    def __init__(self, ce_parent, main_parent, title_str, save_comment_cb, on_closing_comment_editor_cb):
        tk.Frame.__init__(self, ce_parent)

        self.parent = ce_parent
        self.parent.title(title_str + '. Comment editor')
        self.parent.protocol("WM_DELETE_WINDOW", on_closing_comment_editor_cb)

        self.f1 = tk.Frame(ce_parent)
        self.f1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.editor = tk.Text(self.f1, undo=True)

        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind("<<Modified>>", self.handle_modified)

        self.scroll = tk.Scrollbar(self.f1)
        self.scroll.pack(side=tk.LEFT, fill=tk.Y)

        self.scroll.config(command=self.editor.yview)
        self.editor.config(yscrollcommand=self.scroll.set)

        self.save_button = tk.Button(ce_parent, text='Save')
        self.save_button.pack(side=tk.BOTTOM)
        self.save_button.config(command=self.save_comment)

        screenw = main_parent.winfo_screenwidth()
        # screenh = main_parent.winfo_screenheight()
        ce_parent.update_idletasks()
        # geo = [w, h, x, y]
        ce_geo = geo_str2list(ce_parent.geometry())
        main_parent_geo = geo_str2list(main_parent.geometry())
        # put left of ce against right of parent
        ce_geo[2] = main_parent_geo[2] + main_parent_geo[0]
        # if right of ce off screen, then
        if ce_geo[2] + ce_geo[0] > screenw:
            # put right of ce against right of screen
            ce_geo[2] = screenw - ce_geo[0]
        ce_parent.geometry("%dx%d+%d+%d" % tuple(ce_geo))
        # don't let it get too small for the button to show
        ce_parent.minsize(width=ce_geo[0], height=ce_geo[1])

        self.pack()
        self.editor.focus()
        self.save_comment_cb = save_comment_cb

    # public
    def update_comment(self, comment):
        self.editor.replace(1.0, tk.END, comment)
        self.set_not_dirty()

    def get_comment(self):
        comment = self.editor.get(1.0, tk.END)
        return comment[0:-1]

    def check_comment(self):
        if self.editor.edit_modified():
            resp = messagebox.askyesnocancel('Save comment?', 'The comment has been edited. Save?')
            print('resp', resp)
            if resp is None:
                return False
            elif resp is True:
                self.save_comment()
        return True

    # private
    def set_not_dirty(self):
        self.save_button.configure(state=tk.DISABLED)
        self.editor.edit_modified(False)

    def save_comment(self):
        self.save_comment_cb()
        self.set_not_dirty()

    def handle_modified(self, event):
        if self.editor.edit_modified():
            self.save_button.configure(state=tk.NORMAL)
