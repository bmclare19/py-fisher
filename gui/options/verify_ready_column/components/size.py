from tkinter import Frame, Label, LabelFrame, Scale, Entry
from tkinter.constants import HORIZONTAL, EW
from view_model import config_view_model
from gui.validation import vcmd_factory

def verify_ready_column_size(column):
    header_label = Label(column, text = "Size (px)")
    header_label.grid(row=2, column=0)

    attributes_container = LabelFrame(column)
    attributes_container.grid(sticky=EW, row=3, column=0, padx=5)

    # Width

    width_container = Frame(attributes_container, height=1)
    width_container.grid(row=0, column=0, padx=5)

    width_label = Label(width_container, text="W:")
    width_label.grid(row=0, column=0, pady=(20, 0))

    width_scale = Scale(
        width_container,
         from_=0, 
         to=config_view_model['resolution']['x'].get(), 
         orient=HORIZONTAL, 
         variable=config_view_model['verification']['ready']['region']['width']
         )
    width_scale.grid(row=0, column=1)

    width_entry = Entry(
        width_container, 
        width=4, 
        textvariable=config_view_model['verification']['ready']['region']['width'],
        validate='key', 
        validatecommand=vcmd_factory(width_container, "int")
        )
    width_entry.grid(row=0, column=2, padx=3, pady=(20, 0))

    # Height

    height_container = Frame(attributes_container, height=1)
    height_container.grid(row=1, column=0, padx=5, pady=(0, 5))

    height_label = Label(height_container, text="H:")
    height_label.grid(row=0, column=0, pady=(20, 0))

    height_scale = Scale(
        height_container, 
        from_=0, 
        to=config_view_model['resolution']['y'].get(), 
        orient=HORIZONTAL, 
        variable=config_view_model['verification']['ready']['region']['height']
        )
    height_scale.grid(row=0, column=1)

    height_entry = Entry(
        height_container, 
        width=4, 
        textvariable=config_view_model['verification']['ready']['region']['height'],
        validate='key', 
        validatecommand=vcmd_factory(height_container, "int")
        )
    height_entry.grid(row=0, column=2, pady=(20, 0))
