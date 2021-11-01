from tkinter import Toplevel, Canvas, Variable
from tkinter.constants import TOP, BOTH
from wrappers.logging_wrapper import debug

class DraggableMixin:
    def __init__(self, *args, on_drag=None, **kwargs):
        super().__init__(*args, **kwargs)
        DraggableMixin.make_draggable(self, on_drag)

    @staticmethod
    def make_draggable(widget, on_drag=None):
        def _on_drag_start(event):
            widget = event.widget.winfo_toplevel()
            widget._drag_start_x = event.x
            widget._drag_start_y = event.y

        def _on_drag_motion(event):
            widget = event.widget.winfo_toplevel()
            x = widget.winfo_x() - widget._drag_start_x + event.x
            y = widget.winfo_y() - widget._drag_start_y + event.y
            widget.geometry("+%d+%d" % (x, y))
            if on_drag is not None: 
                on_drag(x, y)

        widget.bind("<Button-1>", _on_drag_start)
        widget.bind("<B1-Motion>", _on_drag_motion)

class FloatingWindow(Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overrideredirect(True)

class RectangleWindow(DraggableMixin, FloatingWindow):

    _inherent_window_padding = 2
    _border_thickness = 5
    _offset_half_thickness = int(_border_thickness / 2)

    def __init__(self, x, y, width, height, *args, **kwargs):
        super().__init__(*args, on_drag=self._on_drag, **kwargs)

        #view models
        self.x, self.y, self.width, self.height = x, y, width, height

        # previous values
        self._x, self._y, self._width, self._height = None, None, None, None

        self._variable_traces = []

        def __register_vm_updates(*vars_):
            for v in vars_:
                self._variable_traces.append(
                    (v, "write", v.trace_add("write", lambda *a: self._on_vm_update(v)))
                )
        __register_vm_updates(self.x, self.y, self.width, self.height)

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.bind('<Destroy>', self._on_closing)

        self.resizable(True, True)
        self.attributes('-topmost', True)
        self.wm_attributes('-transparentcolor', self['bg'])
        self.deiconify()

        self._canvas = Canvas(self)
        self._rectangle_id = None

        self._redraw()

    def _on_closing(self, *args):
        while len(self._variable_traces): 
            t = self._variable_traces.pop(0)
            t[0].trace_remove(t[1], t[2])
            
    def _on_vm_update(self, v):
        try:
            _ = v.get()
            # check if the view actually needs to be updated
            if self.x.get() != self._x or self.y.get() != self._y:
                self._redraw()
        except: 
            pass
    
    def _on_drag(self, x, y):
        """A callback that handles updating the view model when the 
        window position changed via DraggableMixin.
        
        Setting the view models will cause _on_vm_update to be called 
        effectively doing what has already been done so we need to prevent
        that from happening. We handle that case by setting a variable to
        the previous value and checking if the new value is different from
        the current."""
        # add the padding because padding calculation is handled internally
        # and the provided x and y values are really vm - padding
        self.x.set(x + self._inherent_window_padding)
        self._x = self.x.get()

        self.y.set(y + self._inherent_window_padding)
        self._y = self.y.get()

    def _redraw(self):
        if self._rectangle_id is not None:
            self._canvas.delete(self._rectangle_id)
            self._rectangle_id = None

        self.geometry(
            '%dx%d+%d+%d' % (
                self.width.get() + 2 * self._inherent_window_padding + 1, 
                self.height.get() + 2 * self._inherent_window_padding + 1, 
                self.x.get() - self._inherent_window_padding, 
                self.y.get() - self._inherent_window_padding
            )
        )

        self._rectangle_id = self._canvas.create_rectangle(
            self._offset_half_thickness + 2, 
            self._offset_half_thickness + 2, 
            self.width.get() + self._offset_half_thickness + 2 - self._border_thickness + 1, 
            self.height.get() + self._offset_half_thickness + 2 - self._border_thickness + 1,  
            outline="green", 
            width=self._border_thickness
        )
        self._canvas.pack(side=TOP, fill=BOTH, expand=True)
