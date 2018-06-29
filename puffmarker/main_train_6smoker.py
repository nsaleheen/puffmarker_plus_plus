import os


from puffmarker.input.import_stream_processor_inputs import *
from puffmarker.utils.PUFFMARKER_CONSTANTS import *
from puffmarker.wrist_features import compute_wrist_features
from puffmarker.utils.pickle_utils import *

pids = ['p01', 'p02', 'p03', 'p04', 'p05', 'p06']


pids = ['p04', 'p05', 'p06']
# pids = ['p05']


def getLabel(st, et, smoking_epis: List[DataPoint], puffs):
    label = 0  # not puff
    #     print(range(len(puff_times)))
    for puff in puffs:
        if (puff.start_time >= st) & (puff.start_time <= et):
            label = 1
            return label

    for epi in smoking_epis:
        if ((epi.start_time <= st) & (st <= epi.end_time)) | (
                (epi.start_time <= et) & (et <= epi.end_time)):
            label = -1  # included episode but not puff
            return label
    return label


def main_process_segments():
    fastSize = 13
    slowSize = 131

    data_dir = '/home/nsleheen/data/csvdataSI_new/'

    Xs = []
    Ys = []
    nSample = 0
    TP = 0
    FP = 0
    FN = 0
    nPuff = 0
    feature_vectors = []
    # for i in range(len(pids)):
    for pid in pids:
        basedir = data_dir + pid + '/'
        sids = [d for d in os.listdir(basedir) if
                os.path.isdir(os.path.join(basedir, d))]
        sids.sort()
        for sid in sids:
            cur_dir = data_dir + pid + '/' + sid + '/'
            print(cur_dir)

            smoking_epis = get_marked_smoking_episodes(cur_dir, pid, sid)

            for wrist in [LEFT_WRIST, RIGHT_WRIST]:

                accel = get_accelerometer(cur_dir, wrist)
                gyro = get_gyroscope(cur_dir, wrist)
                if len(accel) != len(gyro):
                    print('accel gyro length different')
                puffs = get_marked_smoking_puffs_filtered(cur_dir, wrist)
                # puffs = get_all_marked_smoking_puffs(cur_dir, wrist, pid, sid)

                all_features = compute_wrist_features(accel,
                                                      gyro,
                                                      FAST_MOVING_AVG_SIZE,
                                                      SLOW_MOVING_AVG_SIZE)
                # puff_labels_right = classify_puffs(all_features)

                st = [v.start_time for v in all_features]
                et = [v.end_time for v in all_features]

                # print(smoking_epis)
                # print(st)
                # print(et)
                for k in range(len(st)):
                    label = getLabel(st[k], et[k], smoking_epis, puffs)
                    if label != -1:
                        Xs.append(all_features[k].sample)
                        feature_vectors.append(all_features[k])
                        if label == 0:
                            # Ys.append('non-puff')
                            Ys.append(0)
                        else:
                            # Ys.append('puff')
                            Ys.append(1)
                            # for m in range(5):
                            #     Xs.append(all_features[k].sample)
                            #     Ys.append(1)

                # ----------------------- for training print .............
                for pt in puffs:
                    pt = pt.start_time
                    is_found = False
                    for k in range(len(st)):
                        if (pt >= st[k]) & (pt <= et[k]):
                            is_found = True
                            break
                    if is_found:
                        TP = TP + 1
                    else:
                        FN = FN + 1
                nPuff = nPuff + len(puffs)

        print(FN)
        print(TP)
        print(nPuff)
        #
    # print(len(Ys))
    # #     print(sum(Ys))
    #
    # print(nSample)

    print('matched = ' + str(TP))
    print('missed = ' + str(FN))
    print('total positive= ' + str(nPuff))
    print('total candidates= ' + str(len(Ys)))

    # return Xs, Ys
    return feature_vectors, Ys


if __name__ == '__main__':
    # points = np.arange(-5, 5, 0.01)
    # dx, dy = np.meshgrid(points, points)
    # z = (np.sin(dx)+np.sin(dy))
    # plt.imshow(z)
    # plt.colorbar()
    # plt.title('plot for sin(x)+sin(y)')
    # plt.show()

    Xs, Ys = main_process_segments()
    save_pickle('Xs', Xs)
    save_pickle('Ys', Ys)
    #
    R_nonpuff = [x[1] for i, x in enumerate(Xs) if Ys[i] == 0]
    R_puff = [x[1] for i, x in enumerate(Xs) if Ys[i] == 1]

    P_nonpuff = [x[5] for i, x in enumerate(Xs) if Ys[i] == 0]
    P_puff = [x[5] for i, x in enumerate(Xs) if Ys[i] == 1]

    Y_nonpuff = [x[9] for i, x in enumerate(Xs) if Ys[i] == 0]
    Y_puff = [x[9] for i, x in enumerate(Xs) if Ys[i] == 1]

    prev_peak_puff = [x[-4] for i, x in enumerate(Xs) if Ys[i] == 1]
    nxt_peak_puff = [x[-3] for i, x in enumerate(Xs) if Ys[i] == 1]

    prev_peak_diff_puff = [x[-2] for i, x in enumerate(Xs) if Ys[i] == 1]
    nxt_peak_diff_puff = [x[-1] for i, x in enumerate(Xs) if Ys[i] == 1]

    prev_peak_area_puff = [x[-2] * x[-4] for i, x in enumerate(Xs) if
                           Ys[i] == 1]
    nxt_peak_area_puff = [x[-1] * x[-3] for i, x in enumerate(Xs) if Ys[i] == 1]

    print('avg roll = ' + str(min(R_puff)) + ', ' + str(max(R_puff)))
    print('avg pitch = ' + str(min(P_puff)) + ', ' + str(max(P_puff)))
    print('avg yaw = ' + str(min(Y_puff)) + ', ' + str(max(Y_puff)))
    print('avg prev_peak dur = ' + str(min(prev_peak_puff)) + ', ' + str(
        max(prev_peak_puff)))
    print('avg next_peak dur = ' + str(min(nxt_peak_puff)) + ', ' + str(
        max(nxt_peak_puff)))

    print('avg prev_peak diff = ' + str(min(prev_peak_diff_puff)) + ', ' + str(
        max(prev_peak_diff_puff)))
    print('avg next_peak diff = ' + str(min(nxt_peak_diff_puff)) + ', ' + str(
        max(nxt_peak_diff_puff)))

    print('avg prev_peak area = ' + str(min(prev_peak_area_puff)) + ', ' + str(
        max(prev_peak_area_puff)))
    print('avg next_peak area = ' + str(min(nxt_peak_area_puff)) + ', ' + str(
        max(nxt_peak_area_puff)))

    R_nonpuff = [x[2] for i, x in enumerate(Xs) if Ys[i] == 0]
    R_puff = [x[2] for i, x in enumerate(Xs) if Ys[i] == 1]

    P_nonpuff = [x[6] for i, x in enumerate(Xs) if Ys[i] == 0]
    P_puff = [x[6] for i, x in enumerate(Xs) if Ys[i] == 1]

    Y_nonpuff = [x[10] for i, x in enumerate(Xs) if Ys[i] == 0]
    Y_puff = [x[10] for i, x in enumerate(Xs) if Ys[i] == 1]

    print('med roll = ' + str(min(R_puff)) + ', ' + str(max(R_puff)))
    print('med pitch = ' + str(min(P_puff)) + ', ' + str(max(P_puff)))
    print('med yaw = ' + str(min(Y_puff)) + ', ' + str(max(Y_puff)))

    # sns.distplot([v[0] for v in RPY_nonpuff], hist=False, rug=True, label='roll non puff')
    # sns.distplot([v[1] for v in RPY_nonpuff], hist=False, rug=True, label='pitch non puff')
    # sns.distplot([v[2] for v in RPY_nonpuff], hist=False, rug=True, label='yaw non puff')

    # sns.distplot(R_puff, hist=False, rug=True, label='roll puff')
    # sns.distplot(P_puff, hist=False, rug=True, label='pitch puff')
    # sns.distplot(Y_puff, hist=False, rug=True, label='yaw puff')

    # sns.distplot(prev_peak_area_puff, hist=False, rug=True, label='prev_peak_area_puff')
    # sns.distplot(nxt_peak_area_puff, hist=False, rug=True, label='nxt_peak_area_puff')
    #
    #
    # plt.show()
    #
    #
    # Xs = np.array(Xs)
    # Ys = np.array([Ys])
    # M = np.concatenate((Xs, Ys.T), axis=1)

# filter both
# matched = 283
# missed = 19
# total positive= 302
# total candidates= 3294

# filter roll pitch
# matched = 283
# missed = 19
# total positive= 302
# total candidates= 41355

# complementary filter
# matched = 283
# missed = 19
# total positive= 302
# total candidates= 2765
# roll = 43.4513834902, -19.0186393702
# pitch = 166.085487833, -158.208668053
# yaw = 107.85341914, 24.2115948997

# filter duration orientation accelY
# matched = 282
# missed = 20
# total positive= 302
# total candidates= 2454
