__author__ = 'colindavey'
import tkinter as tk
from tkinter import *

def editor2editor(ed1, ed2):
    the_string = ed1.get(1.0, END)
    # this is needed to strip the newline that mysteriously is appended
    the_string = the_string[0:-1]
    ed2.replace(1.0, END, the_string)


class CommentEditor(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.f1 = Frame(parent)
        self.f1.pack(side=TOP, fill=BOTH, expand=True)
        self.editor = tk.Text(self.f1, undo=True)

        self.editor.pack(side=LEFT, fill=BOTH, expand=True)
        self.editor.bind("<<Modified>>", self.handle_modified)

        self.scroll = Scrollbar(self.f1)
        self.scroll.pack(side=LEFT, fill=Y)

        self.scroll.config(command=self.editor.yview)
        self.editor.config(yscrollcommand=self.scroll.set)

        self.save_button = tk.Button(parent, text='Save')
        self.save_button.pack(side=BOTTOM)

        self.pack()
        self.editor.focus()

    def handle_modified(self, event):
        print('modified: ', self.editor.edit_modified())
        self.save_button.configure(state=tk.NORMAL)

    def handle_button(self):
        print('save button')

    # def set_text(self, text):
    #     self.editor.replace(1.0, END, text)
    #     self.editor.delete(END, END-1)
    #     # self.editor.insert(END, text)
    #
    # def get_text(self):
    #     return self.editor.get(1.0, END)

class CommentEditorApp(object):
    def __init__(self, parent=None, model=None):

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.editor = tk.Text(parent)
        self.editor.pack()

        self.comment_button = tk.Button(self.parent, text='{}', command=self.handle_button)
        self.comment_button.pack()
        self.ce_root = None

    def run(self):
        tk.mainloop()

    def save_comment(self):
        editor2editor(self.ce.editor, self.editor)
        self.editor.edit_modified(False)
        self.ce.save_button.configure(state=tk.DISABLED)

    def handle_button(self):
        print('{} button')
        if self.ce_root is None:
            self.ce_root = Tk()
            self.ce_root.protocol("WM_DELETE_WINDOW", self.on_closing_comment_editor)
            self.ce = CommentEditor(self.ce_root)
            self.ce.save_button.config(command=self.save_comment)

        # low level tk stuff
        self.ce_root.lift()
        self.ce_root.update()
        editor2editor(self.editor, self.ce.editor)
        self.ce.save_button.configure(state=tk.DISABLED)

    def on_closing_comment_editor(self):
        print('closing')
        self.ce_root.destroy()
        self.ce_root = None

    def on_closing(self):
        if self.ce_root is not None:
            self.ce_root.destroy()
        self.parent.destroy()

if __name__ == "__main__":

    the_parent = tk.Tk()
    cea = CommentEditorApp(the_parent)
    cea.run()




