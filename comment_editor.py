__author__ = 'colindavey'
import tkinter as tk

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

    def update_comment(self, comment):
        self.editor.replace(1.0, tk.END, comment)
        # self.save_button.configure(state=tk.DISABLED)
        # self.editor.edit_modified(False)
        self.set_not_dirty()

    def save_comment(self):
        comment = self.editor.get(1.0, tk.END)
        comment = comment[0:-1]
        print('comment:', comment)
        self.save_comment_cb(comment)
        # self.save_button.configure(state=tk.DISABLED)
        # self.editor.edit_modified(False)
        self.set_not_dirty()

    def set_not_dirty(self):
        print('not dirty')
        self.save_button.configure(state=tk.DISABLED)
        self.editor.edit_modified(False)

    def handle_modified(self, event):
        print('handle_modified: ', self.editor.edit_modified())
        self.save_button.configure(state=tk.NORMAL)

    # def handle_button(self):
    #     print('save button')

    # def set_text(self, text):
    #     self.editor.replace(1.0, END, text)
    #     self.editor.delete(END, END-1)
    #     # self.editor.insert(END, text)
    #
    # def get_text(self):
    #     return self.editor.get(1.0, END)

# def editor2editor(ed1, ed2):
#     the_string = ed1.get(1.0, tk.END)
#     # this is needed to strip the newline that mysteriously is appended
#     the_string = the_string[0:-1]
#     ed2.replace(1.0, tk.END, the_string)

# class CommentEditorApp(object):
#     def __init__(self, parent=None, model=None):

#         self.parent = parent
#         self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

#         self.editor = tk.Text(parent)
#         self.editor.pack()

#         self.comment_button = tk.Button(self.parent, text='{}', command=self.handle_button)
#         self.comment_button.pack()
#         self.ce_root = None

#     def run(self):
#         tk.mainloop()

#     def save_comment(self):
#         editor2editor(self.ce.editor, self.editor)
#         self.editor.edit_modified(False)
#         self.ce.save_button.configure(state=tk.DISABLED)

#     def handle_button(self):
#         print('{} button')
#         if self.ce_root is None:
#             self.ce_root = tk.Tk()
#             self.ce_root.protocol("WM_DELETE_WINDOW", self.on_closing_comment_editor)
#             self.ce = CommentEditor(self.ce_root)
#             self.ce.save_button.config(command=self.save_comment)

#         # low level tk stuff
#         self.ce_root.lift()
#         self.ce_root.update()
#         editor2editor(self.editor, self.ce.editor)
#         self.ce.save_button.configure(state=tk.DISABLED)

#     def on_closing_comment_editor(self):
#         print('closing')
#         self.ce_root.destroy()
#         self.ce_root = None

#     def on_closing(self):
#         if self.ce_root is not None:
#             self.ce_root.destroy()
#         self.parent.destroy()

# if __name__ == "__main__":

#     the_parent = tk.Tk()
#     cea = CommentEditorApp(the_parent)
#     cea.run()

