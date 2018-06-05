from typing import List

from puffmarker.domain.datapoint import DataPoint
from datetime import datetime, timedelta
import puffmarker.input.import_stream_processor_inputs as spi

from puffmarker.utils.PUFFMARKER_CONSTANTS import *
import pytz
tz = pytz.timezone('US/Central')


def convert_sample(sample):
    return list([float(x.strip()) for x in sample.split(',')])


def line_parser(input):
    ts, sample = input.split(',', 1)
    sample = convert_sample(sample)
    ts = sample[6]
    gt = sample[8]
    start_time = int(float(ts)) / 1000.0
    accel_dp = DataPoint(start_time=datetime.fromtimestamp(start_time, tz),
                         offset='0', sample=[sample[0], -sample[1], sample[2]])
    gyro_dp = DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset='0',
                        sample=[sample[3], -sample[4], sample[5]])

    gt = DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset='0',
                        sample=gt)

    return accel_dp, gyro_dp, gt


def load_data(filename):
    fp = open(filename)
    file_content = fp.read()
    fp.close()

    lines = file_content.splitlines()
    accel = []
    gyro = []
    gt = []

    for i in range(1, len(lines)):
        line = lines[i]
        accel_dp, gyro_dp, gt_dp = line_parser(line)
        accel.append(accel_dp)
        gyro.append(gyro_dp)
        gt.append(gt_dp)

    return accel, gyro, gt

def load_detected_puff_timings(filename):
    return spi.load_data(filename)
