
from geopy.distance import vincenty
import csv

from measurement import Measurement
from ground_truth import GroundTruth


class MeasureCollection:
    def __init__(self):
        self.measures = []
        self.sum_distance = 0
        self.avg_distance = 0
        self.length = 0
        self.center_latitude = 0
        self.center_longitude = 0
        self.variance = -1.0

    def get_probable_ground_truth(self):
        nr_of_gt_measures = {'NO_PARKING': 0.0, 'PARKING_CAR': 0.0, 'OVERTAKEN_CAR': 0.0}
        for measure in self.measures:
            if measure.ground_truth.is_parking_car:
                nr_of_gt_measures['PARKING_CAR'] += 1
            elif measure.ground_truth.is_overtaken_car:
                nr_of_gt_measures['OVERTAKEN_CAR'] += 1
            else:
                nr_of_gt_measures['NO_PARKING'] += 1

        if self.get_length() > 0.5 and (nr_of_gt_measures['PARKING_CAR'] / len(self.measures)) > 0.7:
            return 'OCCUPIED_PARKING_SPACE'
        if self.get_length() > 0.5 and (nr_of_gt_measures['OVERTAKEN_CAR'] / len(self.measures)) > 0.7:
            return 'OVERTAKEN_CAR'
        return 'NO_PARKING'

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
        self.length = self.get_length()
        self.variance = -1

        first_measure = self.measures[0]
        last_measure = self.measures[len(self.measures) - 1]

        self.center_longitude = (first_measure.longitude + last_measure.longitude) / 2
        self.center_latitude = (first_measure.latitude + last_measure.latitude) / 2

    def get_length(self):
        length = 0.0
        if len(self.measures) > 0:
            last_measure = self.measures[0]
            for i in range(1, len(self.measures)):
                length += vincenty(
                            (self.measures[i].latitude, self.measures[i].longitude),
                            (last_measure.latitude, last_measure.longitude)
                        ).meters
                last_measure = self.measures[i]

        return length

    def get_distance_variance(self):
        if self.variance != -1.0:
            return self.variance

        sum_top = 0
        for measure in self.measures:
            sum_top = (measure.distance - self.avg_distance)**2

        return sum_top / len(self.measures)

    @staticmethod
    def create_measure_collections(measurements):
        abs_to_avg_distance_threshold = 90

        plateaus = []
        cur_plateau = MeasureCollection()
        last_plateau_distance = None
        for measure in measurements:
            if cur_plateau.is_empty() or abs(last_plateau_distance - measure.distance) < abs_to_avg_distance_threshold:
                cur_plateau.add_measure(measure)
            else:
                if len(cur_plateau.measures) > 0:
                    plateaus.append(cur_plateau)
                cur_plateau = MeasureCollection()
                cur_plateau.add_measure(measure)
            last_plateau_distance = measure.distance

        if len(cur_plateau.measures) > 0:
            plateaus.append(cur_plateau)

        print 'found plateaus', len(plateaus)

        #plateaus = self.merge_plateaus(plateaus)

        return plateaus

    @staticmethod
    def merge_plateaus(plateaus):
        threshold_distance_between_ends = 50

        i = 1
        while i < len(plateaus):
            distance_between_ends = abs(plateaus[i-1].last_measure().distance - plateaus[i].first_measure().distance)
            # print distance_between_ends
            if distance_between_ends <= threshold_distance_between_ends:
                plateaus[i-1].add_measure_collection(plateaus[i])
                plateaus.pop(i)
            else:
                i += 1

        print 'merged plateaus', len(plateaus)

        return plateaus

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
