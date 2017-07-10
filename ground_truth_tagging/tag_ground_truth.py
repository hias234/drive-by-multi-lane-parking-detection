
import os
import time
import kivy
import csv
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Color
from kivy.graphics import Rectangle
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window

from datetime import datetime


class GroundTruth:
    def __init__(self, timestamp, is_parking_car, is_overtaken_car):
        self.timestamp = timestamp
        self.is_parking_car = is_parking_car
        self.is_overtaken_car = is_overtaken_car


class GroundTruthTaggingApp(App):

    def __init__(self, **kwargs):
        super(GroundTruthTaggingApp, self).__init__(**kwargs)

        self.ground_truth = []

        self.base_path = 'C:\\sw\\master\\collected data\\data\\raw_20170705_065613_869794.dat_images_Camera\\'
        self.files = sorted([f for f in os.listdir(self.base_path) if os.path.isfile(os.path.join(self.base_path, f))])
        print self.files

        self.cur_index = 0

        self.image = Image(source=os.path.join(self.base_path, self.files[0]), size=(352, 288), pos=(0, 0))
        with self.image.canvas as canvas:
            Color(1., 0, 0)
            Rectangle(pos=(400, 100), size=(1, 400))

        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .1), pos=(0, 0))
        self.bt_previous = Button(text='<')
        self.bt_previous.bind(on_press=self.on_prev_clicked)
        self.bt_start_here = Button(text='Start from here [b]')
        self.bt_start_here.bind(on_press=self.on_start_here)
        self.bt_parking_car = Button(text='Parking Car [p]')
        self.bt_parking_car.bind(on_press=self.on_parking_car_clicked)
        self.bt_overtaken_car = Button(text='Overtaken Car [o]')
        self.bt_overtaken_car.bind(on_press=self.on_overtaken_car_clicked)
        self.bt_no_parking_space = Button(text='No Parking Car [n]')
        self.bt_stop_here = Button(text='Stop Here and Save [e]')
        self.bt_stop_here.bind(on_press=self.on_stop_here)
        self.bt_next = Button(text='>')
        self.bt_next.bind(on_press=self.on_next_clicked)
        self.button_layout.add_widget(self.bt_previous)
        self.button_layout.add_widget(self.bt_start_here)
        self.button_layout.add_widget(self.bt_next)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.started_index = None

    def build(self):
        layout = FloatLayout(size=(300, 300))
        layout.add_widget(self.image)
        layout.add_widget(self.button_layout)

        return layout

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'right' and self.started_index is None:
            self.on_next_clicked(None)
        elif keycode[1] == 'left':
            self.on_prev_clicked(None)
        elif keycode[1] == 'b' and self.started_index is None:
            self.on_start_here(None)
        elif keycode[1] == 'p' and self.started_index is not None:
            self.on_parking_car_clicked(None)
        elif keycode[1] == 'n' and self.started_index is not None:
            self.on_no_car_clicked(None)
        elif keycode[1] == 'o' and self.started_index is not None:
            self.on_overtaken_car_clicked(None)
        elif keycode[1] == 'e' and self.started_index is not None:
            self.on_stop_here(None)
        return True

    def on_parking_car_clicked(self, instance):
        timestamp = self.get_timestamp(self.cur_index)

        gt = GroundTruth(timestamp, True, False)
        self.add_ground_truth(gt)
        self.on_next_clicked('')

    def on_overtaken_car_clicked(self, instance):
        timestamp = self.get_timestamp(self.cur_index)

        gt = GroundTruth(timestamp, False, True)
        self.add_ground_truth(gt)
        self.on_next_clicked('')

    def on_no_car_clicked(self, instance):
        timestamp = self.get_timestamp(self.cur_index)

        gt = GroundTruth(timestamp, False, False)
        self.add_ground_truth(gt)
        self.on_next_clicked('')

    def get_timestamp(self, index):
        f = self.files[index]
        dt = datetime.strptime(f.split('.')[0], '%Y%m%d_%H%M%S_%f')
        return (dt - datetime(1970, 1, 1)).total_seconds()

    def add_ground_truth(self, gt):
        index = self.cur_index - self.started_index
        if index >= len(self.ground_truth):
            self.ground_truth.append(gt)
        else:
            self.ground_truth[index] = gt

    def on_next_clicked(self, instance):
        if self.cur_index + 1 < len(self.files):
            self.cur_index += 1
            self.image.source = os.path.join(self.base_path, self.files[self.cur_index])
        else:
            self.on_stop_here(None)

    def on_prev_clicked(self, instance):
        if self.cur_index > 0 and (self.started_index is None or self.cur_index > self.started_index):
            self.cur_index -= 1
            self.image.source = os.path.join(self.base_path, self.files[self.cur_index])

    def on_start_here(self, instance):
        self.button_layout.clear_widgets()
        self.button_layout.add_widget(self.bt_previous)
        self.button_layout.add_widget(self.bt_parking_car)
        self.button_layout.add_widget(self.bt_no_parking_space)
        self.button_layout.add_widget(self.bt_overtaken_car)
        self.button_layout.add_widget(self.bt_stop_here)
        self.started_index = self.cur_index

    def on_stop_here(self, instance):
        with open(os.path.join(self.base_path, '00gt' + str(time.time()) + '.dat'), 'a') as out:
            csv_out = csv.writer(out)

            for gt in self.ground_truth:
                print gt.timestamp, gt.is_parking_car, gt.is_overtaken_car
                csv_out.writerow([gt.timestamp, gt.is_parking_car, gt.is_overtaken_car])

if __name__ == '__main__':
    GroundTruthTaggingApp().run()
