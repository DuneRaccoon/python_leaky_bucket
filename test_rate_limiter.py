#!/usr/bin/env python

import datetime
import unittest
from unittest.mock import Mock

from leaky_bucket_limiter import (
    Rate,
    TimeUnit,
    RateLimiter,
    InMemoryBucket
)

class TestRateLimiter(unittest.TestCase):
    """Tests for normal contexts in RateLimiter class."""

    def setUp(self):

        self.base_rate = Rate(5, TimeUnit.SECOND, allow_burst=False)
        self.base_rate_with_burst = Rate(5, TimeUnit.SECOND, allow_burst=True)

        self.limiters = {
            'no_burst': RateLimiter("test_limiter",
                self.base_rate,
                bucket_class=InMemoryBucket
            ),
            'with_burst': RateLimiter("test_limiter",
                self.base_rate_with_burst,
                bucket_class=InMemoryBucket
            )
        }

    def tearDown(self):
        for limiter in self.limiters.values():
            for bucket in limiter.buckets:
                del bucket

    @staticmethod
    def get_min_time(num_tasks: int, rate: Rate) -> float:
        if rate.allow_burst:
            num_tasks -= rate.rate

        if num_tasks <= 0:
            return 0
        
        min_elapsed_time = (num_tasks / rate.rate) - (1/(rate.rate))

        return min_elapsed_time
    
    def test_000_something(self):
        """Test something."""

    def test_limiter_no_burst(self):
        import time

        # mock = Mock()
        # def mock_request():

        # def mock_case(n_requests: int = 10):
        #     with limiter:

        # simulate a task
        def do_thing():
            with self.limiters['no_burst']:
                t = datetime.datetime.now()
                return t
        
        num_tasks = 10
        responses = []
        start = time.time()
        for _ in range(num_tasks):
            responses.append(do_thing())

        time_taken = time.time() - start

        self.assertEqual(len(responses), num_tasks)
        self.assertGreaterEqual(time_taken, self.get_min_time(num_tasks, self.base_rate))

    def test_limiter_with_burst(self):
        import time

        def do_thing():
            with self.limiters['with_burst']:
                t = datetime.datetime.now()
                return t
        
        num_tasks = 10
        responses = []
        start = time.time()
        for _ in range(num_tasks):
            responses.append(do_thing())

        time_taken = time.time() - start

        self.assertEqual(len(responses), num_tasks)
        self.assertGreaterEqual(time_taken, self.get_min_time(num_tasks, self.base_rate_with_burst))

class TestAsyncRateLimiter(unittest.IsolatedAsyncioTestCase):
    """Tests for async contexts in RateLimiter class."""

    # def setUp(self):
    #     self.limiter = RateLimiter("test_limiter",
    #         Rate(30, TimeUnit.MINUTE, allow_burst=False),
    #         Rate(5, TimeUnit.SECOND),
    #         bucket_class=InMemoryBucket
    #     )

    def setUp(self):
        self.base_rate = Rate(5, TimeUnit.SECOND, allow_burst=False)
        self.base_rate_with_burst = Rate(5, TimeUnit.SECOND, allow_burst=True)

        self.limiters = {
            'no_burst': RateLimiter("test_limiter",
                self.base_rate,
                bucket_class=InMemoryBucket
            ),
            'with_burst': RateLimiter("test_limiter",
                self.base_rate_with_burst,
                bucket_class=InMemoryBucket
            )
        }

    def tearDown(self):
        for limiter in self.limiters.values():
            for bucket in limiter.buckets:
                del bucket

    @staticmethod
    def get_min_time(num_tasks: int, rate: Rate) -> float:
        if rate.allow_burst:
            num_tasks -= rate.rate

        if num_tasks <= 0:
            return 0
        
        min_elapsed_time = (num_tasks / rate.rate) - (1/(rate.rate))

        return min_elapsed_time

    def test_000_something(self):
        """Test something."""

    async def test_limiter_no_burst(self):
        import time, asyncio

        # simulate a task
        async def do_thing():
            async with self.limiters['no_burst']:
                t = datetime.datetime.now()
                return t
        
        num_tasks = 10
        async def do_tasks(num_tasks: int = 10):
            start = time.time()
            responses = await asyncio.gather(*[
                do_thing() for _ in range(num_tasks)
            ])
            return responses, time.time() - start

        responses, time_taken = await do_tasks(num_tasks=num_tasks)

        self.assertEqual(len(responses), num_tasks)
        self.assertGreaterEqual(time_taken, self.get_min_time(num_tasks, self.base_rate))

    async def test_limiter_with_burst(self):
        import time, asyncio

        # simulate a task
        async def do_thing():
            async with self.limiters['with_burst']:
                t = datetime.datetime.now()
                return t
        
        num_tasks = 10
        async def do_tasks(num_tasks: int = 10):
            start = time.time()
            responses = await asyncio.gather(*[
                do_thing() for _ in range(num_tasks)
            ])
            return responses, time.time() - start

        responses, time_taken = await do_tasks(num_tasks=num_tasks)

        self.assertEqual(len(responses), num_tasks)
        self.assertGreaterEqual(time_taken, self.get_min_time(num_tasks, self.base_rate_with_burst))
        
if __name__ == '__main__':
    unittest.main()