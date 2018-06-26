from typing import List

from puffmarker.domain.datapoint import DataPoint
from datetime import datetime, timedelta
import puffmarker.input.import_stream_processor_inputs as spi

from puffmarker.utils.PUFFMARKER_CONSTANTS import *
import pytz
tz = pytz.timezone('US/Central')


def convert_sample(sample):
    return list([float(x.strip()) for x in sample.split(',')])


def line_parser(input, sd_indx, fd_indx, dd_indx, cd_indx):
    ts, sample = input.split(',', 1)
    sample = convert_sample(sample)
    ts = sample[6]
    # gt = sample[8]
    # gt = sample[8+6] #smoking conf
    # gt = sample[8+9] #eating conf

    start_time = int(float(ts)) / 1000.0
    accel_dp = DataPoint(start_time=datetime.fromtimestamp(start_time, tz),
                         offset='0', sample=[sample[0], -sample[1], sample[2]])
    gyro_dp = DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset='0',
                        sample=[sample[3], -sample[4], sample[5]])

    gt_sd = None
    gt_fd = None
    gt_dd = None
    gt_cd = None

    if sd_indx != -1:
        gt_sd = DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset='0', sample=sample[sd_indx])
    if fd_indx != -1:
        gt_fd = DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset='0', sample=sample[fd_indx])
    if dd_indx != -1:
        gt_dd = DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset='0', sample=sample[dd_indx])
    if cd_indx != -1:
        gt_cd = DataPoint(start_time=datetime.fromtimestamp(start_time, tz), offset='0', sample=sample[cd_indx])

    return accel_dp, gyro_dp, gt_sd, gt_fd, gt_dd, gt_cd

def get_label_index(labels):
    sd_index = -1
    fd_index = -1
    dd_index = -1
    cd_index = -1

    for i, lb in enumerate(labels):
        if lb in [text_sd]:
            sd_index = i
        if lb in [text_fd]:
            fd_index = i
        if lb in [text_dd]:
            dd_index = i
        if lb in [text_cd]:
            cd_index = i

    return sd_index, fd_index, dd_index, cd_index

def load_NU_data(filename):
    fp = open(filename)
    file_content = fp.read()
    fp.close()

    lines = file_content.splitlines()
    accel = []
    gyro = []
    gt_sd = []
    gt_fd = []
    gt_dd = []
    gt_cd = []

    labels = lines[0].split(',')
    labels = labels[1:]
    sd_indx, fd_indx, dd_indx, cd_indx = get_label_index(labels)

    for i in range(1, len(lines)):
        line = lines[i]

        accel_dp, gyro_dp, gt_sd_tmp, gt_fd_tmp, gt_dd_tmp, gt_cd_tmp = line_parser(line, sd_indx, fd_indx, dd_indx, cd_indx)

        accel.append(accel_dp)
        gyro.append(gyro_dp)
        gt_sd.append(gt_sd_tmp)
        gt_fd.append(gt_fd_tmp)
        gt_dd.append(gt_dd_tmp)
        gt_cd.append(gt_cd_tmp)

    return accel, gyro, gt_sd, gt_fd, gt_dd, gt_cd

def load_detected_puff_timings(filename):
    return spi.load_data(filename)

filenames = ['acc_gyr_label_inlab_Eating.csv'
    , 'acc_gyr_label_inlab_Smoking.csv'
    , 'acc_gyr_label_inlab_False.csv']

def import_data(cur_data_dir):
    accel=[]
    gyro=[]
    gt_sd=[]
    gt_fd=[]
    gt_dd=[]
    gt_cd=[]

    for filename in filenames:
        accel_t, gyro_t, gt_sd_t, gt_fd_t, gt_dd_t, gt_cd_t = load_NU_data(cur_data_dir + filename)
        accel.extend(accel_t)
        gyro.extend(gyro_t)
        gt_sd.extend(gt_sd_t)
        gt_fd.extend(gt_fd_t)
        gt_dd.extend(gt_dd_t)
        gt_cd.extend(gt_cd_t)

    return accel, gyro, gt_sd, gt_fd, gt_dd, gt_cd