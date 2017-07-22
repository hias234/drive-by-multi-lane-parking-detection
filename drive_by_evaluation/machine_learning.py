import os
from measurement import Measurement
from measure_collection import MeasureCollection
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import pickle
from ground_truth import GroundTruthClass


def get_dataset(measure_collections, dataset=None):
    if dataset is None:
        dataset = ([], [])

    for mc in measure_collections:
        dataset[0].append([mc.avg_distance, mc.get_length(), mc.get_duration(), mc.get_nr_of_measures(),
                           mc.get_distance_variance(), mc.avg_speed,
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
    base_path = 'C:\\sw\\master\\collected data\\data_20170720_donau_traffic_jam_per\\'
    # ml_file_path = 'C:\\sw\\master\\00ml.arff'
    ml_file_path = 'C:\\sw\\master\\20170720ml.arff'



    dataset_train = None
    dataset_test = None
    i = 0.0
    files = sorted([f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))])
    #write_to_file(base_path, ml_file_path)
    for f in files:
        data_file = os.path.join(base_path, f)
        camera_folder = os.path.join(base_path, f) + '_images_Camera\\'
        gt_files = [gt_f for gt_f in os.listdir(camera_folder) if gt_f.startswith('00gt')]
        if (len(gt_files) > 0):
            print gt_files[0]
            measurements1 = Measurement.read(data_file, os.path.join(camera_folder, gt_files[0]))
            measure_collections1 = MeasureCollection.create_measure_collections(measurements1)
            #MeasureCollection.write_arff_file(measure_collections1, ml_file_path)
            if (i / len(files) < 0.7):
                dataset_train = get_dataset(measure_collections1, dataset=dataset_train)
            else:
                dataset_test = get_dataset(measure_collections1, dataset=dataset_test)
            i += 1

    clf = RandomForestClassifier()
    clf.fit(dataset_train[0], dataset_train[1])
    print 'fitted'
    i = 0
    while i < len(dataset_test[0]):
        predicted = clf.predict(np.array(dataset_test[0][i]).reshape(1, -1))
        #print predicted[0]
        #print dataset_test[1][i]
        if predicted[0] != dataset_test[1][i]:
            print 'mismatch'
            print dataset_test[0][i]
            print dataset_test[1][i]
            print predicted
        i += 1
    print cross_val_score(clf, dataset_train[0], dataset_train[1], cv=5)

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