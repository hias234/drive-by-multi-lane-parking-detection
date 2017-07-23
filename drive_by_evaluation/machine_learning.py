import os
from measurement import Measurement
from measure_collection import MeasureCollection
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import pickle
from ground_truth import GroundTruthClass
from multi_scorer import MultiScorer


class DataSet:
    def __init__(self, class_labels):
        self.x = []
        self.y_true = []
        self.class_labels = class_labels

    def append_sample(self, x, y_true):
        self.x.append(x)
        self.y_true.append(y_true)

def get_dataset(measure_collections, dataset=None):
    if dataset is None:
        dataset = ([], [])

    for mc in measure_collections:
        dataset[0].append([mc.avg_distance, mc.get_length(), mc.get_duration(), mc.get_nr_of_measures(),
                           mc.get_distance_variance(), mc.avg_speed, mc.get_acceleration(),
                           mc.first_measure().distance, mc.measures[len(mc.measures) / 2].distance,
                           mc.last_measure().distance])

        ground_truth = 'FREE_SPACE'
        gt = mc.get_probable_ground_truth()
        if GroundTruthClass.is_parking_car(gt):
            ground_truth = 'PARKING_CAR'
        elif GroundTruthClass.is_overtaking_situation(gt):
            ground_truth = 'OVERTAKING_SITUATION'
        elif GroundTruthClass.is_parking_motorcycle_or_bicycle(gt):
            ground_truth = 'PARKING_MC_BC'

        dataset[1].append(ground_truth)

    return dataset


def get_overtaking_situation_dataset(measure_collections, dataset=None):
    if dataset is None:
        dataset = ([], [])

    for mc in measure_collections:
        dataset[0].append([mc.avg_distance, mc.get_length(), mc.get_duration(), mc.get_nr_of_measures(),
                           mc.get_distance_variance(), mc.avg_speed, mc.get_acceleration(),
                           mc.first_measure().distance, mc.measures[len(mc.measures) / 2].distance,
                           mc.last_measure().distance])

        ground_truth = 'NO_OVERTAKING_SITUATION'
        gt = mc.get_probable_ground_truth()
        if GroundTruthClass.is_overtaking_situation(gt):
            ground_truth = 'OVERTAKING_SITUATION'

        dataset[1].append(ground_truth)

    return dataset


def write_to_file(base_path, ml_file_path):
    files = sorted([f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))])

    for f in files:
        data_file = os.path.join(base_path, f)
        camera_folder = os.path.join(base_path, f) + '_images_Camera\\'
        gt_files = [gt_f for gt_f in os.listdir(camera_folder) if gt_f.startswith('00gt')]
        if (len(gt_files) > 0):
            print gt_files[0]
            measurements1 = Measurement.read(data_file, os.path.join(camera_folder, gt_files[0]))
            measure_collections1 = MeasureCollection.create_measure_collections(measurements1)
            MeasureCollection.write_arff_file(measure_collections1, ml_file_path)


def recall_class(y_true, y_pred, clazz='PARKING_CAR', average='macro'):
    i = 0
    while i < y_true.shape[0]:
        if y_true[i] != clazz:
            np.delete(y_true, i)
            np.delete(y_pred, i)
        else:
            i += 1
    return recall_score(y_true, y_pred, average=average)

if __name__ == '__main__':
    base_path = 'C:\\sw\\master\\collected data\\'
    # ml_file_path = 'C:\\sw\\master\\00ml.arff'
    ml_file_path = 'C:\\sw\\master\\20170718ml.arff'



    dataset_train = None
    dataset_test = None
    i = 0.0
    #write_to_file(base_path, ml_file_path)
    measure_collections_dir = MeasureCollection.read_directory(base_path)
    for file_name, measure_collection in measure_collections_dir.iteritems():
        print file_name
        #MeasureCollection.write_arff_file(measure_collections1, ml_file_path)
        if i / len(measure_collections_dir) < 0.8:
            dataset_train = get_dataset(measure_collection, dataset=dataset_train)
        else:
            dataset_test = get_dataset(measure_collection, dataset=dataset_test)
        i += 1

    clf = RandomForestClassifier()
    # clf.fit(dataset_train[0], dataset_train[1])
    # print 'fitted'
    # i = 0
    # mismatches = []
    # while i < len(dataset_test[0]):
    #     predicted = clf.predict(np.array(dataset_test[0][i]).reshape(1, -1))
    #     #print predicted[0]
    #     #print dataset_test[1][i]
    #     if predicted[0] != dataset_test[1][i]:
    #         print 'features: ', dataset_test[0][i]
    #         print 'GroundTruth: ', dataset_test[1][i]
    #         print 'Predicted: ', predicted[0]
    #         print ''
    #         mismatches.append((dataset_test[0][i], dataset_test[1][i], predicted[0]))
    #     i += 1
    #
    # print len(mismatches)

    scorer = MultiScorer({
        'Accuracy': (accuracy_score, {}),
        'Precision': (precision_score, {'average': 'weighted'}),
        'Recall': (recall_score, {'average': 'weighted'}),
        'ConfusionMatrix': (confusion_matrix, {'labels': ['FREE_SPACE', 'PARKING_CAR', 'OVERTAKING_SITUATION', 'PARKING_MC_BC']})
    })

    dataset = (dataset_train[0], dataset_train[1])
    dataset[0].extend(dataset_test[0])
    dataset[1].extend(dataset_test[1])
    cross_val_score(clf, dataset[0], dataset[1], cv=10, scoring=scorer)
    results = scorer.get_results()

    confusion_m = None
    for metric_name in results.keys():
        if metric_name == 'ConfusionMatrix':
            print metric_name
            confusion_m = np.sum(results[metric_name], axis=0)
            print confusion_m
        else:
            print metric_name, np.average(results[metric_name])

    true_pos = np.array(np.diag(confusion_m), dtype=float)
    false_pos = np.sum(confusion_m, axis=0) - true_pos
    false_neg = np.sum(confusion_m, axis=1) - true_pos

    precision = (true_pos / (true_pos + false_pos))
    print 'Precision: ', precision
    recall = (true_pos / (true_pos + false_neg))
    print 'Recall: ', recall

# measurements1 = Measurement.read('C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074500_002138.dat',
#                                     'C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074500_002138.dat_images_Camera\\00gt1500400602.86.dat')
# measure_collections1 = MeasureCollection.create_measure_collections(measurements1)
# MeasureCollection.write_arff_file(measure_collections1, 'C:\\sw\\master\\00ml.arff')
#
# measurements2 = Measurement.read('C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074348_696382.dat',
#                                 'C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074348_696382.dat_images_Camera\\00gt1500398878.87.dat')
# measure_collections2 = MeasureCollection.create_measure_collections(measurements2)
# MeasureCollection.write_arff_file(measure_collections2, 'C:\\sw\\master\\00ml.arff')
#
# measurements2 = Measurement.read('C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074705_730731.dat',
#                                 'C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074705_730731.dat_images_Camera\\00gt1500403346.39.dat')
# measure_collections2 = MeasureCollection.create_measure_collections(measurements2)
# MeasureCollection.write_arff_file(measure_collections2, 'C:\\sw\\master\\00ml.arff')