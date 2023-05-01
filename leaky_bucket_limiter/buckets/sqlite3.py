import os
import redis
import datetime
import sqlalchemy
import sqlite3
import tempfile
from typing import Generator

from typing import Union
from .base import AbstractBaseBucket

TEMP_DIR = tempfile.gettempdir()

CREATE_LIMITER_TABLE = """
    CREATE TABLE IF NOT EXISTS rate_limit (
        bucket VARCHAR(255) PRIMARY KEY,
        current_volume FLOAT,
        max_volume FLOAT,
        last_time_checked DATETIME
    );
"""

SELECT_BUCKET = """
    SELECT * FROM rate_limit
    WHERE bucket = '{bucket}';
"""

INSERT_BUCKET = """
    INSERT INTO rate_limit
    (bucket, current_volume, max_volume, last_time_checked)
    VALUES (?, ?, ?, ?);
"""

UPDATE_BUCKET_VOLUME = """
    UPDATE rate_limit
    SET current_volume = {current_volume}
    WHERE bucket = '{bucket}';
"""

UPDATE_BUCKET_LAST_CHECKED = """
    UPDATE rate_limit
    SET last_time_checked = '{last_time_checked}'
    WHERE bucket = '{bucket}';
"""

class SQLite3Bucket(AbstractBaseBucket):
    """
    SQLite3 bucket subclass

    kwargs:
        :db_path: 
            -> SQLite3 db path, defaults to db named limiter.sqlite, located in the system's temp directory
    """
    def __init__(self, 
        *args, 
        db_path: str = os.path.join(TEMP_DIR, 'limiter.sqlite'),
        **kwargs
    ):
        super(SQLite3Bucket, self).__init__(*args)

        self.db_path = db_path
        self.kwargs_ = kwargs
        self._connection = None

    @property
    def connection(self):
        if not self._connection:
            self._connection = sqlite3.connect(
                str(self.db_path), **self.kwargs_
            )
            self._connection.execute(CREATE_LIMITER_TABLE)
            self._connection.commit()
        return self._connection

    @property
    def current_volume(self) -> float:
        return self.get_bucket()['current_volume']
    
    @current_volume.setter
    def current_volume(self, volume: Union[int, float]):
        self.connection.execute(UPDATE_BUCKET_VOLUME.format(
            current_volume=volume,
            bucket=self.bucket_id
        ))
        self.connection.commit()

    @property
    def last_time_checked(self) -> float:
        return self.get_bucket()['last_time_checked'].timestamp()
    
    @last_time_checked.setter
    def last_time_checked(self, time: float):
        self.connection.execute(UPDATE_BUCKET_LAST_CHECKED.format(
            last_time_checked=datetime.datetime.fromtimestamp(time),
            bucket=self.bucket_id
        ))
        self.connection.commit()

    def tear_down(self):
        if self._connection:
            self.connection.close()
            self._connection = None
        
    def _fetch_as_dict(self, cursor: sqlite3.Cursor):
        line = cursor.fetchone()
        if line:
            return dict(zip(
                [c[0] for c in cursor.description], line
            ))

    def _insert_and_select(self):
        line = (
            self.bucket_id, 0, self.max_capacity, datetime.datetime.now().isoformat()
        )
        self.connection.execute(INSERT_BUCKET, line)
        self.connection.commit()
        return dict(zip(
            ('bucket', 'current_volume', 'max_volume', 'last_time_checked'), line
        ))

    def get_bucket(self):
        c = self.connection.execute(SELECT_BUCKET.format(bucket=self.bucket_id))
        data = self._fetch_as_dict(c) or self._insert_and_select()
        data['last_time_checked'] = datetime.datetime.fromisoformat(data['last_time_checked'])
        return data