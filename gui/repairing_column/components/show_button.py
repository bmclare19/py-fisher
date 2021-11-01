from tkinter import LabelFrame, Button
from tkinter.constants import EW, BOTH
from functools import partial
from gui.view_model import config_view_model
from gui.gui_functions import popup_rectangle_window

def repairing_column_show(repairing_column):
    frame = LabelFrame(repairing_column)
    frame.grid(sticky=EW, row=6, column=0, padx=5, pady=(0,3))

    button = Button(frame, text = "Show repair position")
    button.pack(fill=BOTH)
    button.configure(
        command = partial(
            popup_rectangle_window, 
            button, 
            config_view_model['repair']['ui_positions']['fishing_rod']['x'], 
            config_view_model['repair']['ui_positions']['fishing_rod']['y']
        )
    )
    
