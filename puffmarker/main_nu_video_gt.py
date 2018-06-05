import os
from typing import List
import seaborn as sns

from puffmarker.input.import_NU_video_gt import *
from puffmarker.plots.plot_signal import *
from puffmarker.wrist_features import *

pids = ['202_update', '205', '208', '209', '211', '212', '215', '218']
sids = [['0626'], ['0818'], [], ['0929'], ['1002'], ['1013'], ['1027'],
        ['1103']]
stream_process_puffs_filenames = ['202_0626_sp.csv', '205_0818_sp.csv',
                                  '209_0929_sp.csv', '211_1002_sp.csv',
                                  '212_1013_sp.csv', '215_1027_sp.csv',
                                  '218_1103_sp.csv']
# pids = ['p04', 'p05', 'p06']
pids = ['202_update', '205', '211', '215', '218']
stream_process_puffs_filenames = ['202_0626_sp.csv', '205_0818_sp.csv',
                                  '211_1002_sp.csv',
                                  '215_1027_sp.csv',
                                  '218_1103_sp.csv']

# pids = ['202_update']

stream_process_puffs_filename = '202_0626_sp.csv'


# def getLabel(st, et, smoking_epis: List[DataPoint], puffs):
#     return label


def get_puff_labels(gt: List[DataPoint]) -> List[DataPoint]:
    puff_labels = []
    i = 0
    while i < len(gt):
        if gt[i].sample == 1:
            start_time = gt[i].start_time
            while i < len(gt) and gt[i].sample == 1:
                i += 1
            end_time = gt[i - 1].start_time
            puff_labels.append(
                DataPoint(start_time=start_time, end_time=end_time,
                          offset=gt[i - 1].offset, sample=[1]))
        else:
            i += 1
    return puff_labels


def main_process_puffmarker():
    data_dir = '/home/nsaleheen/data/NU_data/Encoded_Data/'
    dir_sufix = '/RIGHT_WRIST/ACC_GYR/'
    filename = 'acc_gyr_label_inlab_Smoking.csv'
    all_features = []
    for iii, pid in enumerate(pids):
        cur_data_dir = data_dir + pid + dir_sufix
        print(cur_data_dir)

        accel, gyro, gt = load_data(cur_data_dir + filename)
        stream_process_puffs_filename = stream_process_puffs_filenames[iii]
        detected_puffs = load_detected_puff_timings(
            '/home/nsaleheen/data/NU_data/Encoded_Data/stream-processor-outputs/' + stream_process_puffs_filename)
        detected_puffs = [v for v in detected_puffs if v.start_time >= accel[0].start_time and v.start_time <=accel[-1].start_time]
        gt = get_puff_labels(gt)
        print('------------------', len(detected_puffs), len(gt))
        # -------------------------------------
        gyr_mag = magnitude(gyro)
        accel_mag = magnitude(accel)

        roll_list, pitch_list, yaw_list = calculate_roll_pitch_yaw(accel)
        # roll_list, pitch_list, yaw_list = complementary_filter(accel, gyro)

        gyr_mag_800 = smooth(gyr_mag, FAST_MOVING_AVG_SIZE)
        gyr_mag_8000 = smooth(gyr_mag, SLOW_MOVING_AVG_SIZE)

        gyr_intersections = moving_average_convergence_divergence_new(
            gyr_mag_8000, gyr_mag_800, accel)

        gyr_intersections = filter_with_duration(gyr_intersections)
        gyr_intersections = filter_with_roll_pitch(gyr_intersections, roll_list, pitch_list, yaw_list)
        # gyr_intersections = filter_with_complementary_roll_pitch(gyr_intersections, roll_list, pitch_list, yaw_list, accel_mag)
        #
        ay = [v.sample[1] for v in accel]
        print('75=' + str(np.percentile(ay, 75)) + '; 80=' + str(
            np.percentile(ay, 80)) + '; 90=' + str(np.percentile(ay, 90)))
        # print('75=' + str(np.percentile(ay, 75)) + '; 80=' + str(np.percentile(ay, 75)))
        # gyr_intersections = filter_with_accleY(gyr_intersections, accel, accel_mag)
        # gyr_intersections = filter_with_accleY_interval(gyr_intersections, accel, accel_mag, min(0.6, np.percentile(ay, 90)))

        features = compute_candidate_features(gyr_intersections, gyr_mag,
                                              roll_list, pitch_list, yaw_list,
                                              accel_mag, accel)

        # -------------------------------------
        #         features = compute_wrist_features(accel,
        #                                               gyro,
        #                                               FAST_MOVING_AVG_SIZE,
        #                                               SLOW_MOVING_AVG_SIZE)

        cand = [
            DataPoint(start_time=v.start_time, end_time=v.end_time, sample=[1])
            for v in features]

        all_features.extend(features)
        print('#cand = ', len(cand))

        plot_signal(accel, 0, 1, 'Accel', ['accel-x', 'accel-y', 'accel-z'])
        plot_signal(gyr_mag, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag'])
        # plot_signal(gyr_mag_800, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag800'])
        # plot_signal(gyr_mag_8000, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag8000'])

        # plot_line([DataPoint(accel[0].start_time, accel[-1].start_time, '0', [1])], 0)
        plt.plot([accel[0].start_time, accel[-1].start_time], [0, 0], '--k')

        # plot_line([DataPoint(accel[0].start_time, accel[-1].start_time, '0', [1])], 2.5)
        # plot_point(gt, -3, 1, 'gt', ['puff'])

        plot_point(detected_puffs, -3, 1, pid, ['stream_processor'])
        plot_point(detected_puffs, 6, 1, pid, ['stream_processor'])

        plot_line(gt, 5)
        plot_line(cand, 4)
        for i, v in enumerate(gt):
            t_delta = timedelta(seconds=2)
            plt.xlim(v.start_time - t_delta, v.end_time + t_delta)
            # plt.text(v.start_time - t_delta, 4, 'Cand', fontsize=20)
            plt.text(v.start_time - t_delta, 5, 'gt', fontsize=20)
            plt.title(pid + '_' + str(i))
            plt.legend()
            plt.savefig(data_dir + '/plot_new/' + pid + '_' + str(i) + '_puff.png')
        plt.legend()
        plt.show()
    return all_features


if __name__ == '__main__':
    # points = np.arange(-5, 5, 0.01)
    # dx, dy = np.meshgrid(points, points)
    # z = (np.sin(dx)+np.sin(dy))
    # plt.imshow(z)
    # plt.colorbar()
    # plt.title('plot for sin(x)+sin(y)')
    # plt.show()

    all_features = main_process_puffmarker()
    roll = [x.sample[1] for i, x in enumerate(all_features)]
    pitch = [x.sample[5] for i, x in enumerate(all_features)]
    yaw = [x.sample[9] for i, x in enumerate(all_features)]
    print('avg roll = ' + str(min(roll)) + ', ' + str(max(roll)))
    print('avg pitch = ' + str(min(pitch)) + ', ' + str(max(pitch)))
    print('avg yaw = ' + str(min(yaw)) + ', ' + str(max(yaw)))

# avg roll = 4.64535557352, 51.7689940023
# avg pitch = -133.469444281, -113.229638214
# avg yaw = 32.9308641721, 84.060616845
# comp
# avg roll = -44.369484683, -20.1868872802
# avg pitch = 10.3523201513, 71.4914146706
# avg yaw = 32.7350584684, 85.6169777669
