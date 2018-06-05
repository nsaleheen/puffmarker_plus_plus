import numpy as np
from typing import List
from puffmarker.domain.datapoint import DataPoint
from numpy.linalg import norm


def magnitude(data: List[DataPoint]):

    input_sample = np.array([i.sample for i in data])

    mag_sample = norm(input_sample, axis=1).tolist()

    result = [DataPoint(start_time=v.start_time, offset=v.start_time, sample=mag_sample[i]) for i, v in enumerate(data)]

    return result


def smooth(data: List[DataPoint],
           span: int = 5) -> List[DataPoint]:

    """
    Smooths data using moving average filter over a span.
    The first few elements of data_smooth are given by
    data_smooth(1) = data(1)
    data_smooth(2) = (data(1) + data(2) + data(3))/3
    data_smooth(3) = (data(1) + data(2) + data(3) + data(4) + data(5))/5
    data_smooth(4) = (data(2) + data(3) + data(4) + data(5) + data(6))/5

    for more details follow the below links:
    https://www.mathworks.com/help/curvefit/smooth.html
    http://stackoverflow.com/a/40443565

    :return: data_smooth
    :param data:
    :param span:
    """

    if data is None or len(data) == 0:
        return []

    sample = [i.sample for i in data]
    sample_middle = np.convolve(sample, np.ones(span, dtype=int), 'valid') / span
    divisor = np.arange(1, span - 1, 2)
    sample_start = np.cumsum(sample[:span - 1])[::2] / divisor
    sample_end = (np.cumsum(sample[:-span:-1])[::2] / divisor)[::-1]
    sample_smooth = np.concatenate((sample_start, sample_middle, sample_end))

    data_smooth = []

    if len(sample_smooth) == len(data):
        for i, item in enumerate(data):
            dp = DataPoint.from_tuple(sample=sample_smooth[i], start_time=item.start_time, end_time=item.end_time)
            data_smooth.append(dp)
    else:
        raise Exception("Smoothed data length does not match with original data length.")

    return data_smooth


def moving_average_curve(data: List[DataPoint],
                         window_length: int) -> List[DataPoint]:
    """
    Moving average curve from filtered (using moving average) samples.

    :return: mac
    :param data:
    :param window_length:
    """
    if data is None or len(data) == 0:
        return []

    sample = [i.sample for i in data]
    mac = []
    for i in range(window_length, len(sample) - (window_length + 1)):
        sample_avg = np.mean(sample[i - window_length:i + window_length + 1])
        mac.append(DataPoint.from_tuple(sample=sample_avg, start_time=data[i].start_time, end_time=data[i].end_time))

    return mac

