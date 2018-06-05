import os
import numpy as np
import pandas as pd

import datetime
import uuid
from typing import List
from uuid import UUID

from datetime import datetime, timedelta
from typing import Any
import sys
import json
import codecs
import gzip
import numpy as np

from time import time
from scipy.stats import randint as sp_randint

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, make_scorer
from sklearn.metrics import precision_recall_fscore_support, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report
from scikitplot.metrics import plot_confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scikitplot as skplt

MINIMUM_TIME_DIFFERENCE_BETWEEN_EPISODES = 10 * 60 * 1000;
# MINIMUM_TIME_DIFFERENCE_FIRST_AND_LAST_PUFFS = 7 * 60 * 1000;
MINIMUM_TIME_DIFFERENCE_FIRST_AND_LAST_PUFFS = 7  # minutes
# MINIMUM_INTER_PUFF_DURATION = 10 * 1000;
MINIMUM_INTER_PUFF_DURATION = 5  # seconds
MINIMUM_PUFFS_IN_EPISODE = 4;

import scikitplot as skplt
# http://scikit-plot.readthedocs.io/en/stable/estimators.html
from sklearn.metrics import confusion_matrix


def load_pickle(filename):
    with open(filename, 'rb') as handle:
        data = pickle.load(handle)
    return data


def my_plot_confution_matrix(X, Y):
    clf = RandomForestClassifier(n_jobs=2, random_state=0, n_estimators=100)

    scores = cross_val_score(clf, X, Y, cv=10, scoring='f1_macro')
    print("Cross-validation Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
    y_pred = cross_val_predict(clf, X, Y, cv=10)
    print('Precision: %.3f' % precision_score(y_true=Y, y_pred=y_pred))
    print('Recall: %.3f' % recall_score(y_true=Y, y_pred=y_pred))
    print('F1: %.3f' % f1_score(y_true=Y, y_pred=y_pred))

    plot_confusion_matrix(Y, y_pred, normalize=True)
    plt.xticks(rotation=90)
    plt.show()


def my_plot_confution_matrix_color(X, Y):
    clf = RandomForestClassifier(n_jobs=2, random_state=0, n_estimators=100)

    scores = cross_val_score(clf, X, Y, cv=10, scoring='f1_macro')
    print("Cross-validation Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
    y_pred = cross_val_predict(clf, X, Y, cv=10)
    cm = confusion_matrix(Y, y_pred)
    #     print(cm)
    # Show confusion matrix in a separate window
    plt.matshow(cm)
    plt.title('Confusion matrix')
    plt.colorbar()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()


def my_plot_learning_curve(X, Y):
    clf = RandomForestClassifier(n_jobs=2, random_state=0, n_estimators=100)
    skplt.estimators.plot_learning_curve(clf, X, Y)
    plt.xticks(rotation=90)
    plt.show()


def my_plot_feature_importances(X, Y, features):
    clf = RandomForestClassifier(n_jobs=2, random_state=0, n_estimators=100)
    clf.fit(X, Y)
    skplt.estimators.plot_feature_importances(clf, feature_names=features)
    plt.xticks(rotation=90)
    plt.show()


def process_puffmarker_wrist_level():
    #     F, X, Y, features = load_puffmarker_wrist_feature_data()
    X = load_pickle('Xs')
    Y = load_pickle('Ys')
    print(sum(Y))
    print(str(len(Y) - sum(Y)))
    # X = [v[:-4] for v in X]

    features = ['duration', 'roll_mean', 'roll_median', 'roll_sd',
                'roll_quartile', 'pitch_mean', 'pitch_median', 'pitch_sd',
                'pitch_quartile', 'yaw_mean', 'yaw_median', 'yaw_sd', 'yaw_quartile',
                'gyro_mean', 'gyro_median', 'gyro_sd', 'gyro_quartile',
                'ay_mean', 'ay_median', 'ay_sd', 'ay_quartile',
                'prev_dur', 'nxt_dur', 'prev dif', 'nxt_diff',
                'prev_aymn', 'nxt_aymn', 'prev aysd', 'nxt_aysd']
    # X = [v[:16] for v in X]
    # features = features[:16]
    my_plot_confution_matrix(X, Y)
    #     my_plot_precision_recall_curve(X, Y)
    my_plot_learning_curve(X, Y)
    my_plot_feature_importances(X, Y, features)


# Utility function to report best scores
def report(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                results['mean_test_score'][candidate],
                results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")


def search_parameter(X, y):
    # build a classifier
    clf = RandomForestClassifier(n_estimators=20)

    #
    # # specify parameters and distributions to sample from
    # param_dist = {"max_depth": [3, 5, 7, 11, 13, None],
    #               "max_features": sp_randint(1, 15),
    #               "min_samples_split": sp_randint(2, 11),
    #               "min_samples_leaf": sp_randint(1, 11),
    #               "bootstrap": [True, False],
    #               "criterion": ["gini", "entropy"]}
    #
    # # run randomized search
    # n_iter_search = 20
    # random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
    #                                    n_iter=n_iter_search)
    #
    # start = time()
    # random_search.fit(X, y)
    # print("RandomizedSearchCV took %.2f seconds for %d candidates"
    #       " parameter settings." % ((time() - start), n_iter_search))
    # report(random_search.cv_results_)

    # use a full grid over all parameters
    param_grid = {
        # 'n_estimators': [50, 100, 200, 500, 700],
        'n_estimators': [50, 100],
        'max_features': ['auto', 'sqrt', 'log2'],
        "max_depth": [3, 5, 7, 11, 13, None],
        # "max_features": [1, 3, 5, 10, 13, 15],
        "min_samples_split": [2, 3, 10],
        "min_samples_leaf": [1, 3, 10],
        "bootstrap": [True, False],
        "criterion": ["gini", "entropy"]}

    # run grid search
    scorer = make_scorer(f1_score)
    grid_search = GridSearchCV(estimator=clf, param_grid=param_grid, scoring=scorer, cv=10)
    start = time()
    gs = grid_search.fit(X, y)

    print(gs.best_score_)
    print(gs.best_params_)

    print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
          % (time() - start, len(grid_search.cv_results_['params'])))
    report(grid_search.cv_results_)


if __name__ == '__main__':
    process_puffmarker_wrist_level()
    # X = load_pickle('Xs')
    # Y = load_pickle('Ys')
    # search_parameter(X, Y)
# -------------------------------------------------------------------------------------------------------------


# # get some data
# digits = load_digits()
# X, y = digits.data, digits.target
