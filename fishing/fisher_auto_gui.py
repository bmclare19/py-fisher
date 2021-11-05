from time import sleep
from fishing.helpers import TimeoutRange, Vec2
from wrappers.win32api_wrapper import left_click, key_up, key_down, press_key, click_mouse_with_coordinates
from wrappers.logging_wrapper import trace

CAST_ANIMATION_WAIT_MS = 2000
FREE_LOOK_END_WAIT_MS = 1700
EQUIP_BAIT_ANIMATION_WAIT_MS = 1000

class FisherAutoGui:

    def __init__(self, config):

        # Keybindings 
        self.toggle_fishing_mode_key = config['key_bindings']['toggle_fishing_mode'].get()
        self.equip_bait_key = config['key_bindings']['equip_bait'].get()
        self.inventory_key = config['key_bindings']['inventory'].get()
        self.free_look_key = config['key_bindings']['free_look'].get()

        self.repair_key = 'r' if config['repair']['use_repair_kit'].get() else 't'
        self.repair_position = Vec2(
            config['repair']['ui_positions']['fishing_rod'],
            )
        self.bait_position = Vec2(
            config['bait']['ui_positions']['select']
            )
        self.equip_bait_button_position = Vec2(
            config['bait']['ui_positions']['equip']
            )

        # Timeouts 
        self.arm_disarm_timeout = TimeoutRange(config['repair']['timeouts']['arm_disarm'])
        self.inventory_timeout = TimeoutRange(config['repair']['timeouts']['inventory'])
        self.repair_timeout = TimeoutRange(config['repair']['timeouts']['repair'])
        self.confirm_repair_timeout = TimeoutRange(config['repair']['timeouts']['confirm'])
        self.bait_select_timeout = TimeoutRange(config['bait']['timeouts']['select'])
        self.bait_confirm_timeout = TimeoutRange(config['bait']['timeouts']['equip'])
        self.cast_timeout = TimeoutRange(config['fishing']['timeouts']['cast'])
        self.fish_noticed_timeout = TimeoutRange(config['fishing']['timeouts']['noticed'])
        self.reel_timeout = TimeoutRange(config['fishing']['timeouts']['reeling'])
        self.move_around_timeout = TimeoutRange(config['afk_prevention']['timeouts']['move'])

    def _delay_ms(self, timeout_ms):
        sleep(timeout_ms / 1000)

    def begin_free_look(self):
        key_down(self.free_look_key)
        self._delay_ms(10)

    def end_free_look(self):
        key_up(self.free_look_key)
        self._delay_ms(FREE_LOOK_END_WAIT_MS)

    def _press_toggle_fishing_mode_key(self):
        trace("Pressing fishing key")
        timeout_ms = self.arm_disarm_timeout.random_timeout_ms()
        self._delay_ms(timeout_ms)
        press_key(self.toggle_fishing_mode_key)
        self._delay_ms(timeout_ms)

    def _press_inventory_key(self):
        trace("Pressing inventory key")
        timeout_ms = self.inventory_timeout.random_timeout_ms()
        self._delay_ms(timeout_ms)
        press_key(self.inventory_key)
        self._delay_ms(timeout_ms)

    def _repair(self):
        trace("Repairing fishing rod")
        timeout_ms = self.repair_timeout.random_timeout_ms()
        self._delay_ms(timeout_ms)

        trace("Repairing with key: {}".format(self.repair_key))
        key_down(self.repair_key)
        self._delay_ms(100)

        click_mouse_with_coordinates(
            self.repair_position.x,
            self.repair_position.y
            )
        self._delay_ms(100)

        key_up(self.repair_key)
        self._delay_ms(timeout_ms)

    def _confirm_repair(self):
        trace("Confirming repair")
        timeout_ms = self.confirm_repair_timeout.random_timeout_ms()
        self._delay_ms(timeout_ms)
        press_key('e')
        self._delay_ms(timeout_ms)

    def run_repair_sequence(self):
        trace("Running repair sequence")

        self.end_free_look()

        self._press_toggle_fishing_mode_key()
        self._press_inventory_key()
        self._repair()
        self._confirm_repair()
        self._press_inventory_key()
        self._press_toggle_fishing_mode_key()

    def run_fish_caught_sequence(self):
        trace("Running fish caught sequence...")
        self._delay_ms(1500)
        left_click()
        self._delay_ms(2000)

    def run_fish_noticed_sequence(self):
        trace("Running fish noticed sequence...")
        timeout_ms = self.fish_noticed_timeout.random_timeout_ms()
        left_click(timeout_ms)

    def run_reel_fish_sequence(self):
        trace("Running reel fish sequence...")
        timeout_ms = self.reel_timeout.random_timeout_ms()
        left_click(timeout_ms)

    def run_cast_sequence(self):
        trace("Running cast sequence...")

        # end free look which waits FREE_LOOK_END_WAIT_MS to reset camera
        self.end_free_look()

        # once camera is reset immediateley free look again
        self.begin_free_look()

        left_click(self.cast_timeout.random_timeout_ms())
        self._delay_ms(100)

        trace("Waiting %s ms for cast animation" % CAST_ANIMATION_WAIT_MS)
        self._delay_ms(CAST_ANIMATION_WAIT_MS)

    def run_afk_prevention_sequence(self):
        trace("Running afk prevention sequence")
        timeout_ms = self.move_around_timeout.random_timeout_ms()
        press_key('a')
        self._delay_ms(timeout_ms)
        press_key('d')

    def _press_on_bait(self):
        trace("Clicking on bait")
        timeout_ms = self.bait_select_timeout.random_timeout_ms()
        self._delay_ms(timeout_ms)
        click_mouse_with_coordinates(
            self.bait_position.x,
            self.bait_position.y
            )
        self._delay_ms(timeout_ms)

    def _press_equip_bait(self):
        trace("Clicking equip bait button")
        timeout_ms = self.bait_confirm_timeout.random_timeout_ms()
        self._delay_ms(timeout_ms)
        click_mouse_with_coordinates(
            self.equip_bait_button_position.x,
            self.equip_bait_button_position.y
            )
        self._delay_ms(timeout_ms)

        # waiting for animation to finish
        self._delay_ms(EQUIP_BAIT_ANIMATION_WAIT_MS)

    def run_select_bait_sequence(self):
        trace("Running select bait sequence")
        self.end_free_look()

        press_key(self.equip_bait_key)
        self._press_on_bait()
        self._press_equip_bait()

    def run_reset_ui_sequence(self):
        trace("Running reset UI sequence")
        press_key('esc')
        self._press_inventory_key()
        self._press_inventory_key()
        self._press_toggle_fishing_mode_key()