import random, string
from functools import partial
from tkinter import Tk
from concurrent.futures import ThreadPoolExecutor

root = Tk()
worker_pool = ThreadPoolExecutor(max_workers=1)

def gui_init(icon_path):
    from gui.gui_functions import on_closing
    from gui.fishing_column.fishing_column import fishing_column
    from gui.repairing_column.repairing_column import repairing_column
    from gui.bait_column.bait_column import bait_column
    from gui.start_fishing_button.start_fishing_button import start_fishing_button
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", partial(on_closing))
    fishing_column()
    repairing_column()
    bait_column()
    start_fishing_button()
    root.iconbitmap(icon_path)
    root.title(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
    return root