from time import time
from gui import root, worker_pool
from fishing.fisher_auto_gui import FisherAutoGui
from fishing.results import ResultSet
from fishing.scanner import Scanner
from wrappers.logging_wrapper import info, trace

class FisherState:
    NONE = 'NONE'
    IDLE = 'IDLE'
    WAITING_FOR_FISH = 'WAITING_FOR_FISH'
    REELING = 'REELING'
    PAUSE_REELING = 'PAUSE_REELING'
    REELING_NO_MATCH = 'REELING_NO_MATCH'

class Fisher:

    def __init__(self, config):
        self.update_interval = 10
        self.state = FisherState.NONE
        self.continue_fishing = False
        self.repair_enabled = config['repair']['enabled'].get()
        self.repair_interval_seconds = config['repair']['interval'].get()
        self.last_repair_time = int(time())
        self.bait_enabled = config['bait']['enabled'].get()
        self.afk_prevention_enabled = config['afk_prevention']['enabled'].get()
        self.results = ResultSet()
        self.scanner = Scanner(config)
        self.auto_gui = FisherAutoGui(config)

    def _reset(self):
        self.auto_gui.run_reset_ui_sequence()
        self.results.clear()
        self.state = FisherState.IDLE

    def _update(self):
        if not self.continue_fishing:
            info("Stopped fishing.")
            self.state = FisherState.NONE
            return

        # if NONE then wait for a few seconds so the user can tab back over to the game
        # then set state to IDLE so the program can begin
        if self.state == FisherState.NONE:
            info("Started fishing!")
            self.update_interval = 10
            self.results.clear()
            self.state = FisherState.IDLE
        # if IDLE then cast and set state to WAITING_FOR_FISH
        elif self.state == FisherState.IDLE:
            if self.repair_enabled:
                should_repair_in = -1 * (int(time()) - self.last_repair_time - self.repair_interval_seconds)
                if should_repair_in < 0:
                    self.last_repair_time = int(time())
                    info("Repairing")
                    self.auto_gui.run_repair_sequence()
                    if self.afk_prevention_enabled:
                        info("Preventing AFK detection")
                        self.auto_gui.run_afk_prevention_sequence()
                    if self.bait_enabled:
                        info("Selecting bait")
                        self.auto_gui.run_select_bait_sequence()
            info("Casting fishing rod...")
            self.auto_gui.run_cast_sequence()
            self.state = FisherState.WAITING_FOR_FISH
            self.update_interval = 100
        # if WAITING_FOR_FISH then wait until match is found then set state to REELING
        elif self.state == FisherState.WAITING_FOR_FISH:
            fish_noticed_result = self.scanner.check_fish_noticed()
            if fish_noticed_result == True:
                info("Fish noticed!")
                self.auto_gui.run_fish_noticed_sequence()
                self.state = FisherState.REELING
                self.update_interval = 10
                info("Reeling...")
        # if REELING then check sub state and act accordingly until no sub state is found then set to IDLE
        elif self.state == FisherState.REELING:
            reeling_state = self.scanner.get_reeling_state()
            if reeling_state == 'green':
                info("Reeling in fish")
                self.auto_gui.run_reel_fish_sequence()
            elif reeling_state == 'orange' or reeling_state == 'red':
                info("Pausing reeling to avoid line break")
                self.state = FisherState.PAUSE_REELING
            elif reeling_state is None:
                info("Waiting for updated reeling state")
                self.state = FisherState.REELING_NO_MATCH
        # if PAUSE_REELING then check if the fishing icon is at its minimum again and if so reel the fish 
        # and set state to REELING again
        elif self.state == FisherState.PAUSE_REELING:
            if self.scanner.can_start_reeling_again():
                info("Starting to reel again...")
                self.auto_gui.run_reel_fish_sequence()
                self.state = FisherState.REELING
        # special handling for the REELING_NO_MATCH case which can either indicate that the color 
        # was in a transition state OR the fish has been caught. duration is set really low because
        # the transition color should not take up more than 1-5 frames or 10-50 ms 
        elif self.state == FisherState.REELING_NO_MATCH:
            if self.results.get_sequence_duration() > 1.5:
                info("Fish caught!")
                self.auto_gui.run_fish_caught_sequence()
                self.state = FisherState.IDLE
                self.results.clear()
            else:
                reeling_state = self.scanner.get_reeling_state()
                if reeling_state is not None:
                    info("Reeling state recognized, resuming reeling")
                    self.state = FisherState.REELING

        self.results.add(self.state)

        # check if the program has been in the same state for the last 25 seconds; if so there is 
        # likely an error and everything needs to be reset
        if self.results.get_sequence_duration() > 25:
            info("A problem was detected. Resetting UI and fisher state")
            self._reset()

        root.after(
            self.update_interval,
            self.update
            )

    def update(self):
        worker_pool.submit(self._update)
