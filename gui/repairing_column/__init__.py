from tkinter import Label, LabelFrame, N, E, W

def repairing_column(tab):
    from .components import repairing_column_afk, repairing_column_enable, \
        repairing_column_interval, repairing_column_kit, \
            repairing_column_position, repairing_column_show

    repairing_column_header = Label(tab, text = "Repairing")
    repairing_column_header.grid(row=0, column=1, pady=(3, 0))

    repairing_column = LabelFrame(tab)
    repairing_column.grid(sticky=(N,E,W), row=1, column=1, padx=5, pady=(0, 10))

    repairing_column_position_header = Label(repairing_column, text = "Click position (px)")
    repairing_column_position_header.grid(row=0, column=0)

    repairing_column_position(repairing_column)
    repairing_column_interval(repairing_column)
    repairing_column_enable(repairing_column)
    repairing_column_kit(repairing_column)
    repairing_column_afk(repairing_column)
    repairing_column_show(repairing_column)
