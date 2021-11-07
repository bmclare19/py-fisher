import cv2
import numpy as np
from PIL import ImageGrab
from app_config import FISH_IDLE_IMG_PATH, WAITING_FOR_FISH_IMAGE_PATH, FISH_NOTICED_IMAGE_PATH,\
    CAN_BE_REELED_IMAGE_PATH
from view_model import config_view_model, register_vm_updates, unregister_vm_updates
from fishing.helpers import Color, Region
from wrappers.logging_wrapper import info, trace

WAITING_FOR_FISH_IMG = cv2.imread(WAITING_FOR_FISH_IMAGE_PATH)
NOTICE_IMG = cv2.imread(FISH_NOTICED_IMAGE_PATH)
CAN_BE_REELED_IMG = cv2.imread(CAN_BE_REELED_IMAGE_PATH)
FISHING_IDLE_IMG = cv2.imread(FISH_IDLE_IMG_PATH)
FISHING_IDLE_IMG = cv2.cvtColor(FISHING_IDLE_IMG, cv2.COLOR_BGR2GRAY)

COLOR_WAGES = 7
MATCH_THRESHOLD = 0.75

class Scanner:

    def __init__(self, vm):
        self.vm = vm

        self.region = Region(vm['fishing'])
        self.reel_green = Color(vm['colors']['green'])
        self.reel_orange = Color(vm['colors']['orange'])
        self.reel_red = Color(vm['colors']['red'])

    def _get_screen_region(self, bbox=None):
        bbox = bbox if bbox is not None else self.region.bbox
        return np.array(
            ImageGrab.grab(bbox=bbox)
            )

    def _pixel_match(self, img, matcher):
        lower, upper = (
            [matcher[0] - COLOR_WAGES, matcher[1] - COLOR_WAGES, matcher[2] - COLOR_WAGES],
            [matcher[0] + COLOR_WAGES, matcher[1] + COLOR_WAGES, matcher[2] + COLOR_WAGES]
            )

        color_lower = np.array(lower)
        color_upper = np.array(upper)

        mask = cv2.inRange(img, color_lower, color_upper)
        return mask.any()

    def check_fishing_ready(self, bbox=None):
        """Checks if fishing is ready by looking for the fishing
        menu that appears when you enter fishing mode.

        Because the region examined doesn't have the same background
        every time we use a modified edge map and check that against
        a lower threshold to sample for the menu."""
        img = self._get_screen_region(bbox)
        edged = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        v = np.median(edged)

        lower = int(max(0, (1.0 - 0.33) * v))
        upper = int(min(255, (1.0 + 0.33) * v))

        edged = cv2.Canny(edged, lower, upper, L2gradient=True)

        res = cv2.matchTemplate(edged, FISHING_IDLE_IMG, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        trace(max_val)
        # match threshold is lower for this because we use an edge map and
        return max_val >= 0.5

    def check_waiting_for_fish(self):
        img = self._get_screen_region()
        img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        res = cv2.matchTemplate(img_cv, WAITING_FOR_FISH_IMG, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return max_val >= MATCH_THRESHOLD

    def check_fish_noticed(self):
        img = self._get_screen_region()
        img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        res = cv2.matchTemplate(img_cv, NOTICE_IMG, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val >= MATCH_THRESHOLD:
            return True

        res = cv2.matchTemplate(img_cv, WAITING_FOR_FISH_IMG, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val >= MATCH_THRESHOLD:
            return False

        return None

    def get_reeling_state(self):
        img = self._get_screen_region()

        if self._pixel_match(img, self.reel_green):     
            return 'green'

        if self._pixel_match(img, self.reel_orange):        
            return 'orange'

        if self._pixel_match(img, self.reel_red):                    
            return 'red'
            
        return 'unknown'

    def can_start_reeling_again(self, threshold=0.75):
        img = self._get_screen_region()
        img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        res = cv2.matchTemplate(img_cv, CAN_BE_REELED_IMG, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return max_val >= threshold

    def should_repair(self, bbox):
        img = self._get_screen_region(bbox)
        img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        lower = np.array([245, 245, 245])
        upper = np.array([255, 255, 255])
        mask = cv2.inRange(img_cv, lower, upper)

        coord = cv2.findNonZero(mask)
        if len(coord) < 2:
            return True

        min_, max_ = coord[0][0], coord[-1][0]
        x_diff = max_[0] - min_[0]
        durability = x_diff / 176
        info('Estimated durability: %f' % durability)
        return x_diff <= 5

scanner = Scanner(config_view_model)