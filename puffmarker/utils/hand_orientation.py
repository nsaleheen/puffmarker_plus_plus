import math
from typing import List

from puffmarker.domain.datapoint import DataPoint


def complementary_filter(accel: List[DataPoint], gyro: List[DataPoint], fq=16.0):
    ts = [v.start_time for v in accel]
    acc_x = [v.sample[0] for v in accel]
    acc_y = [v.sample[1] for v in accel]
    acc_z = [v.sample[2] for v in accel]

    gyr_x = [v.sample[0] for v in gyro]
    gyr_y = [v.sample[1] for v in gyro]
    gyr_z = [v.sample[2] for v in gyro]

    dt = 1.0 / fq  # 1/16.0;
    M_PI = math.pi
    hpf = 0.85
    lpf = 0.15

    thetaX_acc = [0] * len(acc_x)  # math.atan2(-acc_z,acc_y)*180/M_PI;
    thetaY_acc = [0] * len(acc_x)  # math.atan2(acc_x,acc_z)*180/M_PI;
    thetaZ_acc = [0] * len(acc_x)  # math.atan2(acc_y,acc_x)*180/M_PI;

    thetaX = [0] * len(gyr_x)
    thetaY = [0] * len(gyr_y)
    thetaZ = [0] * len(gyr_z)

    for index in range(len(gyr_x)):
        thetaX_acc[index] = math.atan2(-acc_z[index], acc_y[index]) * 180 / M_PI
        thetaY_acc[index] = math.atan2(acc_x[index], acc_z[index]) * 180 / M_PI
        thetaZ_acc[index] = math.atan2(acc_y[index], acc_x[index]) * 180 / M_PI

        if index == 0:
            thetaX[index] = hpf * thetaX[index] * dt + lpf * thetaX_acc[index]
            thetaY[index] = hpf * thetaY[index] * dt + lpf * thetaY_acc[index]
            thetaZ[index] = hpf * thetaZ[index] * dt + lpf * thetaZ_acc[index]
        else:
            thetaX[index] = hpf * (thetaX[index - 1] + gyr_x[index] * dt) + lpf * thetaX_acc[index]
            thetaY[index] = hpf * (thetaY[index - 1] + gyr_y[index] * dt) + lpf * thetaY_acc[index]
            thetaZ[index] = hpf * (thetaZ[index - 1] + gyr_z[index] * dt) + lpf * thetaZ_acc[index]

    rolls = [DataPoint(start_time=v.start_time, sample=thetaX[i]) for i, v in enumerate(accel)]
    pitches = [DataPoint(start_time=v.start_time, sample=thetaY[i]) for i, v in enumerate(accel)]
    yaws = [DataPoint(start_time=v.start_time, sample=thetaZ[i]) for i, v in enumerate(accel)]
    return rolls, pitches, yaws

def calculate_roll_pitch_yaw(accel_data: List[DataPoint]):
    '''
    Computes hand orientation (roll, pitch, yaw) from accelerometer signal
    :param accel_data:
    :return: roll_list, pitch_list, yaw_list
    '''
    roll_list = calculate_roll(accel_data)
    pitch_list = calculate_pitch(accel_data)
    yaw_list = calculate_yaw(accel_data)

    return roll_list, pitch_list, yaw_list


def calculate_roll(accel_data: List[DataPoint]):
    roll_list = []
    for dp in accel_data:
        ax = dp.sample[0]
        ay = dp.sample[1]
        az = dp.sample[2]
        rll = 180 * math.atan2(ax, math.sqrt(ay * ay + az * az)) / math.pi
        roll_list.append(DataPoint(start_time=dp.start_time, end_time=dp.end_time, offset=dp.offset, sample=rll))

    return roll_list


def calculate_pitch(accel_data: List[DataPoint]):
    pitch_list = []
    for dp in accel_data:
        ay = dp.sample[1]
        az = dp.sample[2]
        ptch = 180 * math.atan2(-ay, -az) / math.pi
        pitch_list.append(DataPoint(start_time=dp.start_time, end_time=dp.end_time, offset=dp.offset, sample=ptch))

    return pitch_list


def calculate_yaw(accel_data: List[DataPoint]):
    yaw_list = []
    for dp in accel_data:
        ax = dp.sample[0]
        ay = dp.sample[1]
        yw = 180 * math.atan2(ay, ax) / math.pi
        yaw_list.append(DataPoint(start_time=dp.start_time, end_time=dp.end_time, offset=dp.offset, sample=yw))

    return yaw_list
