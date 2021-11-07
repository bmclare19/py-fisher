from functools import partial
from tkinter import IntVar
from .widgets import RectangleWindow

def popup_rectangle_window(button, x, y, width=IntVar(value=25), height=IntVar(value=25)):
    window = RectangleWindow(x, y, width, height)

    button.configure(
        command = partial(
            destroy_rectangle_window, 
            window, button, x, y, width, height
        )
    )

def destroy_rectangle_window(window, button, x, y, width, height):
    window.destroy()
    button.configure(
        command = partial(
            popup_rectangle_window,
            button, x, y, width, height
        )
    )