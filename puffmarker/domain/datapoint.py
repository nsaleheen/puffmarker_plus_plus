from datetime import datetime, timedelta
from typing import Any

class DataPoint:
    def __init__(self,
                 start_time: datetime = None,
                 end_time: datetime = None,
                 offset: str=None,
                 sample: Any = None):
        self._start_time = start_time
        self._end_time = end_time
        self._offset = offset
        self._sample = sample

    @property
    def sample(self):
        return self._sample

    @sample.setter
    def sample(self, val):
        self._sample = val

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, val):
        self._start_time = val

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, val):
        self._end_time = val

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, val):
        self._offset = val

    @classmethod
    def from_tuple(cls, start_time: datetime, sample: Any, end_time: datetime = None, offset: str=None):
        return cls(start_time=start_time, end_time=end_time, offset=offset, sample=sample)

    def __str__(self):
        return str(self.start_time) + " - " + str(self.sample)

    def __repr__(self):
        return 'DataPoint(' + ', '.join(map(str, [self.start_time, self.offset, self.sample]))
