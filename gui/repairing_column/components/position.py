from tkinter import Frame, Label, LabelFrame, Entry, Scale
from tkinter import HORIZONTAL, EW
from view_model import config_view_model
from gui.validation import vcmd_factory

def repairing_column_position(repairing_column):
    position_container = LabelFrame(repairing_column)
    position_container.grid(sticky=EW, row=1, column=0, padx=5, pady=(0, 5))

    # X

    x_container = Frame(position_container, height=1)
    x_container.grid(row=0, column=0, padx=5)

    x_label = Label(x_container, text="X:", anchor="s")
    x_label.grid(row=0, column=0, pady=(20, 0))

    x_scale = Scale(
        x_container, 
        from_=0, 
        to=config_view_model['resolution']['x'].get(), 
        orient=HORIZONTAL, 
        variable=config_view_model['repair']['ui_positions']['fishing_rod']['x']
        )
    x_scale.grid(row=0, column=1)

    x_entry = Entry(
        x_container, 
        width=4, 
        textvariable=config_view_model['repair']['ui_positions']['fishing_rod']['x'],
        validate='key', 
        validatecommand=vcmd_factory(x_container, "int")
        )
    x_entry.grid(row=0, column=2, pady=(20, 0))

    # Y

    y_container = Frame(position_container, height=1)
    y_container.grid(row=1, column=0, padx=5, pady=(0, 5))

    y_label = Label(y_container, text="Y:")
    y_label.grid(row=0, column=0, pady=(20, 0))

    y_scale = Scale(
        y_container, 
        from_=0, 
        to=config_view_model['resolution']['y'].get(), 
        orient=HORIZONTAL, 
        variable=config_view_model['repair']['ui_positions']['fishing_rod']['y']
        )
    y_scale.grid(row=0, column=1)

    y_entry = Entry(
        y_container, 
        width=4, 
        textvariable=config_view_model['repair']['ui_positions']['fishing_rod']['y'],
        validate='key', 
        validatecommand=vcmd_factory(y_container, "int")
        )
    y_entry.grid(row=0, column=2, pady=(20, 0))
