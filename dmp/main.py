from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
import time
from datetime import datetime
from kivy.clock import Clock
from threading import Thread
import socket
import json
from kivy.uix.widget import Widget

class Values(Widget):
    timer_update = NumericProperty(0)
    dist_travel = NumericProperty(0)
    average_mph = NumericProperty(0)
    dist_travel_2 = NumericProperty(0)
    temp = NumericProperty(0)

class Update():
    values = Values()

    def __init__(self):
        self.speed = '0'
        self.host = '127.0.0.1'
        self.port = 25000
        self.s = socket.socket()
        self.data = {}

    def connect(self):
        self.s.connect((self.host, self.port))
        while True:
            data = self.s.recv(1024)
            if not data:
                break
            self.data = json.loads(data.decode())
            instance = self.parent.get_screen('settings')
class Dash(FloatLayout):
    pass
class NavBar(AnchorLayout):
    pass
class SettingsMenu(AnchorLayout):
    temp = NumericProperty()
    def access_update_val(self, obj):
        print("Input_Screen: update_val.temp={}".format(obj.temp))
        self.temp = obj.temp


class Messages(AnchorLayout):
    pass
class StandardMenu(GridLayout):
    pass
class LeftStack(StackLayout):
    pass
class Header(GridLayout):
    pass
class RawData(RecycleView):
    pass
class Table(ScrollView):
    pass



class DasApp(App):
    settings = SettingsMenu()
    #time avaliable to all screens
    time = StringProperty('00:00:00')
    def set_time(self, *args):
        self.time= datetime.now().strftime('%H:%M:%S')
    Thread(target=Update().connect).start()

    def build(self):
        self.settings = SettingsMenu()
        self.background_color = settings['background_color']
        Clock.schedule_interval(self.set_time, 1)
        return Builder.load_file('dash.kv')

if __name__ == '__main__':
    settings = {
        'background_color': [0,0,0,.5]
    }
    Thread(target=DasApp().run()).start()