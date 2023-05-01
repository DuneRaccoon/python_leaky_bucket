from enum import Enum

class TimeUnit(Enum):
    SECOND = 1
    MINUTE = SECOND * 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
    WEEK = DAY * 7
    MONTH = (WEEK * 52) // 12