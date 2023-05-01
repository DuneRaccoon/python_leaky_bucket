from typing import Union
from .constants import TimeUnit

class Rate:
    """
    Rate class to use in conjunction with a bucket

    args:
        :max_capacity: 
            -> maximum number of requests available in bucket, per time period. Same as the bucket limit
        :unit: 
            -> TimeUnit enumerable as defined above

    kwargs:
        :allow_burst: 
            -> If set to false, the rate will be recalculated to the maximum allowed rate as though the bucket were filled
            from initialisation. Otherwise if true, the bucket will be immediately allowed to fill to capacity, and then throttled. 
            Bursts are useful when requests are sporadic, to maximise speed and efficiency while keeping under request limits
    """
    def __init__(self, 
        max_capacity: Union[int, float], 
        unit: TimeUnit,
        allow_burst: bool=True
    ):  
        self.base_max_capacity = max_capacity
        self.max_capacity = max_capacity
        self.unit = unit
        self.time_period = unit.value

        self.allow_burst = allow_burst
        if self.allow_burst == False:
            self.time_period = 1 / (self.max_capacity / self.time_period)
            self.max_capacity = 1

    def __repr__(self):
        return f"{self.base_max_capacity} / {self.unit} ({self.rate} per second)"
    
    @property
    def rate(self):
        return (self.max_capacity / self.time_period)
    