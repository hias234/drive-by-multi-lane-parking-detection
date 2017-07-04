
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

path = 'C:\sw\master\collected data\data'


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


class GroundTruthTaggingApp(App):

    def build(self):
        layout = FloatLayout(size=(300, 300))

        self.image = Image(source='C:\\sw\\master\\collected data\\data\\raw_20170704_191952_111273.dat_images_Camera\\20170704_191952_650762.jpg', size_hint=(.7, .7), pos=(150, 250))

        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .1), pos=(0, 0))
        self.bt_previous = Button(text='<')
        self.bt_occupied_parking_space = Button(text='Occupied Parking Space')
        self.bt_vacant_parking_space = Button(text='Vacant Parking Space')
        self.bt_no_parking_space = Button(text='No Parking Space')
        self.bt_no_parking_space = Button(text='No Parking Space')
        self.bt_next = Button(text='>')
        button_layout.add_widget(self.bt_previous)
        button_layout.add_widget(self.bt_occupied_parking_space)
        button_layout.add_widget(self.bt_vacant_parking_space)
        button_layout.add_widget(self.bt_no_parking_space)
        button_layout.add_widget(self.bt_next)

        layout.add_widget(self.image)
        layout.add_widget(button_layout)

        return layout


if __name__ == '__main__':
    GroundTruthTaggingApp().run()
