from rzctl import rzctl
from wrappers.logging_wrapper import info

if rzctl is None:
    info('rzctl object is not valid')
else:
    from time import sleep
    while True:
        rzctl.mouse_move(775, 175)
        sleep(1)