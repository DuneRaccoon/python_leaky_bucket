import functools
from inspect import iscoroutinefunction
from typing import List, Iterable
from .rate import Rate
from .buckets import AbstractBaseBucket, InMemoryBucket

class RateLimiter(object):
    """
    Rate limiter class that takes 1 or more rate limits
    """
    def __init__(self,
        identifier: str,
        *rates,
        bucket_class: AbstractBaseBucket=InMemoryBucket,
        bucket_kwargs: dict = {},
        **kwargs
    ):
        self.identifier = identifier
        self.bucket_class = bucket_class
        self.bucket_kwargs = bucket_kwargs
        self.buckets: List[AbstractBaseBucket] = []

        for index, rate in enumerate(self._sort_rates(rates)):
            self.buckets.append(self.bucket_class(
                f"{self.identifier}:{index}",
                rate.max_capacity,
                rate,
                **self.bucket_kwargs
            ))

    def __repr__(self):
        buckets = "\n\t".join([str(b) for b in self.buckets])
        return f"<RateLimiter - {self.identifier}: \n\t{buckets}\n>"

    def __call__(self, f):
        if iscoroutinefunction(f):
            @functools.wraps(f)
            async def wrapper(*args, **kwargs):
                self._do_acquire()
                return await f(*args, **kwargs)
        else:
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                self._do_acquire()
                return f(*args, **kwargs)
            
        return wrapper
        
    def _do_acquire(self):
        for bucket in self.buckets:
            bucket.acquire_space()

    # async def _async_do_acquire(self):
    #     for bucket in self.buckets:
    #         await bucket.async_acquire_space()

    @staticmethod
    def _sort_rates(rates: Iterable[Rate]):
        return sorted(rates, key=lambda x: (x.unit.value, x.max_capacity))
    
    def __enter__(self) -> None:
        self._do_acquire()

    def __exit__(self, *exc) -> None:
        pass

    async def __aenter__(self) -> None:
        # await self._async_do_acquire()
        self._do_acquire()
    
    async def __aexit__(self, *exc) -> None:
        pass