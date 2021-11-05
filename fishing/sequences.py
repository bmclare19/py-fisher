from time import time
from fishing.helpers import TimeoutRange
from fishing.scanner import scanner
from wrappers.logging_wrapper import info, trace, error
from wrappers.win32api_wrapper import left_down, left_up, key_up, key_down

class Waiter:

    def __init__(self):
        self.waiting = False
        self.wait_start = None
        self.wait_timeout_ms = None

    def start(self, tr):
        self.waiting = True
        self.wait_start = time()
        self.wait_timeout_ms = tr.random_timeout_ms() \
            if isinstance(tr, TimeoutRange) else tr

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
        COMPLETE = 'COMPLETE'
        ERROR = 'ERROR'

    def __init__(self, start_state=None):
        # state objects
        self._start_state = self._state = start_state if start_state is not None else self.State.INIT
        self._next_state = None

        # waiter object
        self.waiter = Waiter()

        self._sequence_start = None
        self._update_count = 0

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
        if self.state == self.State.ERROR:
            return True
        return self.state_elapsed_ms > 25000

    def reset(self):
        self._state = self._start_state
        self._next_state = None
        self._sequence_start = None
        self._update_count = 0
        self.waiter.reset()
        return self

    def _wait_then(self, tr, next_state):
        self.waiter.start(tr)
        self.state = self.State.WAITING
        self._next_state = next_state

    def _update(self):
        raise NotImplementedError(
            "Implement me bitch"
            )

    def update(self):
        if self.is_first_run:
            trace('%s: %s' % (self.NAME, self.state))

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
    NAME = 'VERIFYING_START'

    class State(BaseSequence.State):
        SCANNING_FOR_START = 'SCANNING_FOR_START'

    def __init__(self, vm):
        super().__init__(self.State.SCANNING_FOR_START)
        self.vm = vm

    def _update(self):
        if self.state == self.State.SCANNING_FOR_START:
            self.state = self.State.COMPLETE

class CastingSequence(BaseSequence):
    NAME = 'CASTING'

    class State(BaseSequence.State):
        CAST_START = 'CAST_START'
        CAST_END = 'CAST_END'

    def __init__(self, vm):
        super().__init__()
        self.vm = vm

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
            key_up(self.vm['key_bindings']['free_look'].get())
            self._wait_then(
                self.free_look_anim_tr,
                self.State.CAST_START
                )
        elif self.state == self.State.CAST_START:
            key_down(self.vm['key_bindings']['free_look'].get())
            left_down()
            self._wait_then(
                self.cast_tr,
                self.State.CAST_END
                )
        elif self.state == self.State.CAST_END:
            left_up()
            self._wait_then(
                self.casting_tr,
                self.State.COMPLETE
                )

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
        self._reset_min = 0.7
        self._reset_max_wait = 4000

    def is_reel_reset(self):
        current_threshold_change = (self._reset_max - self._reset_min) * \
            (self.state_elapsed_ms / self._reset_max_wait)
        threshold = self._reset_max - current_threshold_change
        if threshold < self._reset_min:
            raise RuntimeError(
                'Reel reset exceeded maximum allowable wait time'
                )
        return scanner.can_start_reeling_again(
            threshold=threshold
            )

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

class SequenceChain:

    def __init__(self, vm):
        self._chain = [
            CastingSequence(vm),
            ScanningForFishSequence(vm),
            FishNoticedSequence(vm),
            ReelingSequence(vm),
            FishCaughtSequence(vm)
        ]
        self._index = -1

    @property
    def current(self):
        return None if self._index < 0 else \
            self._chain[self._index]

    def is_started(self):
        return self.current is not None

    def start(self):
        self._index = -1
        for s in self._chain: s.reset()
        return self.next()
    
    def next(self):
        self._index += 1
        if self._index >= len(self._chain): 
            return self.start()
        return self.current
        