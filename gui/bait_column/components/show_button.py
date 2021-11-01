from functools import partial
from tkinter import Button, Frame
from tkinter.constants import BOTH, BOTTOM, NSEW, TOP
from gui.view_model import config_view_model
from gui.gui_functions import popup_rectangle_window

def bait_column_show_button(bait_column):
    button_container = Frame(bait_column)
    button_container.grid(sticky=NSEW, row=5, column=0, padx=5, pady=(0, 4))

    # Show bait position

    show_bait_position_button = Button(button_container, text = "Show bait position")
    show_bait_position_button.pack(side=TOP, fill=BOTH, pady=(0, 3))
    show_bait_position_button.configure(
        command = partial(
            popup_rectangle_window, 
            show_bait_position_button, 
            config_view_model['bait']['ui_positions']['select']['x'],
            config_view_model['bait']['ui_positions']['select']['y']
            )
        )

    # Show equip bait button position
    
    show_equip_button_position_button = Button(button_container, text = "Show equip button position")
    show_equip_button_position_button.pack(side=BOTTOM, fill=BOTH)
    show_equip_button_position_button.configure(
        command = partial(
            popup_rectangle_window,
            show_equip_button_position_button,
            config_view_model['bait']['ui_positions']['equip']['x'],
            config_view_model['bait']['ui_positions']['equip']['y']
            )
        )
