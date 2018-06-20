import os
from typing import List
import seaborn as sns
import matplotlib.pyplot as plt
from puffmarker.plots.plot_signal import *
from puffmarker.wrist_features import *

from puffmarker.input.import_stream_processor_inputs import *
from puffmarker.utils.PUFFMARKER_CONSTANTS import *
from puffmarker.wrist_features import compute_wrist_features
from puffmarker.utils.pickle_utils import *

pids = ['p01', 'p02', 'p03', 'p04', 'p05', 'p06']


# pids = ['p04', 'p05', 'p06']
# pids = ['p05']

def main_plot_histogram_accelaxis():
    data_dir = '/home/nsaleheen/data/csvdataSI_new/'
    for pid in pids:
        basedir = data_dir + pid + '/'
        sids = [d for d in os.listdir(basedir) if os.path.isdir(os.path.join(basedir, d))]
        sids.sort()
        for sid in sids:
            cur_dir = data_dir + pid + '/' + sid + '/'
            print(cur_dir)

            for wrist in [LEFT_WRIST, RIGHT_WRIST]:

                accel = get_accelerometer(cur_dir, wrist)
                x = [v.sample[0] for v in accel]
                y = [v.sample[1] for v in accel]
                z = [v.sample[2] for v in accel]
                # the histogram of the data
                plt.hist(x, 50, normed=1, facecolor='green', alpha=0.25, label='x')
                plt.hist(y, 50, normed=1, facecolor='red', alpha=0.25, label='y')
                plt.hist(z, 50, normed=1, facecolor='blue', alpha=0.25, label='z')

                plt.legend()
                plt.title(pid + '_' + sid + '_' + wrist)
                plt.savefig(data_dir + '/plot_hist/' + pid + '_' + sid + '_' + wrist + '.png')

                plt.show()
                print('x', max(x), min(x), 'y', max(y), min(y), 'z', max(z), min(z))


def plot_puffs_and_episodes():
    data_dir = '/home/nsaleheen/data/csvdataSI_new/'
    for pid in pids:
        basedir = data_dir + pid + '/'
        sids = [d for d in os.listdir(basedir) if
                os.path.isdir(os.path.join(basedir, d))]
        sids.sort()
        for sid in sids:
            cur_dir = data_dir + pid + '/' + sid + '/'
            print(cur_dir)

            smoking_epis = get_marked_smoking_episodes(cur_dir, pid, sid)

            rip = get_respiration(cur_dir)

            accel_left = get_accelerometer(cur_dir, LEFT_WRIST)
            gyro_left = get_gyroscope(cur_dir, LEFT_WRIST)
            gyro_left = magnitude(gyro_left)
            accel_right = get_accelerometer(cur_dir, RIGHT_WRIST)
            gyro_right = get_gyroscope(cur_dir, RIGHT_WRIST)
            gyro_right = magnitude(gyro_right)

            puffs_left = get_marked_smoking_puffs_filtered(cur_dir, LEFT_WRIST)
            puffs_right = get_marked_smoking_puffs_filtered(cur_dir, RIGHT_WRIST)
            print('SE: ', smoking_epis)
            print('SP L: ', puffs_left)
            print('SP R: ', puffs_right)
            # puffs = get_all_marked_smoking_puffs(cur_dir, wrist, pid, sid)

            # plot_signal(accel_left, 0, 1, 'Accel', ['L-ax', 'L-ay', 'L-az'])
            # plt.plot([accel_left[0].start_time, accel_left[-1].start_time], [0, 0], '--k')
            # plot_signal(gyro_left, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag'])

            plot_signal(rip, -5, 1.0/500, 'Rip', ['rip'])

            plot_signal(accel_right, 0, 1, 'Accel', ['R-ax', 'R-ay', 'R-az'])
            plt.plot([accel_right[0].start_time, accel_right[-1].start_time], [0, 0], '--k')
            plot_signal(gyro_right, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag'])
            # if len(puffs_left)>0:
            #     plot_point(puffs_left, 10)
            if len(puffs_right)>0:
                plot_point(puffs_right, 6)
            # plot_line(smoking_epis, 12)
            plt.xticks(rotation=90)
            plt.legend()
            plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '.png')

            for i, epi in enumerate(smoking_epis):
                t_delta = timedelta(seconds=15)
                plt.xlim(epi.start_time - t_delta, epi.end_time + t_delta)
                # plt.text(epi.start_time - t_delta, 10, 'Puff-left', fontsize=20)
                # plt.text(epi.start_time - t_delta, 11, 'Puff-right', fontsize=20)
                # plt.text(epi.start_time - t_delta, 12, 'episode', fontsize=20)
                plt.title(pid + '_' + sid + '_e' + str(i))
                plt.xticks(rotation=90)
                plt.legend()
                plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '_' + str(i) + '_epi.png')

            # for i, epi in enumerate(puffs_left):
            #     t_delta = timedelta(seconds=5)
            #     plt.xlim(epi.start_time - t_delta, epi.start_time + t_delta)
            #     plt.text(epi.start_time - t_delta, 10, 'Puff-left', fontsize=20)
            #     plt.title(pid + '_' + sid + '_pl' + str(i))
            #     plt.legend()
            #     plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '_l' + str(i) + '_puff.png')

            for i, epi in enumerate(puffs_right):
                t_delta = timedelta(seconds=15)
                plt.xlim(epi.start_time - t_delta, epi.start_time + t_delta)
                # plt.text(epi.start_time - t_delta, 11, 'Puff-right', fontsize=20)
                plt.title(pid + '_' + sid + '_pl' + str(i))
                plt.legend()
                plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '_r' + str(i) + '_puff.png')

# def plot_puffs_and_episodes_candidate():
#     data_dir = '/home/nsaleheen/data/csvdataSI_new/'
#
#     Xs = []
#     Ys = []
#     TP = 0
#     FP = 0
#     FN = 0
#     nPuff = 0
#     # for i in range(len(pids)):
#     for pid in pids:
#         basedir = data_dir + pid + '/'
#         sids = [d for d in os.listdir(basedir) if
#                 os.path.isdir(os.path.join(basedir, d))]
#         sids.sort()
#         for sid in sids:
#             cur_dir = data_dir + pid + '/' + sid + '/'
#             print(cur_dir)
#
#             smoking_epis = get_marked_smoking_episodes(cur_dir, pid, sid)
#
#             for wrist in [LEFT_WRIST, RIGHT_WRIST]:
#
#                 accel = get_accelerometer(cur_dir, wrist)
#                 gyro = get_gyroscope(cur_dir, wrist)
#                 if len(accel) != len(gyro):
#                     print('accel gyro length different')
#                 puffs = get_marked_smoking_puffs_filtered(cur_dir, wrist)
#                 # puffs = get_all_marked_smoking_puffs(cur_dir, wrist, pid, sid)
#
#                 all_features = compute_wrist_features(accel,
#                                                       gyro,
#                                                       FAST_MOVING_AVG_SIZE,
#                                                       SLOW_MOVING_AVG_SIZE)
#                 # puff_labels_right = classify_puffs(all_features)
#
#                 st = [v.start_time for v in all_features]
#                 et = [v.end_time for v in all_features]
#
#                 # print(smoking_epis)
#                 # print(st)
#                 # print(et)
#                 for k in range(len(st)):
#                     label = getLabel(st[k], et[k], smoking_epis, puffs)
#                     if label != -1:
#                         Xs.append(all_features[k].sample)
#                         if label == 0:
#                             # Ys.append('non-puff')
#                             Ys.append(0)
#                         else:
#                             # Ys.append('puff')
#                             Ys.append(1)
#                             for m in range(5):
#                                 Xs.append(all_features[k].sample)
#                                 Ys.append(1)
#
#                 # ----------------------- for training print .............
#                 for pt in puffs:
#                     pt = pt.start_time
#                     is_found = False
#                     for k in range(len(st)):
#                         if (pt >= st[k]) & (pt <= et[k]):
#                             is_found = True
#                             break
#                     if is_found:
#                         TP = TP + 1
#                     else:
#                         FN = FN + 1
#                 nPuff = nPuff + len(puffs)
#
#             plot_signal(accel_left, 0, 1, 'Accel', ['L-ax', 'L-ay', 'L-az'])
#             plt.plot([accel_left[0].start_time, accel_left[-1].start_time], [0, 0], '--k')
#             plot_signal(gyro_left, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag'])
#
#             plot_signal(accel_right, 6, 1, 'Accel', ['R-ax', 'R-ay', 'R-az'])
#             plt.plot([accel_right[0].start_time, accel_right[-1].start_time], [6, 6], '--k')
#             plot_signal(gyro_right, 8.5, 1.0 / 100, 'Gyro', ['gyro_mag'])
#             if len(puffs_left)>0:
#                 plot_point(puffs_left, 10)
#             if len(puffs_right)>0:
#                 plot_point(puffs_right, 11)
#             plot_line(smoking_epis, 12)
#             plt.xticks(rotation=90)
#             plt.legend()
#             plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '.png')
#
#             for i, epi in enumerate(smoking_epis):
#                 t_delta = timedelta(seconds=15)
#                 plt.xlim(epi.start_time - t_delta, epi.end_time + t_delta)
#                 plt.text(epi.start_time - t_delta, 10, 'Puff-left', fontsize=20)
#                 plt.text(epi.start_time - t_delta, 11, 'Puff-right', fontsize=20)
#                 plt.text(epi.start_time - t_delta, 12, 'episode', fontsize=20)
#                 plt.title(pid + '_' + sid + '_e' + str(i))
#                 plt.xticks(rotation=90)
#                 plt.legend()
#                 plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '_' + str(i) + '_epi.png')
#
#             for i, epi in enumerate(puffs_left):
#                 t_delta = timedelta(seconds=5)
#                 plt.xlim(epi.start_time - t_delta, epi.start_time + t_delta)
#                 plt.text(epi.start_time - t_delta, 10, 'Puff-left', fontsize=20)
#                 plt.title(pid + '_' + sid + '_pl' + str(i))
#                 plt.legend()
#                 plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '_l' + str(i) + '_puff.png')
#
#             for i, epi in enumerate(puffs_right):
#                 t_delta = timedelta(seconds=5)
#                 plt.xlim(epi.start_time - t_delta, epi.start_time + t_delta)
#                 plt.text(epi.start_time - t_delta, 11, 'Puff-right', fontsize=20)
#                 plt.title(pid + '_' + sid + '_pl' + str(i))
#                 plt.legend()
#                 plt.savefig(data_dir + '/plot_signal/' + pid + '_' + sid + '_r' + str(i) + '_puff.png')


if __name__ == '__main__':
    # main_plot_histogram_accelaxis()
    plot_puffs_and_episodes()

