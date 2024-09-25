from customtkinter import CTkEntry, CTkButton, CTkFrame
from tkinter import ttk
import tkinter as tk

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('Rommukub App')
        self.init_variables()
        self.init_images()

    def init_variables(self):
        pass

    def init_images(self):
        pass

    def draw_gui(self):
        pass


if __name__ == '__main__':
    App = GUI()
    App.draw_gui()
    App.mainloop()
