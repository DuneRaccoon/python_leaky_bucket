import time
import asyncio
from collections import OrderedDict
from abc import ABC, abstractmethod
from typing import Union
from ..rate import Rate

class AbstractBaseBucket(ABC):

    def __init__(self, 
        bucket_id: str,
        max_capacity: int, 
        drip_rate: Rate,
        **kwargs
    ):
        self.bucket_id = bucket_id
        self.max_capacity = max_capacity
        self.drip_rate = drip_rate

        # self._async_waiters: Dict[asyncio.Task, asyncio.Future] = OrderedDict()

    def __repr__(self):
        return f"<{self.__class__.__name__} - capacity: {self.max_capacity}, rate: {self.drip_rate}>"
    
    def __del__(self):
        try:
            self.tear_down()
        except:
            pass

    @property
    @abstractmethod
    def current_volume(self):
        """
        Current size getter abstract method - should be implemented based on the bucket store type
        """
    
    @current_volume.setter
    @abstractmethod
    def current_volume(self, size: Union[int, float]):
        """
        Current size setter abstract method - should be implemented based on the bucket store type
        """
    
    @property
    @abstractmethod
    def last_time_checked(self):
        """
        Last time checked getter abstract method - should be implemented based on the bucket store type
        """

    @last_time_checked.setter
    @abstractmethod
    def last_time_checked(self, time: float):
        """
        Last time checked setter abstract method - should be implemented based on the bucket store type
        """

    @abstractmethod
    def tear_down(self):
        """
        Drop any outstanding connections or flush any data in subclasses that may require it
        """

    def _drip(self) -> None:
        now = time.time()
        if self.current_volume:
            time_elapsed = (now - self.last_time_checked)
            leaked_amount = time_elapsed * self.drip_rate.rate
            self.current_volume = max(
                self.current_volume - leaked_amount, 0
            )
        self.last_time_checked = now
    
    def is_full(self, task_cost: int = 1, async_: bool=False) -> bool:
        self._drip()
        # if async_ and (self.current_volume + task_cost) < self.drip_rate.max_capacity:
        #     for fut in self._async_waiters.values():
        #         if not fut.done():
        #             fut.set_result(True)
        #             break
        return (self.current_volume + task_cost) > self.drip_rate.max_capacity

    def acquire_space(self, task_cost: int = 1):

        if task_cost > self.drip_rate.max_capacity:
            raise ValueError(f"Cannot drip more than the max rate of {self.drip_rate.max_capacity}")

        while self.is_full(task_cost):
            # print(f"{self} is full against {self.drip_rate}")
            time.sleep((1 / self.drip_rate.rate) * task_cost)
        
        self.current_volume += task_cost
    
    # async def async_acquire_space(self, task_cost: int = 1):
    #     if task_cost > self.drip_rate.max_capacity:
    #         raise ValueError(f"Cannot drip more than the max rate of {self.drip_rate.max_capacity}")

    #     while self.is_full(task_cost):
    #         # await asyncio.sleep((1 / self.drip_rate.rate) * task_cost)
    #         time.sleep((1 / self.drip_rate.rate) * task_cost)
        
    #     self.current_volume += task_cost

    # async def async_acquire_space(self, task_cost: int = 1):
    #     """
    #     :task_cost: assumes each task only takes 1 unit of the buckets total capacity
    #     """

    #     loop = asyncio.get_event_loop()
    #     task = asyncio.current_task(loop)
    #     assert task is not None

    #     if task_cost > self.drip_rate.max_capacity:
    #         raise ValueError(f"Can't emit more than the max rate of {self.drip_rate.max_capacity}")

    #     # while the bucket is full
    #     while self.is_full(task_cost, async_=True):
    #         fut = loop.create_future()
    #         self._async_waiters[task] = fut
    #         try:
    #             # block an asynchronous task from running while the bucket is full
    #             blocking_time = (1 / self.drip_rate.rate) * task_cost
    #             await asyncio.wait_for(
    #                 asyncio.shield(fut), blocking_time, loop=loop
    #             )
    #         except asyncio.TimeoutError:
    #             pass
            
    #         fut.cancel()

    #     self._async_waiters.pop(task, None)
    #     self.current_volume += task_cost

    def __enter__(self) -> None:
        self.acquire_space()

    def __exit__(self, *exc) -> None:
        pass

    async def __aenter__(self) -> None:
        # await self.async_acquire_space()
        await self.acquire_space()
    
    async def __aexit__(self, *exc) -> None:
        pass