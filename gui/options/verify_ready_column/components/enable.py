from functools import partial
from tkinter import Label, LabelFrame, Button
from tkinter.constants import LEFT, RIGHT, EW
from view_model import config_view_model

def _update(button, vm):
    vm.set(not vm.get())
    button.configure(
        text="ON" if vm.get() else "OFF",
        bg="green" if vm.get() else "red"
    )

def verify_ready_column_enable(column):
    frame = LabelFrame(column)
    frame.grid(sticky=EW, row=4, column=0, padx=5, pady=(5, 0))

    label = Label(frame, text="Status:")
    label.pack(side=LEFT)

    vm = config_view_model['verification']['ready']['enabled']
    button = Button(frame)
    button.pack(side=RIGHT, padx=3, pady=2)
    button.configure(
        command = partial(
            _update, 
            button,
            vm
        ),
        text="ON" if vm.get() else "OFF",
        bg="green" if vm.get() else "red",
    )
    