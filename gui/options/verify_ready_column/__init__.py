from tkinter import Label, LabelFrame
from tkinter.constants import N, E, W

def verify_ready_column(parent):
    from .components import verify_ready_column_position, verify_ready_column_size, \
        verify_ready_column_enable, verify_ready_column_show_button

    column_header = Label(parent, text = "Verify Ready")
    column_header.grid(row=0, column=0, pady=(3, 0))
    
    column = LabelFrame(parent)
    column.grid(sticky=(N, E, W), row=1, column=0, padx=5, pady=(0, 10))

    verify_ready_column_position(column)
    verify_ready_column_size(column)
    verify_ready_column_enable(column)
    verify_ready_column_show_button(column)