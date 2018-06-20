from typing import List

import numpy as np
from puffmarker.domain.datapoint import DataPoint


def moving_average_convergence_divergence(slow_moving_average_data: List[DataPoint]
                                          , fast_moving_average_data: List[DataPoint]
                                          , THRESHOLD: float, near: int):
    '''
    Generates intersection points of two moving average signals
    :param slow_moving_average_data:
    :param fast_moving_average_data:
    :param THRESHOLD: Cut-off value
    :param near: # of nearest point to ignore
    :return:
    '''
    slow_moving_average = np.array([data.sample for data in slow_moving_average_data])
    fast_moving_average = np.array([data.sample for data in fast_moving_average_data])

    index_list = [0] * len(slow_moving_average)
    cur_index = 0

    for index in range(len(slow_moving_average)):
        diff = slow_moving_average[index] - fast_moving_average[index]
        if diff > THRESHOLD:
            if cur_index == 0:
                index_list[cur_index] = index
                cur_index = cur_index + 1
                index_list[cur_index] = index
            else:
                if index <= index_list[cur_index] + near:
                    index_list[cur_index] = index
                else:
                    cur_index = cur_index + 1
                    index_list[cur_index] = index
                    cur_index = cur_index + 1
                    index_list[cur_index] = index

    intersection_points = []
    if cur_index > 0:
        for index in range(0, cur_index, 2):
            start_index = index_list[index]
            end_index = index_list[index + 1]
            start_time = slow_moving_average_data[start_index].start_time
            end_time = slow_moving_average_data[end_index].start_time
            intersection_points.append(
                DataPoint(start_time=start_time, end_time=end_time, sample=[index_list[index], index_list[index + 1]]))

    return intersection_points


def moving_average_convergence_divergence_new(slow_moving_average_data: List[DataPoint]
                                              , fast_moving_average_data: List[DataPoint],
                                              accel: List[DataPoint]):
    '''
    Generates intersection points of two moving average signals
    :param slow_moving_average_data:
    :param fast_moving_average_data:
    :param THRESHOLD: Cut-off value
    :param near: # of nearest point to ignore
    :return:
    '''
    s = np.array([data.sample for data in slow_moving_average_data])
    f = np.array([data.sample for data in fast_moving_average_data])

    bit_map = [0] * len(s)
    for i in range(len(s)):
        if f[i] > s[i]:
            bit_map[i] = 0
        else:
            bit_map[i] = 1

    for i in range(len(s)):
        if bit_map[i] == 0 and bit_map[max(0, i - 4)] == 1 and bit_map[min(len(s), i + 4)] == 1:
            bit_map[i] = 1

    cur_index = 0
    intersection_points = []

    while cur_index < len(s):
        if bit_map[cur_index] == 1:
            start_index = cur_index
            while cur_index < len(s) and bit_map[cur_index] == 1:
                cur_index = cur_index + 1
            end_index = cur_index - 1

            diff = []
            i = start_index - 1
            while i >= 0 and bit_map[i] == 0:
                diff.append(f[i] - s[i])
                i = i - 1
            i = i + 1
            if len(diff) > 0:
                prev_peak_diff = np.mean(diff)
            else:
                prev_peak_diff = 0
            # prev_peak_dur = (slow_moving_average_data[start_index].start_time - slow_moving_average_data[
            #     i].start_time).total_seconds()
            prev_peak_dur = i

            ay = [accel[i].sample[1] for i in range(i, start_index)]
            prev_ay_mean = np.mean(ay)
            prev_ay_sd = np.std(ay)


            diff = []
            i = end_index + 1
            while i < len(s) and bit_map[i] == 0:
                diff.append(f[i] - s[i])
                i = i + 1
            i = i - 1
            if len(diff) > 0:
                next_peak_diff = np.mean(diff)
            else:
                next_peak_diff = 0
            # next_peak_dur = (slow_moving_average_data[i].start_time - slow_moving_average_data[
            #     end_index].start_time).total_seconds()
            next_peak_dur = i
            ay = [accel[i].sample[1] for i in range(end_index, i)]
            nxt_ay_mean = np.mean(ay)
            nxt_ay_sd = np.std(ay)

            # if prev_peak_dur > 0.45 and next_peak_dur > 0.45 and prev_peak_dur < 4 and next_peak_dur < 4:
            intersection_points.append(DataPoint(start_time=slow_moving_average_data[start_index].start_time,
                                                 end_time=slow_moving_average_data[end_index].start_time,
                                                 sample=[start_index, end_index, prev_peak_dur, next_peak_dur,
                                                         prev_peak_diff, next_peak_diff,
                                                         prev_ay_mean, nxt_ay_mean, prev_ay_sd, nxt_ay_sd]))

        else:
            cur_index = cur_index + 1

    return intersection_points



# def segment_based_on_orientation(roll: List[DataPoint], pitch: List[DataPoint], yaw: List[DataPoint]):


