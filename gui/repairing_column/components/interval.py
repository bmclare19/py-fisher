from tkinter import Label, LabelFrame, Entry
from tkinter.constants import EW, E, RIGHT, W, SE
from view_model import config_view_model

def repairing_column_interval(repairing_column):
    frame = LabelFrame(repairing_column)
    frame.grid(sticky=EW, row=2, column=0, padx=5, pady=(0, 5))

    label = Label(frame, text = "Repair interval:")
    label.grid(sticky=W, row=0, column=0)

    entry = Entry(
        frame, 
        width=6,
        font=("default", 12),
        textvariable=config_view_model['repair']['interval'],
        justify=RIGHT
        )
    entry.grid(sticky=E, row=0, column=1, pady=4)

    seconds_label = Label(frame, text="s")
    seconds_label.grid(sticky=SE, row=0, column=2, padx=3, pady=4)

    frame.grid_columnconfigure(1, weight=1)
