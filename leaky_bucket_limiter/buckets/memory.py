from typing import Union
from .base import AbstractBaseBucket

class InMemoryBucket(AbstractBaseBucket):
    """
    Memory bucket subclass

    Useful for instances where persistance doesn't matter and all code is executed within a single process
    """

    def __init__(self, *args):
        super(InMemoryBucket, self).__init__(*args)

        self._current_volume = 0
        self._last_time_checked = 0

    @property
    def current_volume(self):
        return self._current_volume
    
    @current_volume.setter
    def current_volume(self, volume: Union[int, float]):
        self._current_volume = volume

    @property
    def last_time_checked(self):
        return self._last_time_checked
    
    @last_time_checked.setter
    def last_time_checked(self, time: float):
        self._last_time_checked = time

    def tear_down(self):
        pass