from tkinter import Label, LabelFrame
from tkinter.constants import N, E, W
from gui import root
from gui.bait_column.components.enable import *
from gui.bait_column.components.position import *
from gui.bait_column.components.equip_position import *
from gui.bait_column.components.show_button import *

def bait_column():
    bait_column_header = Label(root, text = "Bait")
    bait_column_header.grid(row=0, column=3, pady=(3, 0))
    
    bait_column = LabelFrame(root)
    bait_column.grid(sticky=(N, E, W), row=1, column=3, padx=5, pady=(0, 10))

    bait_column_position(bait_column)
    bait_column_equip_position(bait_column)
    bait_column_enable(bait_column)
    bait_column_show_button(bait_column)