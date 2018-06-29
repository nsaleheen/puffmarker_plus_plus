from puffmarker.main_nu_video_gt import main_process_puffmarker
from puffmarker.main_train_6smoker import main_process_segments
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

if __name__ == '__main__':

# ------------- 6 smokers data --------------------------------
    all_features, Ys = main_process_segments()
    Ys = np.array(Ys)
    all_features = np.array(all_features)
    all_features0 = all_features[Ys==0]
    Ys0 = Ys[Ys==0]
    all_features1 = all_features[Ys==1]
    Ys1 = Ys[Ys==1]
    print('total', len(all_features), 'unknown', len(Ys0), 'smoking', len(Ys1))

    dur0 = [x.sample[0] for i, x in enumerate(all_features0)]
    roll0 = [x.sample[1] for i, x in enumerate(all_features0)]
    pitch0 = [x.sample[5] for i, x in enumerate(all_features0)]
    yaw0 = [x.sample[9] for i, x in enumerate(all_features0)]

    dur1_UM = [x.sample[0] for i, x in enumerate(all_features1)]
    roll1_UM = [x.sample[1] for i, x in enumerate(all_features1)]
    pitch1_UM = [x.sample[5] for i, x in enumerate(all_features1)]
    yaw1_UM = [x.sample[9] for i, x in enumerate(all_features1)]

    plt.plot(roll0, pitch0, '.b', label='non-puff')
    plt.plot(roll1_UM, pitch1_UM, '.r', label='puff')
    plt.xlabel('Roll')
    plt.ylabel('Pitch')
    plt.title('6 smoker data')
    plt.show()
    plt.plot(roll0, yaw0, '.b')
    plt.plot(roll1_UM, yaw1_UM, '.r')
    plt.xlabel('Roll')
    plt.ylabel('Yaw')
    plt.title('6 smoker data')
    plt.show()
    plt.plot(pitch0, yaw0, '.b')
    plt.plot(pitch1_UM, yaw1_UM, '.r')
    plt.xlabel('Pitch')
    plt.ylabel('Yaw')
    plt.title('6 smoker data')
    plt.show()

# ------------- NU smokers data --------------------------------

    all_features, Ys = main_process_puffmarker()

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

    print('total', len(all_features), 'unknown', len(Ys0), 'smoking', len(Ys1), 'feeding', len(Ys2), 'drinking', len(Ys3), 'confounding', len(Ys4))
    # total 4358 unknown 3533 smoking 147 feeding 369 drinking 31 confounding 278

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
    plt.plot(roll4, pitch4, '.b', label='conf')
    plt.plot(roll1, pitch1, '.r', label='puff')
    plt.plot(roll2, pitch2, '*g', label='feed')
    plt.plot(roll3, pitch3, 'dk', label='drink')
    plt.xlabel('Roll')
    plt.ylabel('Pitch')
    plt.title('NU lab data')
    plt.legend()
    plt.show()
    # plt.plot(roll0, yaw0, '.b')
    plt.plot(roll4, yaw4, '.b', label='conf')
    plt.plot(roll1, yaw1, '.r', label='puff')
    plt.plot(roll2, yaw2, '*g', label='feed')
    plt.plot(roll3, yaw3, 'dk', label='drink')
    plt.xlabel('Roll')
    plt.ylabel('Yaw')
    plt.title('NU lab data')
    plt.legend()
    plt.show()
    # plt.plot(pitch0, yaw0, '.b')
    plt.plot(pitch4, yaw4, '.b', label='conf')
    plt.plot(pitch1, yaw1, '.r', label='puff')
    plt.plot(pitch2, yaw2, '*g', label='feed')
    plt.plot(pitch3, yaw3, 'dk', label='drink')
    plt.xlabel('Pitch')
    plt.ylabel('Yaw')
    plt.title('NU lab data')
    plt.legend()
    plt.show()

    sns.distplot(roll4, hist=False, label='conf')
    sns.distplot(roll1, hist=False, label='puff')
    sns.distplot(roll2, hist=False, label='feed')
    sns.distplot(roll3, hist=False, label='drink')
    plt.title('Roll - NU')
    plt.show()

    sns.distplot(pitch4, hist=False, label='conf')
    sns.distplot(pitch1, hist=False, label='puff')
    sns.distplot(pitch2, hist=False, label='feed')
    sns.distplot(pitch3, hist=False, label='drink')
    plt.title('Pitch - NU')
    plt.show()

    sns.distplot(yaw4, hist=False, label='conf')
    sns.distplot(yaw1, hist=False, label='puff')
    sns.distplot(yaw2, hist=False, label='feed')
    sns.distplot(yaw3, hist=False, label='drink')
    plt.title('Yaw - NU')
    plt.show()


# --------- combine 2 dataset ----------
    sns.distplot(roll1, hist=False, label='NU lab')
    sns.distplot(roll1_UM, hist=False, label='Memphis')
    plt.title('Roll - Memphis vs NU')
    plt.show()
    sns.distplot(pitch1, hist=False, label='NU lab')
    sns.distplot(pitch1_UM, hist=False, label='Memphis')
    plt.title('Pitch - Memphis vs NU')
    plt.show()
    sns.distplot(yaw1, hist=False, label='NU lab')
    sns.distplot(yaw1_UM, hist=False, label='Memphis')
    plt.title('Yaw - Memphis vs NU')
    plt.show()
