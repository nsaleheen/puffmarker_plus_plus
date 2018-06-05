# Copyright (c) 2018, MD2K Center of Excellence
# - Nazir Saleheen <nazir.saleheen@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from typing import List

import numpy as np

from puffmarker.domain.datapoint import DataPoint
from puffmarker.utils.PUFFMARKER_CONSTANTS import *


def filter_with_duration(gyr_intersections: List[DataPoint]):
    '''
    Filters hand-to-mouth gesture candidates based on duration

    :param gyr_intersections: contains all the interval of hand-to-mouth gestures
    :return:
    '''
    gyr_intersections_filtered = []

    for I in gyr_intersections:
        dur = (I.end_time - I.start_time).total_seconds()
        if (dur >= 1.0) & (dur <= 5.0):
            gyr_intersections_filtered.append(I)

    return gyr_intersections_filtered


def filter_with_accleY(gyr_intersections: List[DataPoint],
                       accle: List[DataPoint],
                       accel_mag: List[DataPoint]):
    '''
    Filters hand-to-mouth gesture candidates based on roll and pitch
    :param gyr_intersections: contains all the interval of hand-to-mouth gestures
    :param accle_y:
    :return:
    '''
    gyr_intersections_filtered = []

    for I in gyr_intersections:
        start_index = I.sample[0]
        end_index = I.sample[1]

        temp_ay = [accle[i].sample[1] for i in range(start_index, end_index) if
                   (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]

        mean_ay = np.mean(temp_ay)
        median_ay = np.median(temp_ay)

        if (mean_ay > 0.5) & (median_ay > 0.5):
            gyr_intersections_filtered.append(I)

    return gyr_intersections_filtered


def filter_with_accleY_interval(gyr_intersections: List[DataPoint],
                                accle: List[DataPoint],
                                accel_mag: List[DataPoint],
                                p90):
    '''
    Filters hand-to-mouth gesture candidates based on roll and pitch
    :param gyr_intersections: contains all the interval of hand-to-mouth gestures
    :param accle_y:
    :return:
    '''
    gyr_intersections_filtered = []

    for I in gyr_intersections:
        start_index = I.sample[0]
        end_index = I.sample[1]

        temp_ay = [accle[i].sample[1] for i in range(start_index, end_index) if
                   accle[i].sample[1] >= p90]

        if len(temp_ay) >= ((end_index - start_index) * 0.60):
            gyr_intersections_filtered.append(I)

    return gyr_intersections_filtered


def filter_with_roll_pitch(gyr_intersections: List[DataPoint],
                           roll_list: List[DataPoint],
                           pitch_list: List[DataPoint],
                           yaw_list: List[DataPoint]):
    '''
    Filters hand-to-mouth gesture candidates based on roll and pitch
    :param gyr_intersections: contains all the interval of hand-to-mouth gestures
    :param roll_list:
    :param pitch_list:
    :return:
    '''
    gyr_intersections_filtered = []

    for I in gyr_intersections:
        start_index = I.sample[0]
        end_index = I.sample[1]

        temp_roll = [roll_list[i].sample for i in range(start_index, end_index)]
        temp_pitch = [pitch_list[i].sample for i in range(start_index, end_index)]

        mean_roll = np.mean(temp_roll)
        mean_pitch = np.mean(temp_pitch)

        if (mean_roll > MIN_ROLL) & (mean_roll <= MAX_ROLL) & (mean_pitch >= MIN_PITCH) & (mean_pitch <= MAX_PITCH):
            gyr_intersections_filtered.append(I)

    return gyr_intersections_filtered


def filter_with_complementary_roll_pitch(gyr_intersections: List[DataPoint],
                                         roll_list: List[DataPoint],
                                         pitch_list: List[DataPoint],
                                         yaw_list: List[DataPoint],
                                         accel_mag: List[DataPoint]):
    '''
    Filters hand-to-mouth gesture candidates based on roll and pitch
    :param gyr_intersections: contains all the interval of hand-to-mouth gestures
    :param roll_list:
    :param pitch_list:
    :return:
    '''
    gyr_intersections_filtered = []

    for I in gyr_intersections:
        start_index = I.sample[0]
        end_index = I.sample[1]

        temp_roll = [roll_list[i].sample for i in range(start_index, end_index) if
                     (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]
        temp_yaw = [yaw_list[i].sample for i in range(start_index, end_index) if
                    (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]

        mean_roll = np.mean(temp_roll)
        mean_yaw = np.mean(temp_yaw)

        if (mean_roll > -20) & (mean_roll <= 45) & (mean_yaw >= 22) & (mean_yaw <= 110):
            gyr_intersections_filtered.append(I)

    return gyr_intersections_filtered
