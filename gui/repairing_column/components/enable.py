from functools import partial
from tkinter import Label, LabelFrame, Button
from tkinter.constants import LEFT, RIGHT, EW
from view_model import config_view_model

def _change_repair_button_state(button):
    var = config_view_model['repair']['enabled']
    var.set(not var.get())
    button.configure(
        text="ON" if var.get() else "OFF",
        bg="green" if var.get() else "red"
    )

def repairing_column_enable(repairing_column):
    frame = LabelFrame(repairing_column)
    frame.grid(sticky=EW, row=3, column=0, padx=5, pady=(0, 5))

    label = Label(frame, text="Enable repairs:")
    label.pack(side=LEFT)

    button = Button(frame)
    button.pack(side=RIGHT, padx=3, pady=2)
    button.configure(
        command = partial(
            _change_repair_button_state, 
            button
        ),
        text="ON" if config_view_model['repair']['enabled'].get() else "OFF",
        bg="green" if config_view_model['repair']['enabled'].get() else "red",
    )