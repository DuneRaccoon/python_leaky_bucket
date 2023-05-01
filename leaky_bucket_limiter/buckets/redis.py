import redis
from typing import Union
from .base import AbstractBaseBucket

class RedisBucket(AbstractBaseBucket):
    """
    Redis bucket subclass

    kwargs:
        :redis_host: 
            -> Host name/ip of redis instance
        :redis_port: 
            -> Port redis instance is listening on
        :redis_database: 
            -> Database to connect to (defaults to 0)
        :redis_password: 
            -> Password if applicable
    """
    def __init__(self, 
        *args, 
        redis_host: str=None,
        redis_port: int=None,
        redis_database: int=0,
        redis_password: str = None
    ):
        super(RedisBucket, self).__init__(*args)

        self.connection = redis.from_url(
            f"redis://{f':{redis_password}@' if redis_password else ''}{redis_host}:{redis_port}/{redis_database}"
        )

    @property
    def current_volume(self):
        return float((self.connection.get(f"{self.bucket_id}:volume") or b'0').decode('utf-8'))
    
    @current_volume.setter
    def current_volume(self, volume: Union[int, float]):
        self.connection.set(f"{self.bucket_id}:volume", volume)

    @property
    def last_time_checked(self):
        return float((self.connection.get(f"{self.bucket_id}:last") or b'0').decode('utf-8'))
    
    @last_time_checked.setter
    def last_time_checked(self, time: float):
        self.connection.set(f"{self.bucket_id}:last", float(time))