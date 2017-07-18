import os
from measurement import Measurement
from measure_collection import MeasureCollection

base_path = 'C:\\sw\\master\\collected data\\data_20170718\\'
files = sorted([f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))])

for f in files:
    data_file = os.path.join(base_path, f)
    camera_folder = os.path.join(base_path, f) + '_images_Camera\\'
    gt_files = [gt_f for gt_f in os.listdir(camera_folder) if gt_f.startswith('00gt')]
    if (len(gt_files) > 0):
        print gt_files[0]
        measurements1 = Measurement.read(data_file, os.path.join(camera_folder, gt_files[0]))
        measure_collections1 = MeasureCollection.create_measure_collections(measurements1)
        MeasureCollection.write_arff_file(measure_collections1, 'C:\\sw\\master\\00ml_curve.arff')

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