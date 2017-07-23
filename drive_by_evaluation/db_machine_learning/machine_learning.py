import os
from drive_by_evaluation.measurement import Measurement
from drive_by_evaluation.measure_collection import MeasureCollection
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import pickle
from drive_by_evaluation.ground_truth import GroundTruthClass
from drive_by_evaluation.multi_scorer import MultiScorer
from db_data_set import DataSet
from costcla.models import BayesMinimumRiskClassifier, CostSensitiveDecisionTreeClassifier

import random
#from costcla.datasets import load_creditscoring1
#from costcla.utils import cross_validation

def get_dataset(measure_collections, dataset=None):
    if dataset is None:
        dataset = DataSet(['FREE_SPACE', 'PARKING_CAR', 'OVERTAKING_SITUATION', 'PARKING_MC_BC'])

    for mc in measure_collections:
        features = [mc.avg_distance, mc.get_length(), mc.get_duration(), mc.get_nr_of_measures(),
                    mc.get_distance_variance(), mc.avg_speed, mc.get_acceleration(),
                    mc.first_measure().distance, mc.measures[len(mc.measures) / 2].distance,
                    mc.last_measure().distance]

        ground_truth = 'FREE_SPACE'
        gt = mc.get_probable_ground_truth()
        if GroundTruthClass.is_parking_car(gt):
            ground_truth = 'PARKING_CAR'
        elif GroundTruthClass.is_overtaking_situation(gt):
            ground_truth = 'OVERTAKING_SITUATION'
        elif GroundTruthClass.is_parking_motorcycle_or_bicycle(gt):
            ground_truth = 'PARKING_MC_BC'

        dataset.append_sample(features, ground_truth)

    return dataset


def get_overtaking_situation_dataset(measure_collections, dataset=None):
    if dataset is None:
        dataset = DataSet(['NO_OVERTAKING_SITUATION', 'OVERTAKING_SITUATION'])

    for mc in measure_collections:
        if mc.get_length() > 1.0:
            features = [mc.avg_distance, mc.get_length(), mc.get_duration(), mc.get_nr_of_measures(),
                        mc.get_distance_variance(), mc.avg_speed, mc.get_acceleration(),
                        mc.first_measure().distance, mc.measures[len(mc.measures) / 2].distance,
                        mc.last_measure().distance]

            ground_truth = 'NO_OVERTAKING_SITUATION'
            gt = mc.get_probable_ground_truth()
            if GroundTruthClass.is_overtaking_situation(gt):
                ground_truth = 'OVERTAKING_SITUATION'

            # undersampling
            if not GroundTruthClass.is_overtaking_situation(gt) and random.randint(0, 10) < 10:
                dataset.append_sample(features, ground_truth)
            elif GroundTruthClass.is_overtaking_situation(gt):
                #i = 0
                #while i < 1000:
                dataset.append_sample(features, ground_truth)
                    #i += 1

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


if __name__ == '__main__':
    base_path = 'C:\\sw\\master\\collected data\\'
    # ml_file_path = 'C:\\sw\\master\\00ml.arff'
    ml_file_path = 'C:\\sw\\master\\20170718ml.arff'

    dataset = None
    #write_to_file(base_path, ml_file_path)
    measure_collections_dir = MeasureCollection.read_directory(base_path)
    for file_name, measure_collection in measure_collections_dir.iteritems():
        print file_name
        #MeasureCollection.write_arff_file(measure_collections1, ml_file_path)
        dataset = get_dataset(measure_collection, dataset=dataset)

    classifiers = {'mlp': MLPClassifier(), 'tree': DecisionTreeClassifier(), 'knn': KNeighborsClassifier(3),
                   'svc': SVC(), 'gaussian': GaussianProcessClassifier(), 'rbf': RBF(),
                   'randomforest': RandomForestClassifier()}
    for name, clf in classifiers.iteritems():
        scorer = MultiScorer({
            'Accuracy': (accuracy_score, {}),
            'Precision': (precision_score, {'average': 'weighted'}),
            'Recall': (recall_score, {'average': 'weighted'}),
            'ConfusionMatrix': (confusion_matrix, {'labels': dataset.class_labels})
        })
        print name

        # X_train, X_test, y_train, y_test = train_test_split(dataset.x, dataset.y_true, test_size=0.33, random_state=42)
        # clf.fit(X_train, y_train)
        # print 'fitted'
        # i = 0
        # mismatches = []
        # while i < len(X_test[0]):
        #      predicted = clf.predict(np.array(X_test), [[1, 15], [15, 0]])
        #                              #.reshape(1, -1))
        #      #print predicted[0]
        #      #print dataset_test[1][i]
        #      if predicted[0] != y_test[i]:
        #           print 'features: ', X_test
        #           print 'GroundTruth: ', y_test
        #           print 'Predicted: ', predicted[0]
        #           print ''
        #           mismatches.append((X_test, y_test, predicted[0]))
        #      i += 1
        # print len(mismatches)
        #
        # continue
        cross_val_score(clf, dataset.x, dataset.y_true, cv=10, scoring=scorer)
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
