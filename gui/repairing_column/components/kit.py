from tkinter import Label, LabelFrame, Button
from tkinter.constants import LEFT, RIGHT, EW
from functools import partial
from view_model import config_view_model

def _change_repair_kit_state(button):
    var = config_view_model['repair']['use_repair_kit']
    var.set(not var.get())
    button.configure(
        text="YES" if var.get() else "NO",
        bg="green" if var.get() else "red"
    )

def repairing_column_kit(repairing_column):
    frame = LabelFrame(repairing_column)
    frame.grid(sticky=EW, row=4, column=0, padx=5, pady=(0, 5))
    
    label = Label(frame, text="Use repair kit:")
    label.pack(side=LEFT)

    button = Button(frame)
    button.pack(side=RIGHT, padx=3, pady=2)
    button.configure(
        command = partial(
            _change_repair_kit_state, 
            button
            ),
        text="YES" if config_view_model['repair']['use_repair_kit'].get() else "NO",
        bg="green" if config_view_model['repair']['use_repair_kit'].get() else "red",
    )
