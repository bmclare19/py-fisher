from functools import partial
from tkinter import Button, LabelFrame
from tkinter.constants import DISABLED, NORMAL
from gui import root
from fishing import fisher
from wrappers.logging_wrapper import info

def _change_fishing_state(button):
    continue_ = fisher.continue_fishing = not fisher.continue_fishing
    button.configure(
        text="Stop fishing" if continue_ else "Start fishing",
        command=partial(
            _change_fishing_state if continue_ else _start_fishing, 
            button
        )
    )

def _start_fishing(button):
    _change_fishing_state(button)
    def _start():
        button.configure(state=NORMAL)
        fisher.update()
    button.configure(state=DISABLED)
    root.after(5000, _start)
    info("Starting fishing in 5 seconds...")

def start_fishing_button(tab):
    start_fishing_container = LabelFrame(tab)
    start_fishing_container.grid(row=3, columnspan=4, padx=(10, 0), pady=(15, 0))

    start_fishing_button = Button(start_fishing_container, text = "Start fishing", font=18)
    start_fishing_button.grid(row=0, column=0)
    start_fishing_button.configure(
        command = partial(
            _start_fishing, 
            start_fishing_button
        )
    )
