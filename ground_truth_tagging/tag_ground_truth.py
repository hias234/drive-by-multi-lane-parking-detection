
import os
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from datetime import datetime


class ButtonsComponent(GridLayout):
    def __init__(self, **kwargs):
        super(ButtonsComponent, self).__init__(**kwargs)
        self.cols = 5
        self.bt_previous = Button(text='<')
        self.bt_occupied_parking_space = Button(text='Occupied Parking Space')
        self.bt_vacant_parking_space = Button(text='Vacant Parking Space')
        self.bt_no_parking_space = Button(text='No Parking Space')
        self.bt_no_parking_space = Button(text='No Parking Space')
        self.bt_next = Button(text='>')
        self.add_widget(self.bt_previous)
        self.add_widget(self.bt_occupied_parking_space)
        self.add_widget(self.bt_vacant_parking_space)
        self.add_widget(self.bt_no_parking_space)
        self.add_widget(self.bt_next)

class GroundTruth:
    def __init__(self, timestamp, is_parking_car, is_overtaken_car):
        self.timestamp = timestamp

class GroundTruthTaggingApp(App):

    def build(self):
        layout = FloatLayout(size=(300, 300))

        self.ground_truth = []

        self.base_path = 'C:\\sw\\master\\collected data\\data\\raw_20170704_191952_111273.dat_images_Camera\\'
        self.files = [f for f in os.listdir(self.base_path) if os.path.isfile(os.path.join(self.base_path, f))]
        print self.files

        self.cur_index = 0

        self.image = Image(source=os.path.join(self.base_path, self.files[0]), size_hint=(.7, .7), pos=(150, 250))

        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .1), pos=(0, 0))
        self.bt_previous = Button(text='<')
        self.bt_previous.bind(on_press=self.on_prev_clicked)
        self.bt_start_here = Button(text='Start from here')
        self.bt_start_here.bind(on_press=self.on_start_here)
        self.bt_parking_car = Button(text='Parking Car')
        self.bt_parking_car.bind(on_press=self.on_parking_car_clicked)
        self.bt_vacant_parking_space = Button(text='Vacant Parking Space')
        self.bt_no_parking_space = Button(text='No Parking Space')
        self.bt_stop_here = Button(text='Stop Here')
        self.bt_next = Button(text='>')
        self.bt_next.bind(on_press=self.on_next_clicked)
        self.button_layout.add_widget(self.bt_start_here)
        self.button_layout.add_widget(self.bt_next)

        layout.add_widget(self.image)
        layout.add_widget(self.button_layout)

        return layout

    def on_parking_car_clicked(self, instance):
        timestamp = self.get_timestamp(self.cur_index)

        gt = GroundTruth(timestamp, True, False)
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
            popup = Popup(title='Test popup',
                      content=Label(text='Reached End'),
                      size_hint=(None, None), size=(400, 400))
            popup.open()

    def on_prev_clicked(self, instance):
        if self.cur_index > 0 and self.cur_index > self.started_index:
            self.cur_index -= 1
            self.image.source = os.path.join(self.base_path, self.files[self.cur_index])

    def on_start_here(self, instance):
        self.button_layout.clear_widgets()
        self.button_layout.add_widget(self.bt_previous)
        self.button_layout.add_widget(self.bt_parking_car)
        self.button_layout.add_widget(self.bt_vacant_parking_space)
        self.button_layout.add_widget(self.bt_no_parking_space)
        self.started_index = self.cur_index

if __name__ == '__main__':
    GroundTruthTaggingApp().run()
