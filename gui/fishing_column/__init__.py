from tkinter import Label, LabelFrame
from tkinter.constants import N, E, W

def fishing_column(tab):
    from .components import fishing_column_position, fishing_column_show_button, \
        fishing_column_size

    fishing_column_header = Label(tab, text = "Fishing")
    fishing_column_header.grid(row=0, column=0, pady=(3, 0))
    
    fishing_column = LabelFrame(tab)
    fishing_column.grid(sticky=(N, E, W), row=1, column=0, padx=5, pady=(0, 10))

    fishing_column_position(fishing_column)
    fishing_column_size(fishing_column)
    fishing_column_show_button(fishing_column)