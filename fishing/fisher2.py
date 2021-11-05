from fishing.sequences import SequenceChain
from gui import root, worker_pool
from wrappers.logging_wrapper import info, trace

class Fisher2:

    def __init__(self, view_model):
        self.view_model = view_model
        self.update_interval = 10
        self.continue_fishing = False
        self.sequence = SequenceChain(self.view_model)

    def _reset(self):
        pass

    def _update(self):
        if not self.continue_fishing:
            info("Stopped fishing.")
            self.state = Fisher2.State.NONE
            return

        if not self.sequence.is_started():
            info("Started fishing!")
            self.sequence.start()

        if self.sequence.current.update():
            self.sequence.next()
            
        # check if the program has been in the same state for the last 25 seconds; if so there is 
        # likely an error and everything needs to be reset
        if self.sequence.current.is_error():
            info("A problem was detected. Resetting UI and fisher state")
            self._reset()

        root.after(
            self.update_interval,
            self.update
            )

    def update(self):
        worker_pool.submit(self._update)
