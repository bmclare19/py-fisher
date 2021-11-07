import random, string
from functools import partial
from tkinter import Tk, ttk
from concurrent.futures import ThreadPoolExecutor

root = Tk()
worker_pool = ThreadPoolExecutor(max_workers=1)

def _init_options_tab(tab):
    from .options import verify_ready_column
    from .options import check_repair_column

    verify_ready_column(tab)
    check_repair_column(tab)

def _init_fishing_tab(tab):
    from .fishing_column import fishing_column
    from .repairing_column import repairing_column
    from .bait_column import bait_column
    from .start_fishing_button import start_fishing_button

    fishing_column(tab)
    repairing_column(tab)
    bait_column(tab)
    start_fishing_button(tab)

def gui_init(icon_path):
    def _on_closing():
        from view_model import save_data
        save_data()
        root.destroy()

    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", partial(_on_closing))
    root.iconbitmap(icon_path)
    root.title(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))

    tab_parent = ttk.Notebook(root)

    # Create fishing tab
    fishing_tab = ttk.Frame(tab_parent)
    _init_fishing_tab(fishing_tab)
    tab_parent.add(fishing_tab, text='Fishing')

    # Create options tab
    options_tab = ttk.Frame(tab_parent)
    _init_options_tab(options_tab)
    tab_parent.add(options_tab, text='Options')

    tab_parent.pack(expand=1, fill='both')
    return root