from typing import List

from puffmarker.domain.datapoint import DataPoint
from datetime import datetime, timedelta

from puffmarker.utils.PUFFMARKER_CONSTANTS import *

ax_left_filename = 'left-wrist-accelx.csv'
ay_left_filename = 'left-wrist-accely.csv'
az_left_filename = 'left-wrist-accelz.csv'
gx_left_filename = 'left-wrist-gyrox.csv'
gy_left_filename = 'left-wrist-gyroy.csv'
gz_left_filename = 'left-wrist-gyroz.csv'
ax_right_filename = 'right-wrist-accelx.csv'
ay_right_filename = 'right-wrist-accely.csv'
az_right_filename = 'right-wrist-accelz.csv'
gx_right_filename = 'right-wrist-gyrox.csv'
gy_right_filename = 'right-wrist-gyroy.csv'
gz_right_filename = 'right-wrist-gyroz.csv'

import pytz
tz = pytz.timezone('US/Central')

def convert_sample(sample):
    return list([float(x.strip()) for x in sample.split(',')])


def line_parser_offset(input):
    ts, offset, sample = input.split(',', 2)
    start_time = int(float(ts)) / 1000.0

    sample = convert_sample(sample)
    if len(sample) == 1:
        sample = sample[0]
    return DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset=offset, sample=sample)


def load_data_offset(filename):

    fp = open(filename)
    file_content = fp.read()
    fp.close()

    lines = file_content.splitlines()
    data = list(map(line_parser_offset, lines))

    return data


def line_parser(input):
    ts, sample = input.split(',')
    start_time = int(float(ts)) / 1000.0

    sample = float(sample)
    return DataPoint(start_time=datetime.fromtimestamp(start_time, tz), sample=sample)


def load_data(filename):
    fp = open(filename)
    file_content = fp.read()
    fp.close()

    lines = file_content.splitlines()
    data = list(map(line_parser, lines))

    return data


def get_accelerometer(data_dir, wrist) -> List[DataPoint]:
    if wrist in [LEFT_WRIST]:
        accel_x = load_data(data_dir + ax_left_filename)
        accel_y = load_data(data_dir + ay_left_filename)
        accel_z = load_data(data_dir + az_left_filename)
    else:
        accel_x = load_data(data_dir + ax_right_filename)
        accel_y = load_data(data_dir + ay_right_filename)
        accel_z = load_data(data_dir + az_right_filename)

    accel = []
    for index, val in enumerate(accel_x):
        sample = [accel_x[index].sample, accel_y[index].sample, accel_z[index].sample]
        accel.append(DataPoint(start_time=val.start_time, offset=val.offset, sample=sample))

    return accel


def get_gyroscope(data_dir, wrist) -> List[DataPoint]:
    if wrist in [LEFT_WRIST]:
        gyro_x = load_data(data_dir + gx_left_filename)
        gyro_y = load_data(data_dir + gy_left_filename)
        gyro_z = load_data(data_dir + gz_left_filename)
    else:
        gyro_x = load_data(data_dir + gx_right_filename)
        gyro_y = load_data(data_dir + gy_right_filename)
        gyro_z = load_data(data_dir + gz_right_filename)

    gyro = []
    for index, val in enumerate(gyro_x):
        sample = [gyro_x[index].sample, gyro_y[index].sample, gyro_z[index].sample]
        gyro.append(DataPoint(start_time=val.start_time, offset=val.offset, sample=sample))

    return gyro


# ---- FOR GROUNDTRUTH -----
def get_marked_smoking_puffs_filtered(data_dir, wrist) -> List[DataPoint]:
    if wrist in [LEFT_WRIST]:
        filename = data_dir + 'puff_timestamp_leftwrist.csv'
        label = 1
    else:
        filename = data_dir + 'puff_timestamp_rightwrist.csv'
        label = 2

    fp = open(filename)
    file_content = fp.read()
    fp.close()

    lines = file_content.splitlines()
    puff_timings = []
    for line in lines:
        start_time = int(line) / 1000.0
        tz = pytz.timezone('US/Central')

        puff_timings.append(DataPoint(start_time=datetime.fromtimestamp(start_time, tz), sample=label))

    return puff_timings

ground_truth_file = '/home/nsaleheen/data/csvdataSI_new/ground_truth_allmarked/'
def get_marked_smoking_episodes(data_dir, pid, sid) -> List[DataPoint]:
    smoking_epi = load_data(data_dir + 'episode_start_end.csv')
    # smoking_epi = load_data(ground_truth_file + pid + '_' + sid + '_smoking_epi.csv')

    for epi in smoking_epi:
        tz = pytz.timezone('US/Central')
        epi.end_time = datetime.fromtimestamp(epi.sample/1000.0, tz)
    return smoking_epi


def get_all_marked_smoking_puffs(data_dir, wrist, pid, sid) -> List[DataPoint]:
    if wrist in [LEFT_WRIST]:
        filename = ground_truth_file + pid + '_' + sid + '_smoking_puff_left.csv'
        label = 1
    else:
        filename = ground_truth_file + pid + '_' + sid + '_smoking_puff_right.csv'
        label = 2

    try:
        fp = open(filename)
        file_content = fp.read()
        fp.close()
    except:
        return []

    lines = file_content.splitlines()
    puff_timings = []
    for line in lines:
        start_time = int(line.split(',')[0]) / 1000.0
        puff_timings.append(DataPoint(start_time=datetime.fromtimestamp(start_time), sample=label))

    return puff_timings

