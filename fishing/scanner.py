import cv2 as cv
from numpy import array
from PIL import ImageGrab
from app_config import WAITING_FOR_FISH_IMAGE_PATH, FISH_NOTICED_IMAGE_PATH,\
    CAN_BE_REELED_IMAGE_PATH
from gui.view_model import config_view_model

NOTHING_IMG = cv.imread(WAITING_FOR_FISH_IMAGE_PATH)
NOTICE_IMG = cv.imread(FISH_NOTICED_IMAGE_PATH)
CAN_BE_REELED_IMG = cv.imread(CAN_BE_REELED_IMAGE_PATH)

COLOR_WAGES = 7
MATCH_THRESHOLD = 0.7

class Scanner:

    def __init__(self, view_model):
        self.view_model = view_model
        self.update_config(view_model)

    def update_config(self, config):
        _left, _top, _width, _height = config['fishing']['left'].get(), config['fishing']['top'].get(), \
            config['fishing']['width'].get(), config['fishing']['height'].get(), 
        self.region = (_left, _top, _left + _width, _top + _height)

        def _c_to_tup(c):
            return (
                c['r'].get(), 
                c['g'].get(), 
                c['b'].get()
            )

        self.reel_color_green = _c_to_tup(config['colors']['green'])
        self.reel_color_orange = _c_to_tup(config['colors']['orange'])
        self.reel_color_red = _c_to_tup(config['colors']['red'])

    def _pixel_match(self, img, matcher):
        lower, upper = (
            [matcher[0] - COLOR_WAGES, matcher[1] - COLOR_WAGES, matcher[2] - COLOR_WAGES],
            [matcher[0] + COLOR_WAGES, matcher[1] + COLOR_WAGES, matcher[2] + COLOR_WAGES]
            )

        color_lower = array(lower)
        color_upper = array(upper)

        mask = cv.inRange(img, color_lower, color_upper)
        return mask.any()

    def check_fish_noticed(self):
        img = array(ImageGrab.grab(bbox = self.region))
        img_cv = cv.cvtColor(img, cv.COLOR_RGB2BGR)

        res = cv.matchTemplate(img_cv, NOTICE_IMG, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(res)
        if max_val >= MATCH_THRESHOLD:
            return True

        res = cv.matchTemplate(img_cv, NOTHING_IMG, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(res)
        if max_val >= MATCH_THRESHOLD:
            return False

        return None

    def get_reeling_state(self):
        img = array(ImageGrab.grab(bbox = self.region))

        if self._pixel_match(img, self.reel_color_green):     
            return 'green'

        if self._pixel_match(img, self.reel_color_orange):        
            return 'orange'

        if self._pixel_match(img, self.reel_color_red):                    
            return 'red'
            
        return 'unknown'

    def can_start_reeling_again(self, threshold=0.75):
        img = array(ImageGrab.grab(bbox = self.region))
        img_cv = cv.cvtColor(img, cv.COLOR_RGB2BGR)

        res = cv.matchTemplate(img_cv, CAN_BE_REELED_IMG, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(res)
        return max_val >= threshold

scanner = Scanner(config_view_model)