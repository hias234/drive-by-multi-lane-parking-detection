import csv
import os
import time

import kivy
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput

kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.button import Button
from kivy.core.window import Window

from datetime import datetime

from drive_by_evaluation.ground_truth import GroundTruth, GroundTruthClass
from drive_by_evaluation.measure_collection import MeasureCollection
from drive_by_evaluation.measurement import Measurement


class VisualizationAppStarter(App):

    def __init__(self, **kwargs):
        super(VisualizationAppStarter, self).__init__(**kwargs)

        self.fileChooser = TextInput()
        self.submit = Button(text='Start Visualization')
        self.submit.bind(on_press=self.on_submit)

    def build(self):
        layout = BoxLayout(orientation='vertical')
        # Window.size = (500, 100)
        layout.add_widget(self.fileChooser)
        layout.add_widget(self.submit)

        return layout

    def on_submit(self, instance):
        App.get_running_app().stop()
        VisualizationApp(self.fileChooser.text).run()


class VisualizationApp(App):

    def __init__(self, data_file, **kwargs):
        super(VisualizationApp, self).__init__(**kwargs)

        self.data_file = data_file
        self.camera_folder = data_file + '_images_Camera\\'
        self.camera_files = sorted([os.path.join(self.camera_folder, f) for f in os.listdir(self.camera_folder)
                                    if os.path.isfile(os.path.join(self.camera_folder, f)) and f.endswith('.jpg')])
        self.ground_truth_file = [os.path.join(self.camera_folder, f) for f in os.listdir(self.camera_folder)
                                  if os.path.isfile(os.path.join(self.camera_folder, f)) and f.startswith('00gt')][0]
        #print self.camera_files

        options = {
            'mc_min_speed': 4.0, 'mc_merge': True,
            'mc_separation_threshold': 1.0, 'mc_min_measure_count': 2,
            # 'mc_surrounding_times_s': [10.0],
            # 'mc_surrounding_m': [50.0, 100.0],
            'outlier_threshold_distance': 1.0, 'outlier_threshold_diff': 0.5,
            '1cm_replacement_value': 10.01
        }

        measurements = Measurement.read(data_file, self.ground_truth_file, options=options)
        self.measure_collections_f = MeasureCollection.create_measure_collections(measurements, options=options)

        self.cur_index = 0

        self.image = Image(source=self.camera_files[0], size=(352, 288), pos=(0, 0))
        with self.image.canvas as canvas:
            Color(1., 0, 0)
            Rectangle(pos=(400, 100), size=(1, 400))

        Clock.schedule_interval(self.show_next_image, 0.1)

    def build(self):
        layout = FloatLayout(size=(300, 300))
        # Window.size = (1000, 700)
        layout.add_widget(self.image)

        return layout

    def show_next_image(self, dt):
        self.cur_index += 1
        self.image.source = self.camera_files[self.cur_index]


if __name__ == '__main__':
    VisualizationAppStarter().run()
