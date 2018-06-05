from typing import List
from puffmarker.domain.datapoint import DataPoint
import numpy as np

def getInterpoletedValue(g0, g1, t0, t1, t):
    g = g0 + (g1 - g0) * (t - t0) / (t1 - t0)
    return g



def merge_two_datastream(accel: List[DataPoint], gyro: List[DataPoint]):
    # usually accel is 16Hz and gyro is 32 Hz
    # make gyro 16 Hz
    A = np.array(
        [[dp.start_time.timestamp(), dp.sample[0], dp.sample[1], dp.sample[2]]
         for dp in accel])
    G = np.array(
        [[dp.start_time.timestamp(), dp.sample[0], dp.sample[1], dp.sample[2]]
         for dp in gyro])
    At = A[:, 0]

    Gt = G[:, 0]
    Gx = G[:, 1]
    Gy = G[:, 2]
    Gz = G[:, 3]
    i = 0
    j = 0
    _Gx = [0] * len(At)
    _Gy = [0] * len(At)
    _Gz = [0] * len(At)
    while (i < len(At)) and (j < len(Gt)):
        while Gt[j] < At[i]:
            j = j + 1
            if j >= len(Gt):
                break
        if j < len(Gt):
            if (At[i] == Gt[j]) | (j == 0):
                _Gx[i] = Gx[j]
                _Gy[i] = Gy[j]
                _Gz[i] = Gz[j]
            else:
                _Gx[i] = getInterpoletedValue(Gx[j - 1], Gx[j], Gt[j - 1],
                                              Gt[j], At[i])
                _Gy[i] = getInterpoletedValue(Gy[j - 1], Gy[j], Gt[j - 1],
                                              Gt[j], At[i])
                _Gz[i] = getInterpoletedValue(Gz[j - 1], Gz[j], Gt[j - 1],
                                              Gt[j], At[i])
        i = i + 1

    gyro = [DataPoint(start_time=dp.start_time, end_time=dp.end_time,
                      offset=dp.offset, sample=[_Gx[i], _Gy[i], _Gz[i]])
            for i, dp in enumerate(accel)]
    return gyro
