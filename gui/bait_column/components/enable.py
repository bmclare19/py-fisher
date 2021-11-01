from functools import partial
from tkinter import Label, LabelFrame, Button
from tkinter.constants import EW, LEFT, RIGHT
from gui.gui_functions import change_bait_button_state
from gui.view_model import config_view_model

def bait_column_enable(bait_column):
    frame = LabelFrame(bait_column)
    frame.grid(sticky=EW, row=4, column=0, padx=5, pady=(0, 5))

    label = Label(frame, text="Enable bait:")
    label.pack(side=LEFT)

    button = Button(frame)
    button.pack(side=RIGHT, padx=3, pady=2)
    button.configure(
        command = partial(
            change_bait_button_state, 
            button
            ),
        text="ON" if config_view_model['bait']['enabled'].get() else "OFF",
        bg="green" if config_view_model['bait']['enabled'].get() else "red",
    )