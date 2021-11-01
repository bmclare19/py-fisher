from tkinter import Label, LabelFrame
from tkinter.constants import N, E, W
from gui import root
from gui.fishing_column.components.attributes import *
from gui.fishing_column.components.position import *
from gui.fishing_column.components.show_button import *

def fishing_column():
    fishing_column_header = Label(root, text = "Fishing")
    fishing_column_header.grid(row=0, column=0, pady=(3, 0))
    
    fishing_column = LabelFrame(root)
    fishing_column.grid(sticky=(N, E, W), row=1, column=0, padx=5, pady=(0, 10))

    fishing_column_position(fishing_column)
    fishing_column_attributes(fishing_column)
    fishing_column_show_button(fishing_column)