import matplotlib.pyplot as plt
from typing import List

from puffmarker.domain.datapoint import DataPoint


def plot_signal(data: List[DataPoint], y_offset=0, y_factor=1, plot_title='',
                legend_list=[]):
    if len(data) == 0:
        return

    # X = [v.start_time.timestamp() for v in data]
    X = [v.start_time for v in data]

    if not isinstance(data[0].sample, List):
        Y = [v.sample * y_factor + y_offset for v in data]
        plt.plot(X, Y, label=legend_list[0])
    else:
        sample_size = len(data[0].sample)
        for i in range(sample_size):
            Y = [v.sample[i] * y_factor + y_offset for v in data]
            plt.plot(X, Y, label=legend_list[i])
    plt.title(plot_title)


def plot_point(data: List[DataPoint], y_offset=0, y_factor=1, plot_title='',
               legend_list=[]):
    if len(data) == 0:
        return
    # X = [v.start_time.timestamp() for v in data]
    X = [v.start_time for v in data]
    if not isinstance(data[0].sample, List):
        Y = [v.sample * y_factor + y_offset for v in data]
        if len(legend_list) > 0:
            plt.plot(X, Y, '*', label=legend_list[0])
        else:
            plt.plot(X, Y, '*')
    else:
        sample_size = len(data[0].sample)
        for i in range(sample_size):
            Y = [v.sample[i] * y_factor + y_offset for v in data]
            if len(legend_list)>0:
                plt.plot(X, Y, '*', label=legend_list[0])
            else:
                plt.plot(X, Y, '*')
    plt.title(plot_title)

import numpy
def plot_line(data: List[DataPoint], y_offset=0, legend_list=[]):
    if len(data) == 0:
        return

    c=numpy.random.rand(3,)
    # print(c)

    v = data[0]
    if len(legend_list) > 0:
        plt.plot([v.start_time, v.end_time], [y_offset, y_offset], label=legend_list[0], c=c)
    else:
        plt.plot([v.start_time, v.end_time], [y_offset, y_offset], c=c)

    for i, v in enumerate(data[1:]):
        plt.plot([v.start_time, v.end_time], [y_offset+0.1, y_offset], c=c)
