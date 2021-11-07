import ctypes
from app_config import config, RZCTL_DLL_PATH
from wrappers.logging_wrapper import info, error

def init_rzctl():
    """Initializes the Razer controller object if the following 
    conditions are met:
    
    1. Razer Synapse app is running
    2. Razer Synapse Macro Plugin is installed
    3. User is currently using a Razer mouse
    
    Otherwise the rzctl object is set to None and the winapi is used"""

    class Rzctl:

        class MouseClick:
            LEFT_DOWN = 1
            LEFT_UP = 2

        """Private class that handles the controlling of a Razer mouse
        via the custom Razer Synapse Macro Plugin."""

        def __init__(self, rzctl_mouse_move, rzctl_mouse_click, rzctl_key_state):
            self._rzctl_mouse_move = rzctl_mouse_move
            self._rzctl_mouse_click = rzctl_mouse_click
            self._rzctl_key_state = rzctl_key_state

        def mouse_move(self, x, y, from_start_point=False):
            """Moves the mouse pointer to a specific point on the screen

            x and y are both in pixels on on the main monitor only

            internal scaling is applied to handle the values excpected by
            the macro driver"""
            x = int(x * 65535 / config['resolution']['x'])
            y = int(y * 65535 / config['resolution']['y'])
            self._rzctl_mouse_move(x, y, from_start_point)

        def left_down(self):
            self._rzctl_mouse_click(
                Rzctl.MouseClick.LEFT_DOWN
                )

        def left_up(self):
            self._rzctl_mouse_click(
                Rzctl.MouseClick.LEFT_UP
                )

        # these aren't completely correct at the moment...
        # duplicate keys that have left and right keys (shift, ctrl, alt, etc.)
        # are supposed to pass 0, 1 and 2, 3 for left down/up, right down/up
        # respectively
        def key_down(self, scan_code):
            self._rzctl_key_state(
                scan_code, 0
                )

        def key_up(self, scan_code):
            self._rzctl_key_state(
                scan_code, 1
                )

    # Pretty much everything here can go wrong so just wrap it in a try
    # and figure it out for yourself
    try:
        lib = ctypes.CDLL(RZCTL_DLL_PATH)
        rzctl_init = getattr(lib, "?init@rzctl@@YA_NXZ")
        rzctl_init.restype = ctypes.c_bool

        if not rzctl_init():
            info('Unable initialize rzctl library')
            return None

        rzctl_mouse_move = getattr(lib, "?mouse_move@rzctl@@YAXHH_N@Z")
        rzctl_mouse_move.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_bool]
        rzctl_mouse_move.restype = None

        rzctl_mouse_click = getattr(lib, "?mouse_click@rzctl@@YAXH@Z")
        rzctl_mouse_click.argtypes = [ctypes.c_int]
        rzctl_mouse_click.restype = None

        rzctl_key_state = getattr(lib, "?key_state@rzctl@@YAXFF@Z")
        rzctl_key_state.argtypes = [ctypes.c_int16, ctypes.c_int16]
        rzctl_key_state.restype = None

        info('Rzctl library initialized!')

        return Rzctl(
            rzctl_mouse_move, 
            rzctl_mouse_click,
            rzctl_key_state
            )
    except Exception as ex:
        error('Something went wrong when initializing the rzctl object')
        error(ex)
        return None

rzctl = init_rzctl()