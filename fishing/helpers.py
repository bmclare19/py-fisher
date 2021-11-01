from numpy import random

# A object that handles the timeout ranges provided in the config
# This class respects the view model and every time it's called grabs
# the most recent value
class TimeoutRange:
    _required_keys = ['min', 'max']

    def __init__(self, dict_):
        """ Constructs a TimeoutRange object

        dict_ is an item of type dict that has two keys: min & max.
        min and max must point to a tkinter variable of type integer that
        contain a value in miliseconds. The purpose of this is to always have
        the most recent value based on the view model at all times"""

        assert isinstance(dict_, dict), \
            "dict_ must be provided and be of type dict"

        assert all([k in dict_ for k in self._required_keys]), \
            "invalid source dict format"

        self._dict = dict_

    @property
    def min(self):
        return self._dict['min'].get()

    @property
    def max(self):
        return self._dict['min'].get()

    @property
    def mu(self):
        return (self.max + self.min) / 2

    @property
    def sigma(self):
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
            self.mu, 
            self.sigma
            )
        return int(self.clamp(sample))

    # Provides a random timeout in seconds
    def random_timeout(self):
        timeout_ms = self.random_timeout_ms()
        return int(timeout_ms / 1000)

class Vec2:
    _required_keys = ['x', 'y']

    def __init__(self, dict_):
        """ Constructs a Vec2 object

        dict_ is an item of type dict that has two keys: x & y.
        x and y must point to a tkinter variable of type integer that
        contain a value in px. The purpose of this is to always have
        the most recent value based on the view model at all times"""

        assert isinstance(dict_, dict), \
            "dict_ must be provided and be of type dict"

        assert all([k in dict_ for k in ["x", "y"]]), \
            "invalid source dict format"
        
        self._dict = dict_

    @property
    def x(self):
        return self._dict['x'].get()

    @property
    def y(self):
        return self._dict['y'].get()