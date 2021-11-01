import win32api, win32con
from random import randint
from time import sleep
from rzctl import rzctl

VK_CODE = {
    'f3': 0x72,
    'F3': 0x72, 
    'f4': 0x73,
    'F4': 0x73, 
    'tab': 0x09,
    'esc': 0x1b,
    'a': 0x41,
    'b': 0x42,
    'd': 0x44,
    'e': 0x45,
    'r': 0x52,
    't': 0x54,
    'v': 0x56
}

# Random utilities

RANDOM_TIMEOUT_MIN = 45
RANDOM_TIMEOUT_MAX = 195

def random_timeout_ms(minimum=45, maximum=195):
    return randint(45, 195)

def random_timeout(minimum=45, maximum=195):
    return random_timeout_ms(minimum, maximum) / 1000

def random_timeout_key():
    return random_timeout()

def random_timeout_mouse():
    return random_timeout(30, 90)

def random_timeout_between():
    return random_timeout(10, 50)

# Key API

def key_down(key):
    win32api.keybd_event(
        VK_CODE[key], 0, 0, 0
        )

def key_up(key):
    win32api.keybd_event(
        VK_CODE[key], 0, win32con.KEYEVENTF_KEYUP, 0
        )

def press_key(key, timeout_ms=0):
    timeout_s = timeout_ms / 1000 if timeout_ms > 0 \
        else random_timeout_key()
    key_down(key)
    sleep(timeout_s)
    key_up(key)
    sleep(random_timeout_between())

# Mouse API

def move_mouse(x, y):
    if rzctl is None:
        win32api.SetCursorPos((x, y))
    else:
        rzctl.mouse_move(x, y)

def left_down():
    if rzctl is None:
        win32api.mouse_event(
            win32con.MOUSEEVENTF_LEFTDOWN, 0, 0
            )
    else:
        rzctl.left_down()

def left_up():
    if rzctl is None:
        win32api.mouse_event(
            win32con.MOUSEEVENTF_LEFTUP, 0, 0
            )
    else:
        rzctl.left_up()

def left_click(timeout_ms=0):
    timeout_s = timeout_ms / 1000 if timeout_ms > 0 \
        else random_timeout_mouse()
    left_down()
    sleep(timeout_s)
    left_up()
    sleep(random_timeout_between())

# Helpers

def click_mouse_with_coordinates(x, y):
    move_mouse(x, y)
    sleep(random_timeout_mouse())
    left_click()