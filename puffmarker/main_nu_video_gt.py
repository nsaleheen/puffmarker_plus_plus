import os
from typing import List
import seaborn as sns

from puffmarker.input.import_NU_video_gt import *
from puffmarker.plots.plot_signal import *
from puffmarker.wrist_features import *
from puffmarker.input.import_stream_processor_inputs import get_respiration

pids = ['202_update', '205', '208', '209', '211', '212', '215', '218']
sids = [['0626'], ['0818'], [], ['0929'], ['1002'], ['1013'], ['1027'],
        ['1103']]
stream_process_puffs_filenames = ['202_0626_sp.csv', '205_0818_sp.csv',
                                  '209_0929_sp.csv', '211_1002_sp.csv',
                                  '212_1013_sp.csv', '215_1027_sp.csv',
                                  '218_1103_sp.csv']
# pids = ['p04', 'p05', 'p06']
pids = ['202_update', '205', '211', '218']
stream_process_puffs_filenames = ['202_0626_sp.csv', '205_0818_sp.csv',
                                  '211_1002_sp.csv',
                                  '215_1027_sp.csv',
                                  '218_1103_sp.csv']

# pids = ['202_update']

stream_process_puffs_filename = '202_0626_sp.csv'


# def getLabel(st, et, smoking_epis: List[DataPoint], puffs):
#     return label


def get_event_labels(gt: List[DataPoint], label=1) -> List[DataPoint]:
    if len(gt) == 0:
        return []
    puff_labels = []
    i = 0
    while i < len(gt):
        if gt[i] != None and gt[i].sample == 1:
            start_time = gt[i].start_time
            while i < len(gt) and gt[i].sample == 1:
                i += 1
            end_time = gt[i - 1].start_time
            puff_labels.append(
                DataPoint(start_time=start_time, end_time=end_time,
                          offset=gt[i - 1].offset, sample=[label]))
        else:
            i += 1
    return puff_labels


def main_process_puffmarker():
    data_dir = '/home/nsleheen/data/NU_data/Encoded_Data/'

    dir_sufix = '/RIGHT_WRIST/ACC_GYR/'
    # filename = 'acc_gyr_label_inlab_Smoking.csv'
    filename = 'acc_gyr_label_inlab_Eating.csv'
    # filename = 'acc_gyr_label_inlab_False.csv'
    all_features = []
    Ys = []
    for iii, pid in enumerate(pids):
        cur_data_dir = data_dir + pid + dir_sufix
        print(cur_data_dir)
        # rip = get_respiration(cur_data_dir)

        # accel, gyro, gt_sd, gt_fd, gt_dd, gt_cd = load_NU_data(cur_data_dir + filename)
        accel, gyro, gt_sd, gt_fd, gt_dd, gt_cd = import_data(cur_data_dir)

        gt_sd = get_event_labels(gt_sd, label_sd)
        gt_fd = get_event_labels(gt_fd, label_fd)
        gt_dd = get_event_labels(gt_dd, label_dd)
        gt_cd = get_event_labels(gt_cd, label_cd)
        print(pid, '------------------', len(gt_sd), len(gt_fd), len(gt_dd), len(gt_cd))
        # -------------------------------------
        gyr_mag = magnitude(gyro)
        accel_mag = magnitude(accel)

        # roll_list, pitch_list, yaw_list = calculate_roll_pitch_yaw(accel)
        roll_list, pitch_list, yaw_list = complementary_filter(accel, gyro)

        gyr_mag_800 = smooth(gyr_mag, FAST_MOVING_AVG_SIZE)
        gyr_mag_8000 = smooth(gyr_mag, SLOW_MOVING_AVG_SIZE)

        gyr_intersections = moving_average_convergence_divergence_new(
            gyr_mag_8000, gyr_mag_800, accel)

        # gyr_intersections = filter_with_duration(gyr_intersections)
        # gyr_intersections = filter_with_roll_pitch(gyr_intersections, roll_list, pitch_list, yaw_list)
        # gyr_intersections = filter_with_complementary_roll_pitch(gyr_intersections, roll_list, pitch_list, yaw_list, accel_mag)
        #
        # ay = [v.sample[1] for v in accel]
        # print('75=' + str(np.percentile(ay, 75)) + '; 80=' + str(
        #     np.percentile(ay, 80)) + '; 90=' + str(np.percentile(ay, 90)))
        # print('75=' + str(np.percentile(ay, 75)) + '; 80=' + str(np.percentile(ay, 75)))
        # gyr_intersections = filter_with_accleY(gyr_intersections, accel, accel_mag)
        # gyr_intersections = filter_with_accleY_interval(gyr_intersections, accel, accel_mag, min(0.6, np.percentile(ay, 90)))

        features = compute_candidate_features(gyr_intersections, gyr_mag,
                                              roll_list, pitch_list, yaw_list,
                                              accel_mag, accel)

        cand = [
            DataPoint(start_time=v.start_time, end_time=v.end_time, sample=[1])
            for v in features]

        for f in cand:
            is_smoking = False
            is_feeding = False
            is_drinking = False
            is_confounding = False
            for g in gt_sd:
                if min(f.end_time, g.end_time) > max(f.start_time, g.start_time):
                    is_smoking = True
            for g in gt_fd:
                if min(f.end_time, g.end_time) > max(f.start_time, g.start_time):
                    is_feeding = True
            for g in gt_dd:
                if min(f.end_time, g.end_time) > max(f.start_time, g.start_time):
                    is_drinking = True
            for g in gt_cd:
                if min(f.end_time, g.end_time) > max(f.start_time, g.start_time):
                    is_confounding = True
            if is_smoking == True:
                Ys.append(label_sd)
            elif is_feeding:
                Ys.append(label_fd)
            elif is_drinking:
                Ys.append(label_dd)
            elif is_confounding:
                Ys.append(label_cd)
            else:
                Ys.append(0)

        Y = np.array(Ys)
        print(pid, len(Y[Y==label_sd]), len(Y[Y==label_fd]), len(Y[Y==label_dd]) , len(Y[Y==label_cd]) )

        all_features.extend(features)
        # print('#cand = ', len(cand))
        #
        # plot_signal(rip, -7, 1.0/500, 'Rip', ['rip'])
        #
        # plot_signal(accel, 0, 1, 'Accel', ['accel-x', 'accel-y', 'accel-z'])
        # plot_signal(gyr_mag, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag'])
        # # plot_signal(gyr_mag_800, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag800'])
        # # plot_signal(gyr_mag_8000, 2.5, 1.0 / 100, 'Gyro', ['gyro_mag8000'])
        #
        # # plot_line([DataPoint(accel[0].start_time, accel[-1].start_time, '0', [1])], 0)
        # plt.plot([accel[0].start_time, accel[-1].start_time], [0, 0], '--k')
        #
        # # plot_line([DataPoint(accel[0].start_time, accel[-1].start_time, '0', [1])], 2.5)
        # # plot_point(gt, -3, 1, 'gt', ['puff'])
        #
        # plot_point(detected_puffs, -3, 1, pid, ['stream_processor'])
        # plot_point(detected_puffs, 6, 1, pid, ['stream_processor'])
        #
        # plot_line(gt, 5)
        # plot_line(cand, 4)
        # for i, v in enumerate(gt):
        #     t_delta = timedelta(seconds=5)
        #     plt.xlim(v.start_time - t_delta, v.end_time + t_delta)
        #     # plt.text(v.start_time - t_delta, 4, 'Cand', fontsize=20)
        #     plt.text(v.start_time - t_delta, 5, 'gt', fontsize=20)
        #     plt.title(pid + '_' + str(i))
        #     plt.legend()
        #     # plt.savefig(data_dir + '/plot_new/' + pid + '_' + str(i) + '_puff.png')
        #     # plt.savefig(data_dir + '/plot_new/' + pid + '_' + str(i) + '_bite.png')
        #     # plt.savefig(data_dir + '/plot_new/' + pid + '_' + str(i) + '_confounding_smoking.png')
        #     plt.savefig(data_dir + '/plot_new/' + pid + '_' + str(i) + '_confounding_eating.png')
        # plt.legend()
        # plt.show()
    return all_features, Ys


if __name__ == '__main__':
    # points = np.arange(-5, 5, 0.01)
    # dx, dy = np.meshgrid(points, points)
    # z = (np.sin(dx)+np.sin(dy))
    # plt.imshow(z)
    # plt.colorbar()
    # plt.title('plot for sin(x)+sin(y)')
    # plt.show()

    all_features, Ys = main_process_puffmarker()

    print('LEN::::', len(all_features), len(Ys), sum(Ys))

    Ys = np.array(Ys)
    all_features = np.array(all_features)
    all_features0 = all_features[Ys==0]
    Ys0 = Ys[Ys==0]
    all_features1 = all_features[Ys==1]
    Ys1 = Ys[Ys==1]
    all_features2 = all_features[Ys==2]
    Ys2 = Ys[Ys==2]
    all_features3 = all_features[Ys==3]
    Ys3 = Ys[Ys==3]
    all_features4 = all_features[Ys==4]
    Ys4 = Ys[Ys==4]

    roll0 = [x.sample[1] for i, x in enumerate(all_features0)]
    pitch0 = [x.sample[5] for i, x in enumerate(all_features0)]
    yaw0 = [x.sample[9] for i, x in enumerate(all_features0)]
    roll1 = [x.sample[1] for i, x in enumerate(all_features1)]
    pitch1 = [x.sample[5] for i, x in enumerate(all_features1)]
    yaw1 = [x.sample[9] for i, x in enumerate(all_features1)]
    roll2 = [x.sample[1] for i, x in enumerate(all_features2)]
    pitch2 = [x.sample[5] for i, x in enumerate(all_features2)]
    yaw2 = [x.sample[9] for i, x in enumerate(all_features2)]

    roll3 = [x.sample[1] for i, x in enumerate(all_features3)]
    pitch3 = [x.sample[5] for i, x in enumerate(all_features3)]
    yaw3 = [x.sample[9] for i, x in enumerate(all_features3)]

    roll4 = [x.sample[1] for i, x in enumerate(all_features4)]
    pitch4 = [x.sample[5] for i, x in enumerate(all_features4)]
    yaw4 = [x.sample[9] for i, x in enumerate(all_features4)]

    # plt.plot(roll0, pitch0, '.b')
    plt.plot(roll4, pitch4, '.b')
    plt.plot(roll1, pitch1, '.r')
    plt.plot(roll2, pitch2, '*g')
    plt.plot(roll3, pitch3, 'dk')
    plt.title('roll-pitch')
    plt.show()
    # plt.plot(roll0, yaw0, '.b')
    plt.plot(roll4, yaw4, '.b')
    plt.plot(roll1, yaw1, '.r')
    plt.plot(roll2, yaw2, '*g')
    plt.plot(roll3, yaw3, 'dk')
    plt.title('roll-yaw')
    plt.show()
    # plt.plot(pitch0, yaw0, '.b')
    plt.plot(pitch4, yaw4, '.b')
    plt.plot(pitch1, yaw1, '.r')
    plt.plot(pitch2, yaw2, '*g')
    plt.plot(pitch3, yaw3, 'dk')
    plt.title('pitch-yaw')
    plt.show()

    # print('avg roll = ' + str(min(roll)) + ', ' + str(max(roll)))
    # print('avg pitch = ' + str(min(pitch)) + ', ' + str(max(pitch)))
    # print('avg yaw = ' + str(min(yaw)) + ', ' + str(max(yaw)))

# avg roll = 4.64535557352, 51.7689940023
# avg pitch = -133.469444281, -113.229638214
# avg yaw = 32.9308641721, 84.060616845
# comp
# avg roll = -44.369484683, -20.1868872802
# avg pitch = 10.3523201513, 71.4914146706
# avg yaw = 32.7350584684, 85.6169777669
