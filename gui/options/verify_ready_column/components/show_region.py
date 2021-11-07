from functools import partial
from tkinter import LabelFrame, Button
from tkinter.constants import BOTH, EW
from view_model import config_view_model
from gui.gui_functions import popup_rectangle_window

def verify_ready_column_show_button(column):
    frame = LabelFrame(column)
    frame.grid(sticky=EW, row=5, column=0, padx=5, pady=(5, 3))

    button = Button(frame, text = "Show verify ready position")
    button.pack(fill=BOTH)
    button.configure(
        command = partial(
            popup_rectangle_window, 
            button, 
            config_view_model['verification']['ready']['region']['left'], 
            config_view_model['verification']['ready']['region']['top'], 
            config_view_model['verification']['ready']['region']['width'], 
            config_view_model['verification']['ready']['region']['height']
        )
    )
