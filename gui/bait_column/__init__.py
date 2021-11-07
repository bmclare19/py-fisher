from tkinter import Label, LabelFrame
from tkinter.constants import N, E, W

def bait_column(tab):
    from .components import bait_column_position, bait_column_enable, \
        bait_column_equip_position, bait_column_show_button

    bait_column_header = Label(tab, text = "Bait")
    bait_column_header.grid(row=0, column=2, pady=(3, 0))
    
    bait_column = LabelFrame(tab)
    bait_column.grid(sticky=(N, E, W), row=1, column=2, padx=5, pady=(0, 10))

    bait_column_position(bait_column)
    bait_column_equip_position(bait_column)
    bait_column_enable(bait_column)
    bait_column_show_button(bait_column)