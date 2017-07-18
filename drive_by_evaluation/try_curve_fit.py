import os
from measurement import Measurement
from measure_collection import MeasureCollection
from scipy.optimize import curve_fit


def fit_func(x, a, b, c):
    return a*x*x + b*x + c

measurements1 = Measurement.read('C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074500_002138.dat',
                                     'C:\\sw\\master\\collected data\\data_20170718\\raw_20170718_074500_002138.dat_images_Camera\\00gt1500400602.86.dat')
measure_collections1 = MeasureCollection.create_measure_collections(measurements1)

cars = [mc for mc in measure_collections1 if mc.get_probable_ground_truth() == 'OCCUPIED_PARKING_SPACE']

params = curve_fit(fit_func, [m.timestamp for m in cars[0].measures], [m.distance for m in cars[0].measures])
print params[0]