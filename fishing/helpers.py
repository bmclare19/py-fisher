from numpy import random
from view_model import register_vm_updates

class _VM:
    _required_keys = []

    def __init__(self, dict_):

        assert isinstance(dict_, dict), \
            "dict_ must be provided and be of type dict"

        assert all([r in dict_ for r in self._required_keys]), \
            "invalid source dict format"

        self._dict = dict_

    def _get(self, key):
        return self._dict[key].get()

# A object that handles the timeout ranges provided in the config
# This class respects the view model and every time it's called grabs
# the most recent value
class TimeoutRange(_VM):
    _required_keys = ['min', 'max']

    def __init__(self, dict_):
        """ Constructs a TimeoutRange object

        dict_ is an item of type dict that has two keys: min & max.
        min and max must point to a tkinter variable of type integer that
        contain a value in miliseconds. The purpose of this is to always have
        the most recent value based on the view model at all times"""
        super().__init__(dict_)

    @property
    def min(self):
        return self._get('min')

    @property
    def max(self):
        return self._get('max')

    @property
    def _mu(self):
        return (self.max + self.min) / 2

    @property
    def _sigma(self):
        """Provides the standard deviation for the random sample call such that 
        the sampled value from the numpy.random call will have a 99.99966% of being
        within the provided range"""
        return (self.max - self.min) / 6

    def clamp(self, val):
        return min(max(val, self.min), self.max)

    def random_timeout_ms(self):
        """Provides a random timeout value in milliseconds using a normal Gaussian 
        distribution but ensuring value is clamped to provided range"""
        sample = random.normal(
            self._mu, 
            self._sigma
            )
        return int(self.clamp(sample))

class Vec2(_VM):
    _required_keys = ['x', 'y']

    def __init__(self, dict_):
        """ Constructs a Vec2 object

        dict_ is an item of type dict that has two keys: x & y.
        x and y must point to a tkinter variable of type integer that
        contain a value in px. The purpose of this is to always have
        the most recent value based on the view model at all times"""
        super().__init__(dict_)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError(
                'Index must be a integer'
                )

        if index == 0: return self.x
        if index == 1: return self.y

        raise IndexError(
            'Index out of range: %d' % index
            )

    @property
    def x(self):
        return self._get('x')

    @property
    def y(self):
        return self._get('y')

class Region(_VM):
    _required_keys = ['left', 'top', 'width', 'height']

    def __init__(self, dict_):
        super().__init__(dict_)

        self._bbox = (
            self.left, 
            self.top, 
            self.left + self.width, 
            self.top + self.height
            )

        register_vm_updates(
            self._update_bbox,
            self._dict['left'], self._dict['top'], self._dict['width'], self._dict['height'] 
            )

    def _update_bbox(self, v):
        try:
            if v.get() != v._previous_value:
                self._bbox = (
                    self.left,
                    self.top,
                    self.left + self.width,
                    self.top + self.height
                )
        except:
            pass

    @property
    def left(self):
        return self._get('left')

    @property
    def top(self):
        return self._get('top')

    @property
    def width(self):
        return self._get('width')

    @property
    def height(self):
        return self._get('height')

    @property
    def bbox(self):
        return self._bbox


class Color(_VM):
    _required_keys = ['r', 'g', 'b']

    def __init__(self, dict_):
        super().__init__(dict_)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError(
                'Index must be a integer'
                )

        if index == 0: return self.r
        if index == 1: return self.g
        if index == 2: return self.b

        raise IndexError(
            'Index out of range: %d' % index
            )
    
    @property
    def r(self):
        return self._get('r')

    @property
    def g(self):
        return self._get('g')

    @property
    def b(self):
        return self._get('b')