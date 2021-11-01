from tkinter import LabelFrame, Button
from tkinter.constants import BOTH, EW
from functools import partial
from gui.view_model import config_view_model
from gui.gui_functions import popup_rectangle_window

def fishing_column_show_button(fishing_column):
    frame = LabelFrame(fishing_column)
    frame.grid(sticky=EW, row=4, column=0, padx=5, pady=3)

    button = Button(frame, text = "Show fishing position")
    button.pack(fill=BOTH)
    button.configure(
        command = partial(
            popup_rectangle_window, 
            button, 
            config_view_model['fishing']['left'], 
            config_view_model['fishing']['top'], 
            config_view_model['fishing']['width'], 
            config_view_model['fishing']['height']
        )
    )
