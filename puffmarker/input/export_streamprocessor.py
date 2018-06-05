from typing import List
from puffmarker.domain.datapoint import DataPoint
import numpy as np

def append_to_file(filename, txt):
    fh = open(filename, 'a')
    fh.write(txt + '\n')
    fh.close()

def export_datastream(filename: str, data: List[DataPoint]):

    for dp in data:
        txt = dp.start_time + ',' + dp.start_time.timestamp() + ',' + dp.sample
        append_to_file(filename, txt)

