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

from puffmarker.utils.hand_orientation import calculate_roll_pitch_yaw, complementary_filter
from puffmarker.utils.timeseries_segmentation import moving_average_convergence_divergence, moving_average_convergence_divergence_new
from puffmarker.utils.wrist_candidate_filter import *
from puffmarker.utils.vector import *


def compute_basic_statistical_features(data):
    mean = np.mean(data)
    median = np.median(data)
    sd = np.std(data)
    quartile = np.percentile(data, 75) - np.percentile(data, 25)

    return mean, median, sd, quartile


def compute_candidate_features(gyr_intersections, gyr_mag, roll_list, pitch_list, yaw_list, accel_mag, accel):
    '''
    Computes feature vector for single hand-to-mouth gesture. Mainly statistical features of hand orientation
    :param gyr_intersections:
    :param gyr_mag_stream:
    :param roll_list:
    :param pitch_list:
    :param yaw_list:
    :return:
    '''
    all_features = []
    offset = gyr_mag[0].offset

    for I in gyr_intersections:
        start_time = I.start_time
        end_time = I.end_time
        start_index = I.sample[0]
        end_index = I.sample[1]

        temp_roll = [roll_list[i].sample for i in range(start_index, end_index) if
                     (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]
        temp_pitch = [pitch_list[i].sample for i in range(start_index, end_index) if
                      (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]
        temp_yaw = [yaw_list[i].sample for i in range(start_index, end_index) if
                    (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]

        Gmag_sub = [gyr_mag[i].sample for i in range(start_index, end_index) if
                    (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]
        ay_sub = [accel[i].sample[1] for i in range(start_index, end_index) if
                    (accel_mag[i].sample > 0.9) and (accel_mag[i].sample < 1.1)]

        if len(temp_roll) == 0:
            continue


        duration = 1000 * (end_time - start_time).total_seconds()   # convert to milliseconds

        roll_mean, roll_median, roll_sd, roll_quartile = compute_basic_statistical_features(temp_roll)
        pitch_mean, pitch_median, pitch_sd, pitch_quartile = compute_basic_statistical_features(temp_pitch)
        yaw_mean, yaw_median, yaw_sd, yaw_quartile = compute_basic_statistical_features(temp_yaw)

        gyro_mean, gyro_median, gyro_sd, gyro_quartile = compute_basic_statistical_features(Gmag_sub)

        ay_mean, ay_median, ay_sd, ay_quartile = compute_basic_statistical_features(ay_sub)

        feature_vector = [duration,
                          roll_mean, roll_median, roll_sd, roll_quartile,
                          pitch_mean, pitch_median, pitch_sd, pitch_quartile,
                          yaw_mean, yaw_median, yaw_sd, yaw_quartile,
                          gyro_mean, gyro_median, gyro_sd, gyro_quartile,
                          ay_mean, ay_median, ay_sd, ay_quartile,
                          I.sample[2], I.sample[3], I.sample[4], I.sample[5],
                          I.sample[6], I.sample[7], I.sample[8], I.sample[9]]

        all_features.append(DataPoint(start_time=start_time, end_time=end_time, offset=offset, sample=feature_vector))

    return all_features


def compute_wrist_features(accel: List[DataPoint], gyro: List[DataPoint],
                           fast_moving_avg_size=13, slow_moving_avg_size=131) -> List[DataPoint]:
    gyr_mag = magnitude(gyro)
    accel_mag = magnitude(accel)

    # roll_list, pitch_list, yaw_list = calculate_roll_pitch_yaw(accel)
    roll_list, pitch_list, yaw_list = complementary_filter(accel, gyro)

    gyr_mag_800 = smooth(gyr_mag, fast_moving_avg_size)
    gyr_mag_8000 = smooth(gyr_mag, slow_moving_avg_size)

    gyr_intersections = moving_average_convergence_divergence_new(gyr_mag_8000, gyr_mag_800, accel)

    # gyr_intersections = filter_with_duration(gyr_intersections)
    # gyr_intersections = filter_with_roll_pitch(gyr_intersections, roll_list, pitch_list, yaw_list)
    # gyr_intersections = filter_with_complementary_roll_pitch(gyr_intersections, roll_list, pitch_list, yaw_list, accel_mag)
    #
    ay = [v.sample[1] for v in accel]
    print('75=' + str(np.percentile(ay, 75)) + '; 80=' + str(np.percentile(ay, 80)) + '; 90=' + str(np.percentile(ay, 90)))
    # print('75=' + str(np.percentile(ay, 75)) + '; 80=' + str(np.percentile(ay, 75)))
    # gyr_intersections = filter_with_accleY(gyr_intersections, accel, accel_mag)
    # gyr_intersections = filter_with_accleY_interval(gyr_intersections, accel, accel_mag, min(0.6, np.percentile(ay, 90)))

    all_features = compute_candidate_features(gyr_intersections, gyr_mag, roll_list, pitch_list, yaw_list, accel_mag, accel)

    return all_features
