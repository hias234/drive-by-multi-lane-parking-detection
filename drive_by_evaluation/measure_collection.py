
import os
from geopy.distance import vincenty
import csv

from measurement import Measurement
from ground_truth import GroundTruth, GroundTruthClass


class MeasureCollection:
    def __init__(self):
        self.measures = []
        self.sum_distance = 0.0
        self.avg_distance = 0.0
        self.sum_speed = 0.0
        self.avg_speed = 0.0
        self.length = 0.0
        self.center_latitude = 0.0
        self.center_longitude = 0.0
        self.variance = -1.0

    def get_probable_ground_truth(self):
        ratio_threshold = 0.6

        nr_of_gt_measures = {}
        for measure in self.measures:
            cur_number = nr_of_gt_measures.get(measure.ground_truth.ground_truth_class.name)
            if cur_number is None:
                cur_number = 1.0
            else:
                cur_number += 1.0
            nr_of_gt_measures[measure.ground_truth.ground_truth_class.name] = cur_number

        if self.get_length() > 1.5 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.PARALLEL_PARKING_CAR.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.PARALLEL_PARKING_CAR.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.PARALLEL_PARKING_CAR
        if self.get_length() > 1.0 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.PERPENDICULAR_PARKING_CAR.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.PERPENDICULAR_PARKING_CAR.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.PERPENDICULAR_PARKING_CAR
        if self.get_length() > 1.0 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.OTHER_PARKING_CAR.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.OTHER_PARKING_CAR.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.OTHER_PARKING_CAR

        if self.get_length() > 1.0 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.OVERTAKEN_CAR.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.OVERTAKEN_CAR.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.OVERTAKEN_CAR
        if self.get_length() > 1.0 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.OVERTAKEN_BICYCLE.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.OVERTAKEN_BICYCLE.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.OVERTAKEN_BICYCLE
        if self.get_length() > 1.0 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.OVERTAKEN_MOTORCYCLE.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.OVERTAKEN_MOTORCYCLE.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.OVERTAKEN_MOTORCYCLE

        if self.get_length() > 0.1 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.PARKING_BICYCLE.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.PARKING_BICYCLE.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.PARKING_BICYCLE

        if self.get_length() > 0.1 and self.avg_distance > 0.05 and \
                        nr_of_gt_measures.get(GroundTruthClass.PARKING_MOTORCYCLE.name) is not None and \
                        (nr_of_gt_measures[GroundTruthClass.PARKING_MOTORCYCLE.name] / len(self.measures)) > ratio_threshold:
            return GroundTruthClass.PARKING_MOTORCYCLE

        return GroundTruthClass.FREE_SPACE

    def is_empty(self):
        return len(self.measures) == 0

    def first_measure(self):
        return self.measures[0]

    def last_measure(self):
        return self.measures[len(self.measures) - 1]

    def add_measure_collection(self, measure_collection):
        for measure in measure_collection.measures:
            self.add_measure(measure)

    def add_measure(self, measure):
        self.measures.append(measure)

        self.sum_distance += measure.distance
        self.avg_distance = self.sum_distance / len(self.measures)
        self.sum_speed += measure.speed
        self.avg_speed = self.sum_speed / len(self.measures)
        self.length = self.get_length()
        self.variance = -1

        first_measure = self.measures[0]
        last_measure = self.measures[len(self.measures) - 1]

        self.center_longitude = (first_measure.longitude + last_measure.longitude) / 2
        self.center_latitude = (first_measure.latitude + last_measure.latitude) / 2

    def get_length(self):
        # length = 0.0
        # if len(self.measures) > 0:
        #     last_measure = self.measures[0]
        #     for i in range(1, len(self.measures)):
        #         length += vincenty(
        #                     (self.measures[i].latitude, self.measures[i].longitude),
        #                     (last_measure.latitude, last_measure.longitude)
        #                 ).meters
        #         last_measure = self.measures[i]
        #
        # return length
        #print self.first_measure().latitude, self.first_measure().longitude, self.last_measure().latitude, self.last_measure().longitude
        return vincenty((self.first_measure().latitude, self.first_measure().longitude),
                        (self.last_measure().latitude, self.last_measure().longitude)).meters

    def get_nr_of_measures(self):
        return len(self.measures)

    def get_acceleration(self):
        if self.last_measure().timestamp == self.first_measure().timestamp:
            return 0
        return ((self.last_measure().speed - self.first_measure().speed) /
                (self.last_measure().timestamp - self.first_measure().timestamp))

    def get_distance_variance(self):
        if self.variance != -1.0:
            return self.variance

        sum_top = 0
        for measure in self.measures:
            sum_top = (measure.distance - self.avg_distance)**2

        return sum_top / len(self.measures)

    def get_duration(self):
        return self.last_measure().timestamp - self.first_measure().timestamp

    @staticmethod
    def create_measure_collections(measurements):
        separation_threshold = 0.9
        min_measure_count = 1

        plateaus = []
        cur_plateau = MeasureCollection()
        last_plateau_distance = None
        last_plateau_timestamp = None
        for measure in measurements:
            if cur_plateau.is_empty() or \
                    (abs(last_plateau_distance - measure.distance) < separation_threshold and
                     abs(last_plateau_timestamp - measure.timestamp) < 1.0):
                cur_plateau.add_measure(measure)
            else:
                if len(cur_plateau.measures) >= min_measure_count:
                    plateaus.append(cur_plateau)
                cur_plateau = MeasureCollection()
                cur_plateau.add_measure(measure)
            last_plateau_distance = measure.distance
            last_plateau_timestamp = measure.timestamp

        if len(cur_plateau.measures) > min_measure_count:
            plateaus.append(cur_plateau)

        print 'found plateaus', len(plateaus)

        plateaus = MeasureCollection.merge_measure_collections(plateaus)

        return plateaus

    @staticmethod
    def merge_measure_collections(measure_collections):
        if len(measure_collections) > 0:
            i = 1
            last_length = measure_collections[0].get_length()
            last_distance = measure_collections[0].avg_distance
            if last_distance <= 0.02:
                last_distance = 100
            while i < len(measure_collections):
                length = measure_collections[i].get_length()
                distance = measure_collections[i].avg_distance
                if distance <= 0.02:
                    distance = 100
                if (
                    #(last_length < 0.2 and length < 0.2) or
                    (distance > 10 and last_distance > 10)
                ):
                    measure_collections[i - 1].add_measure_collection(measure_collections[i])
                    measure_collections.pop(i)
                else:
                    last_length = length
                    last_distance = distance
                    i += 1

            print 'merged plateaus', len(measure_collections)

        return measure_collections

    @staticmethod
    def write_to_file(path, measure_collections):
        with open(path, 'a') as file_to_write:
            csv_writer = csv.writer(file_to_write)
            cur_id = 0
            for measure_collection in measure_collections:
                for measure in measure_collection.measures:
                    csv_writer.writerow([cur_id, measure.distance, measure.timestamp, measure.latitude, measure.longitude,
                                         measure.ground_truth.is_parking_car, measure.ground_truth.is_overtaken_car])
                cur_id += 1

    @staticmethod
    def read_from_file(path):
        with open(path, 'r') as file_to_read_from:
            csv_reader = csv.reader(file_to_read_from, delimiter=',')
            measure_collections = []
            last_id = None
            measure_collection = None
            for row in csv_reader:
                if len(row) > 0:
                    cur_id = row[0]
                    if last_id is None or last_id != cur_id:
                        if measure_collection is not None:
                            measure_collections.append(measure_collection)
                        measure_collection = MeasureCollection()

                    measure_collection.add_measure(Measurement(float(row[1]), float(row[2]), float(row[3]), float(row[4]),
                                                               GroundTruth(float(row[2]), row[5] == 'True',
                                                                           row[6] == 'True')))
                    last_id = cur_id

        return measure_collections

    def is_maybe_parking_car(self):
        return self.get_length() > 0.7 and self.avg_speed > 0.5 and \
               self.avg_distance > 0.1

    @staticmethod
    def write_arff_file(measure_collections, path):
        write_header = not os.path.exists(path)
        is_arff_file = path.endswith('.arff')

        with open(path, 'a') as arff_file:
            if write_header and is_arff_file:
                arff_file.write("@RELATION driveby\n")
                arff_file.write("@ATTRIBUTE avg_distance NUMERIC\n")
                arff_file.write("@ATTRIBUTE length NUMERIC\n")
                arff_file.write("@ATTRIBUTE duration_s NUMERIC\n")
                arff_file.write("@ATTRIBUTE nr_of_measures NUMERIC\n")
                arff_file.write("@ATTRIBUTE distance_variance NUMERIC\n")
                arff_file.write("@ATTRIBUTE avg_speed NUMERIC\n")
                arff_file.write("@ATTRIBUTE class {NO_PARKING, OCCUPIED_PARKING_SPACE, OVERTAKEN_CAR}\n")
                arff_file.write("\n\n\n")
                arff_file.write("@DATA\n")

            for measure_collection in measure_collections:
                if measure_collection.is_maybe_parking_car():
                    arff_file.write(str(measure_collection.avg_distance))
                    arff_file.write(",")
                    arff_file.write(str(measure_collection.get_length()))
                    arff_file.write(",")
                    arff_file.write(str(measure_collection.get_duration()))
                    arff_file.write(",")
                    arff_file.write(str(measure_collection.get_nr_of_measures()))
                    arff_file.write(",")
                    arff_file.write(str(measure_collection.get_distance_variance()))
                    arff_file.write(",")
                    arff_file.write(str(measure_collection.avg_speed))
                    arff_file.write(",")
                    arff_file.write(measure_collection.get_probable_ground_truth().name)
                    arff_file.write("\n")

    @staticmethod
    def read_directory(base_path):
        measure_collections = {}

        for f in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, f)) and not f.endswith('_images_Camera'):
                sub_dir_measure_collections = MeasureCollection.read_directory(os.path.join(base_path, f))
                measure_collections.update(sub_dir_measure_collections)
            elif os.path.isfile(os.path.join(base_path, f)) and f.endswith('.dat'):
                data_file = os.path.join(base_path, f)
                camera_folder = data_file + '_images_Camera\\'
                gt_files = [gt_f for gt_f in os.listdir(camera_folder) if gt_f.startswith('00gt')]
                if len(gt_files) > 0:
                    measurements = Measurement.read(data_file, os.path.join(camera_folder, gt_files[0]))
                    measure_collections_f = MeasureCollection.create_measure_collections(measurements)
                    measure_collections[data_file] = measure_collections_f

        return measure_collections
