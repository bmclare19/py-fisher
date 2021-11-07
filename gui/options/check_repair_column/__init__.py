from tkinter import Label, LabelFrame
from tkinter.constants import N, E, W

def check_repair_column(parent):
    from .components import check_repair_column_position, check_repair_column_size, \
        check_repair_column_show_button

    column_header = Label(parent, text = "Verify Ready")
    column_header.grid(row=0, column=1, pady=(3, 0))
    
    column = LabelFrame(parent)
    column.grid(sticky=(N, E, W), row=1, column=1, padx=5, pady=(0, 10))

    check_repair_column_position(column)
    check_repair_column_size(column)
    check_repair_column_show_button(column)