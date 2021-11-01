from functools import partial
from tkinter import IntVar
from tkinter.constants import DISABLED, NORMAL
from gui import root
from gui.view_model import config_view_model, save_data
from gui.widgets.top_levels import RectangleWindow
from fishing import fisher
from wrappers.logging_wrapper import info

def popup_rectangle_window(button, x, y, width=IntVar(value=25), height=IntVar(value=25)):
    window = RectangleWindow(x, y, width, height)

    button.configure(
        command = partial(
            destroy_rectangle_window, 
            window, button, x, y, width, height
        )
    )

def destroy_rectangle_window(window, button, x, y, width, height):
    window.destroy()
    button.configure(
        command = partial(
            popup_rectangle_window,
            button, x, y, width, height
        )
    )

def on_closing():
    save_data()
    root.destroy()

def change_repair_afk_state(button):
    var = config_view_model['afk_prevention']['enabled']
    var.set(not var.get())
    button.configure(
        text="YES" if var.get() else "NO",
        bg="green" if var.get() else "red"
    )

def change_repair_kit_state(button):
    var = config_view_model['repair']['use_repair_kit']
    var.set(not var.get())
    button.configure(
        text="YES" if var.get() else "NO",
        bg="green" if var.get() else "red"
    )

def change_repair_button_state(button):
    var = config_view_model['repair']['enabled']
    var.set(not var.get())
    button.configure(
        text="ON" if var.get() else "OFF",
        bg="green" if var.get() else "red"
    )

def change_bait_button_state(button):
    var = config_view_model['bait']['enabled']
    var.set(not var.get())
    button.configure(
        text="ON" if var.get() else "OFF",
        bg="green" if var.get() else "red"
    )

def change_fishing_state(button):
    continue_ = fisher.continue_fishing = not fisher.continue_fishing
    button.configure(
        text="Stop fishing" if continue_ else "Start fishing",
        command=partial(
            change_fishing_state if continue_ else start_fishing, 
            button
        )
    )

def start_fishing(button):
    change_fishing_state(button)
    def __start():
        button.configure(state=NORMAL)
        fisher.update()
    button.configure(state=DISABLED)
    root.after(5000, __start)
    info("Starting fishing in 5 seconds...")
    