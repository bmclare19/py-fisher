from time import time
from .helpers import Region, TimeoutRange, Vec2
from .scanner import scanner
from wrappers.logging_wrapper import info, trace, error
from wrappers.win32api_wrapper import left_down, left_up, key_up, key_down, move_mouse

class Waiter:

    def __init__(self):
        self.waiting = False
        self.wait_start = None
        self.wait_timeout_ms = None

    def start(self, tr):
        self.wait_timeout_ms = tr.random_timeout_ms() \
            if isinstance(tr, TimeoutRange) else tr
        self.waiting = True
        self.wait_start = time()

    def is_waiting(self):
        if self.waiting:
            elapsed_ms = (time() - self.wait_start) * 1000
            done_waiting = elapsed_ms >= self.wait_timeout_ms
            self.waiting = not done_waiting
        return self.waiting

    def reset(self):
        self.waiting = False
        self.wait_start = None
        self.wait_timeout_ms = None

class BaseSequence:
    NAME = ''
    
    class State:
        INIT = 'INIT'
        WAITING = 'WAITING'
        RUN_CHILD = 'RUN_CHILD'
        COMPLETE = 'COMPLETE'
        ERROR = 'ERROR'

    def __init__(self, start_state=None):
        # state objects
        self._start_state = start_state if start_state is not None else self.State.INIT
        self._state = None
        self._next_state = self._start_state

        # waiter object
        self.waiter = Waiter()

        self._sequence_start = None
        self._update_count = 0

        self._child = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        """Verifies value is a valid state for this object and then checks
        if the new state is different than the old state and if so updates
        both the underlying private self._state object and the new sequence
        start time"""
        if not hasattr(self.State, value):
            raise ValueError(
                'State %s is invalid for %s' % (value, type(self).__name__)
                )
        if self._state != value:
            self._sequence_start = time()
            self._state = value
            trace('%s: %s' % (self.NAME, self.state))

    @property
    def is_first_run(self):
        return self._update_count == 0

    @property
    def state_elapsed_ms(self):
        return 0 if self._sequence_start is None else \
            (time() - self._sequence_start) * 1000

    def is_error(self):
        """Returns the duration of the current sequence in ms"""
        return self.state == self.State.ERROR or \
            self.state_elapsed_ms > 25000

    def reset(self):
        self._state = None
        self._next_state = self._start_state
        self._sequence_start = None
        self._update_count = 0
        self.waiter.reset()
        return self

    def _wait_then(self, tr, next_state):
        self.waiter.start(tr)
        self.state = self.State.WAITING
        self._next_state = next_state

    def _run_child_then(self, child, next_state):
        self._child = child
        self.state = self.State.RUN_CHILD
        self._next_state = next_state

    def _update(self):
        raise NotImplementedError(
            "Implement me bitch"
            )

    def update(self):
        if self.is_first_run:
            trace('%s: %s' % (self.NAME, self.state))

        if self._child is not None:
            if not self._child.update(): return False
            else: self._child = None

        # use the wait object to handle all waiting states
        if self.waiter.is_waiting():
            return False

        # there is only a next state if we were waiting so check
        # if there is and if so update the current state
        if self._next_state is not None:
            self.state = self._next_state
            self._next_state = None

        # call implementation based update
        try:
            self._update()
        except Exception as err:
            error(err)
            self.state = self.State.ERROR

        self._update_count += 1

        return self.state == self.State.COMPLETE

class VerifyingStartSequence(BaseSequence):
    """Verifies that fishing is ready to start by scanning 
    for the presence of the fishing menu. 
    
    Occassionaly this menu won't show up so to handle that we
    have a max time that we are allowed to do this step and if 
    after max time we don't find anything then we proceed."""

    NAME = 'VERIFYING_START'

    class State(BaseSequence.State):
        SCANNING_FOR_START = 'SCANNING_FOR_START'

    def __init__(self, vm):
        super().__init__(self.State.SCANNING_FOR_START)
        self.vm = vm
        self._max_duration = 5000
        self._region = Region(
            vm['verification']['ready']['region']
            )

    @property
    def enabled(self):
        return self.vm['verification']['ready']['enabled'].get()

    def _update(self):
        if not self.enabled:
            self.state = self.State.COMPLETE
            return

        if self.state_elapsed_ms > self._max_duration:
            raise RuntimeError(
                'Max wait time elapsed without verifying ready state'
                )

        if self.state == self.State.SCANNING_FOR_START:
            if scanner.check_fishing_ready(self._region.bbox):
                info('Verified ready state')
                self.state = self.State.COMPLETE

class CastingSequence(BaseSequence):
    NAME = 'CASTING'

    class State(BaseSequence.State):
        FREE_LOOK = 'FREE_LOOK'
        CAST_START = 'CAST_START'
        CAST_END = 'CAST_END'
        VERIFY_CAST = 'VERIFY_CAST'

    def __init__(self, vm):
        super().__init__()
        self.vm = vm

        self.free_look_key = self.vm['key_bindings']['free_look']

        # Timeout objects
        self.free_look_anim_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['free_look']
            )
        self.casting_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['casting']
            )
        self.cast_tr = TimeoutRange(
            self.vm['fishing']['timeouts']\
                ['cast']
            )

    def _update(self):
        if self.state == self.State.INIT:
            key_up(self.free_look_key.get())
            self._wait_then(
                self.free_look_anim_tr,
                self.State.FREE_LOOK
                )
        elif self.state == self.State.FREE_LOOK:
            key_down(self.free_look_key.get())
            self._wait_then(
                250,
                self.State.CAST_START
                )
        elif self.state == self.State.CAST_START:
            left_down()
            self._wait_then(
                self.cast_tr,
                self.State.CAST_END
                )
        elif self.state == self.State.CAST_END:
            left_up()
            self._wait_then(
                self.casting_tr,
                self.State.VERIFY_CAST
                )
        elif self.state == self.State.VERIFY_CAST:
            if scanner.check_waiting_for_fish():
                self.state = self.State.COMPLETE

class ScanningForFishSequence(BaseSequence):
    NAME = 'SCANNING_FOR_FISH'

    class State(BaseSequence.State):
        SCANNING_FOR_FISH = 'SCANNING_FOR_FISH'

    def __init__(self, vm):
        super().__init__(self.State.SCANNING_FOR_FISH)
        self.vm = vm

        # Timeout objects
        self.noticed_tr = TimeoutRange(
            self.vm['fishing']['timeouts']\
                ['noticed']
            )
        self.click_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['click']
            )

    def _update(self):
        if self.state == self.State.SCANNING_FOR_FISH:
            result = scanner.check_fish_noticed()
            if result == True:
                info("Fish noticed!")
                self.state = self.State.COMPLETE

class FishNoticedSequence(BaseSequence):
    NAME = 'FISH_NOTICED'

    class State(BaseSequence.State):
        NOTICED_START = 'NOTICED_START'
        NOTICED_END = 'NOTICED_END'

    def __init__(self, vm):
        super().__init__(self.State.NOTICED_START)
        self.vm = vm

        # Timeout objects
        self.noticed_tr = TimeoutRange(
            self.vm['fishing']['timeouts']\
                ['noticed']
            )
        self.click_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['click']
            )

    def _update(self):
        if self.state == self.State.NOTICED_START:
            left_down()
            self._wait_then(
                self.noticed_tr,
                self.State.NOTICED_END
                )
        elif self.state == self.State.NOTICED_END:
            left_up()
            self._wait_then(
                self.click_tr, 
                self.State.COMPLETE
            )

class ReelingSequence(BaseSequence):
    NAME = 'REELING'

    class State(BaseSequence.State):
        UNKNOWN = 'UNKNOWN'
        GREEN = 'GREEN'
        ORANGE = 'ORANGE'
        RED = 'RED'
        RESET = 'RESET'

    def __init__(self, vm):
        super().__init__(self.State.UNKNOWN)
        self.vm = vm

        # Timeout objects
        self.click_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['click']
            )

        self._reset_max = 0.9
        self._reset_min = 0.6
        self._reset_max_wait = 4000

    def is_reel_reset(self):
        # store this because it's a dynamically calculated property
        elapsed = self.state_elapsed_ms
        if elapsed >= self._reset_max_wait:
            info('Max wait time for reel reset reached')
            return True
        current_threshold_change = (self._reset_max - self._reset_min) * \
            (elapsed / self._reset_max_wait)
        threshold = self._reset_max - current_threshold_change
        return scanner.can_start_reeling_again(threshold=threshold)

    def _update(self):
        if self.state == self.State.RESET:
            if not self.is_reel_reset():
                return

        self.state = scanner.get_reeling_state()\
            .upper()
        
        if self.state == self.State.GREEN:
            left_down()
        elif self.state in [self.State.RED]:
            left_up()
            self.state = self.State.RESET
        elif self.state == self.State.UNKNOWN:
            left_up()
            # if we've been in an unknown state for 1500 ms then we 
            # assume that we've caught the fish
            if self.state_elapsed_ms > 1500:
                info("Fish caught!")
                self.state = self.State.COMPLETE

class FishCaughtSequence(BaseSequence):
    NAME = 'FISH_CAUGHT'

    class State(BaseSequence.State):
        CAUGHT_START = 'CAUGHT_START'
        CAUGHT_END = 'CAUGHT_END'

    def __init__(self, vm):
        super().__init__()
        self.vm = vm

        # Timeout objects
        self.fish_caught_anim_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['fish_caught']
            )

        self.click_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['click']
            )

    def _update(self):
        if self.state == self.State.INIT:
            self._wait_then(
                1500,
                self.State.CAUGHT_START
                )
        elif self.state == self.State.CAUGHT_START:
            left_down()
            self._wait_then(
                self.click_tr,
                self.State.CAUGHT_END
            )
        elif self.state == self.State.CAUGHT_END:
            left_up()
            self._wait_then(
                self.fish_caught_anim_tr,
                self.State.COMPLETE
                )

class ResetSequence(BaseSequence):
    NAME = 'RESETTING'

    class State(BaseSequence.State):
        RESET_MOUSE_STATE = 'RESET_MOUSE_STATE'
        RESET_FREE_LOOK = 'RESET_FREE_LOOK'
        ESCAPE_START = 'ESCAPE_START'
        ESCAPE_END = 'ESCAPE_END'
        INVENTORY_OPEN_START = 'INVENTORY_OPEN_START'
        INVENTORY_OPEN_END = 'INVENTORY_OPEN_END'
        INVENTORY_CLOSE_START = 'INVENTORY_CLOSE_START'
        INVENTORY_CLOSE_END = 'INVENTORY_CLOSE_END'
        TOGGLE_FISHING_START = 'TOGGLE_FISHING_START'
        TOGGLE_FISHING_END = 'TOGGLE_FISHING_END'

    def __init__(self, vm):
        super().__init__()
        self.vm = vm

        self.toggle_fishing_mode_key = vm['key_bindings']['toggle_fishing_mode']
        self.escape_key = vm['key_bindings']['escape']
        self.inventory_key = vm['key_bindings']['inventory']
        self.free_look_key = vm['key_bindings']['free_look']

        # Animation timeout objects
        self.toggle_fishing_mode_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['toggle_fishing_mode']
            )
        self.inventory_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['inventory']
            )
        self.escape_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['escape']
            )
        
        # Interaction timeouts 
        self.click_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['click']
            )
        self.key_press_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['key_press']
            )

    def _update(self):
        if self.state == self.State.INIT:
            self.state = self.State.RESET_MOUSE_STATE
        elif self.state == self.State.RESET_MOUSE_STATE:
            left_up()
            self._wait_then(
                self.click_tr,
                self.State.RESET_FREE_LOOK
            )
        elif self.state == self.State.RESET_FREE_LOOK:
            key_up(self.free_look_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.ESCAPE_START
                )
        # Press escape
        elif self.state == self.State.ESCAPE_START:
            key_down(self.escape_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.ESCAPE_END
                )
        elif self.state == self.State.ESCAPE_END:
            key_up(self.escape_key.get())
            self._wait_then(
                self.escape_tr,
                self.State.INVENTORY_OPEN_START
                )
        # Open inventory
        elif self.state == self.State.INVENTORY_OPEN_START:
            key_down(self.inventory_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.INVENTORY_OPEN_END
                )
        elif self.state == self.State.INVENTORY_OPEN_END:
            key_up(self.inventory_key.get())
            self._wait_then(
                self.inventory_tr,
                self.State.INVENTORY_CLOSE_START
                )
        # Close inventory
        elif self.state == self.State.INVENTORY_CLOSE_START:
            key_down(self.inventory_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.INVENTORY_CLOSE_END
                )
        elif self.state == self.State.INVENTORY_CLOSE_END:
            key_up(self.inventory_key.get())
            self._wait_then(
                self.inventory_tr,
                self.State.TOGGLE_FISHING_START
                )
        # Toggle fishing
        elif self.state == self.State.TOGGLE_FISHING_START:
            key_down(self.toggle_fishing_mode_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.TOGGLE_FISHING_END
                )
        elif self.state == self.State.TOGGLE_FISHING_END:
            key_up(self.toggle_fishing_mode_key.get())
            self._wait_then(
                self.toggle_fishing_mode_tr,
                self.State.COMPLETE
                )

class RepairSequence(BaseSequence):
    NAME = 'REPAIRING'

    class State(BaseSequence.State):
        CHECK_SHOULD_REPAIR = 'CHECK_SHOULD_REPAIR'
        INVENTORY_OPEN_START = 'INVENTORY_OPEN_START'
        INVENTORY_OPEN_END = 'INVENTORY_OPEN_END'
        PRESS_REPAIR_KEY_START = 'PRESS_REPAIR_KEY_START'
        MOVE_MOUSE_TO_REPAIR_START = 'MOVE_MOUSE_TO_REPAIR_START'
        CLICK_REPAIR_START = 'CLICK_REPAIR_START'
        CLICK_REPAIR_END = 'CLICK_REPAIR_END'
        PRESS_REPAIR_KEY_END = 'PRESS_REPAIR_KEY_END'
        CONFIRM_REPAIR_START = 'CONFIRM_REPAIR_START'
        CONFIRM_REPAIR_END = 'CONFIRM_REPAIR_END'
        INVENTORY_CLOSE_START = 'INVENTORY_CLOSE_START'
        INVENTORY_CLOSE_END = 'INVENTORY_CLOSE_END'
        TOGGLE_FISHING_START = 'TOGGLE_FISHING_START'
        TOGGLE_FISHING_END = 'TOGGLE_FISHING_END'

    def __init__(self, vm):
        super().__init__()
        self.vm = vm

        self.toggle_fishing_mode_key = vm['key_bindings']['toggle_fishing_mode']
        self.escape_key = vm['key_bindings']['escape']
        self.inventory_key = vm['key_bindings']['inventory']
        self.free_look_key = vm['key_bindings']['free_look']
        self.repair_key = vm['key_bindings']['repair']

        self.repair_position = Vec2(
            vm['repair']['ui_positions']['fishing_rod']
            )

        # Animation timeout objects
        self.toggle_fishing_mode_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['toggle_fishing_mode']
            )
        self.inventory_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['inventory']
            )
        self.escape_tr = TimeoutRange(
            self.vm['animation']['timeouts']\
                ['escape']
            )
        
        # Interaction timeouts 
        self.click_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['click']
            )
        self.key_press_tr = TimeoutRange(
            self.vm['interaction']['timeouts']\
                ['key_press']
            )

        # Region
        self._region = Region(self.vm['verification']['repair']['region'])

    def _update(self):
        if self.state == self.State.INIT:
            self.state = self.State.CHECK_SHOULD_REPAIR
        elif self.state == self.State.CHECK_SHOULD_REPAIR:
            if scanner.should_repair(self._region.bbox):
                self.state = self.State.INVENTORY_OPEN_START
            else:
                self.state = self.State.COMPLETE
        # Open inventory
        elif self.state == self.State.INVENTORY_OPEN_START:
            key_down(self.inventory_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.INVENTORY_OPEN_END
                )
        elif self.state == self.State.INVENTORY_OPEN_END:
            key_up(self.inventory_key.get())
            self._wait_then(
                self.inventory_tr,
                self.State.PRESS_REPAIR_KEY_START
                )
        # Press repair key
        elif self.state == self.State.PRESS_REPAIR_KEY_START:
            key_down(self.repair_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.MOVE_MOUSE_TO_REPAIR_START
                )
        # Move mouse to fishing rod 
        elif self.state == self.State.MOVE_MOUSE_TO_REPAIR_START:
            move_mouse(
                self.repair_position.x, 
                self.repair_position.y
                )
            self._wait_then(
                self.click_tr,
                self.State.CLICK_REPAIR_START
                )
        # Click on the fishing rod with repair key depressed
        elif self.state == self.State.CLICK_REPAIR_START:
            left_down()
            self._wait_then(
                self.click_tr,
                self.State.CLICK_REPAIR_END
                )
        elif self.state == self.State.CLICK_REPAIR_END:
            left_up()
            self._wait_then(
                self.click_tr,
                self.State.PRESS_REPAIR_KEY_END
                )
        elif self.state == self.State.PRESS_REPAIR_KEY_END:
            key_up(self.repair_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.CONFIRM_REPAIR_START
                )
        # Press confirm key
        elif self.state == self.State.CONFIRM_REPAIR_START:
            key_down('e')
            self._wait_then(
                self.key_press_tr,
                self.State.CONFIRM_REPAIR_END
                )
        elif self.state == self.State.CONFIRM_REPAIR_END:
            key_up('e')
            self._wait_then(
                self.key_press_tr,
                self.State.INVENTORY_CLOSE_START
                )
        # Close inventory
        elif self.state == self.State.INVENTORY_CLOSE_START:
            key_down(self.inventory_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.INVENTORY_CLOSE_END
                )
        elif self.state == self.State.INVENTORY_CLOSE_END:
            key_up(self.inventory_key.get())
            self._wait_then(
                self.inventory_tr,
                self.State.TOGGLE_FISHING_START
                )
        # Toggle fishing
        elif self.state == self.State.TOGGLE_FISHING_START:
            key_down(self.toggle_fishing_mode_key.get())
            self._wait_then(
                self.key_press_tr,
                self.State.TOGGLE_FISHING_END
                )
        elif self.state == self.State.TOGGLE_FISHING_END:
            key_up(self.toggle_fishing_mode_key.get())
            self._wait_then(
                self.toggle_fishing_mode_tr,
                self.State.COMPLETE
                )

class SequenceChain:

    def __init__(self, vm):
        self._chain = [
            RepairSequence(vm),
            VerifyingStartSequence(vm),
            CastingSequence(vm),
            ScanningForFishSequence(vm),
            FishNoticedSequence(vm),
            ReelingSequence(vm),
            FishCaughtSequence(vm),
            ResetSequence(vm)
        ]
        self._index = -1

    @property
    def current(self):
        return None if self._index < 0 else \
            self._chain[self._index]

    def run_error_sequence(self):
        self._chain[-1].reset()
        self._index = len(self._chain) - 1

    def reset(self):
        trace('Resetting sequence')
        self._index = -1
        for s in self._chain: s.reset()

    def is_started(self):
        return self.current is not None

    def start(self):
        self.reset()
        return self.next()
    
    def next(self):
        self._index += 1
        if self._index >= len(self._chain) - 1: 
            return self.start()
        return self.current
        