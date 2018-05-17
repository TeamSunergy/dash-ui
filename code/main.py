from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, DictProperty
from kivy.clock import Clock
from datetime import datetime
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.recycleview import RecycleView
from threading import Thread
import socket
import json
import socket
import os
import sys
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.animation import Animation
from code.tools.convert_colors import percentColor
import time

KIVY_FONTS = [
    {
        "name": "Inconsolata",
        "fn_regular": "static/fonts/Inconsolata/Inconsolata-Regular.ttf",
    },
    {
        "name": "SourceSansPro",
        "fn_regular": "static/fonts/Source_Sans_Pro/SourceSansPro-Regular.ttf"
    }
]
class ScreenManagement(ScreenManager):
    main_screen = ObjectProperty(None)
    error_screen = ObjectProperty(None)
    dev_screen = ObjectProperty(None)
    raw_data_screen = ObjectProperty(None)
    settings_screen = ObjectProperty(None)


class NavigationBar(AnchorLayout):
    time = StringProperty(0)
    current_screen = StringProperty(False)

    # update StringProperty time -- 1 second intervals
    def update_time(self, *args):
        self.time = datetime.now().strftime('%-I:%M %p')

    # store previous screen - (Settings - Main, Error, Dev, Raw-Data)
    def update_screen(self, current_screen):
        if current_screen != 'settings_screen_name':
            self.previous_screen = current_screen
            self.ids.generate_btn.selected = True
            self.ids.screen_management.current = 'settings_screen_name'
        else:
            self.ids.screen_management.current = self.previous_screen
            self.ids.generate_btn.selected = False


class MainScreen(Screen):
    list = DictProperty({'speed': 0})
    def __init__(self, **kwargs):   
        super(MainScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.speed = '0'
        self.host = '127.0.0.1'
        self.port = 25000
        self.sock = socket.socket()
        self.data = {}
        self.turn_signal = True
        self.light_one = Animation(color=[.92, .73, .44, 1]) + Animation(color=[.33, .33, .33, 1])
        self.light_one.repeat = True
        self.light_two = Animation(color=[.92, .73, .44, .75]) + Animation(color=[.33, .33, .33, 1])
        self.light_two.repeat = True
        self.light_three = Animation(color=[.92, .73, .44, .5]) + Animation(color=[.33, .33, .33, 1])
        self.light_three.repeat = True
        Thread(target=self.connect).start()
    def connect(self):
        self.sock.connect((self.host, self.port))
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            self.data = json.loads(data.decode())
            self.list = self.data
            self.update(self.data)

    def animate_left_lights(self, data):
        self.set_lights(False)
        self.light_one.start(self.ids.left1)
        self.light_two.start(self.ids.left2)
        self.light_three.start(self.ids.left3)

    def animate_right_lights(self, data):
        self.set_lights(False)
        self.light_one.start(self.ids.right1)
        self.light_two.start(self.ids.right2)
        self.light_three.start(self.ids.right3)

    def stop_animate_right_lights(self, data):
        self.light_one.cancel(self.ids.right1)
        self.light_two.cancel(self.ids.right2)
        self.light_three.cancel(self.ids.right3)
        self.ids.right1.color = [1, 1, 1, 1]
        self.ids.right2.color = [.92, .73, .44, 0]
        self.ids.right3.color = [.92, .73, .44, 0]
        self.set_lights(True)

    def stop_animate_left_lights(self, data):
        self.light_one.cancel(self.ids.left1)
        self.light_two.cancel(self.ids.left2)
        self.light_three.cancel(self.ids.left3)
        self.ids.left1.color = [1, 1, 1, 1]
        self.ids.left2.color = [.92, .73, .44, 0]
        self.ids.left3.color = [.92, .73, .44, 0]
        self.set_lights(True)

    def set_lights(self, turn_signal):
        self.turn_signal = turn_signal

    net_gauge = ListProperty([1, 1, 1, 1])

    def update(self, data):

        #TEST LOGIC -- NOT CORRECT IMPLEMENTATION
        if self.data['speed'] == 1 and self.turn_signal:
            self.animate_right_lights(data)
        if self.data['speed'] == 10:
            self.stop_animate_left_lights(data)
            self.stop_animate_right_lights(data)
        self.net_gauge = percentColor(self.data['speed'])
        # ---------------------------------

        self.manager.raw_data_screen.populate(data)
        self.manager.dev_screen.update(data)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == '1':
            self.manager.current = 'settings_screen_name'
        elif keycode[1] == '2':
            self.manager.current = 'main_screen_name'
        elif keycode[1] == '3':
            self.manager.current = 'dev_screen_name'
        elif keycode[1] == '4':
            self.manager.current = 'raw_data_screen_name'
        elif keycode[1] == '5':
            self.manager.current = 'error_screen_name'
        return True


class ErrorScreen(Screen, RecycleView):
    pass


class DevScreen(Screen):
    list = DictProperty({'speed': 0})

    def __init__(self, **kwargs):
        super(DevScreen, self).__init__(**kwargs)

    def update(self, data):
        self.list = data


class RawDataScreen(Screen):
    data = ListProperty()

    def __init__(self, **kwargs):
        super(RawDataScreen, self).__init__(**kwargs)

    def populate(self, data):
        self.ids.rv.data = [{'value': str(x) + " : " + str(y)} for x, y in sorted(data.items())]


class SettingsScreen(Screen):
    pass


class DashUIApp(App):
    colors_hex = {
        'white': '#ffffff',
        'red': '#000000',
        'green': '#111111',
        'gray_0': '#222222',
        'gray_1': '#232323',
        'yellow': '#333333',
        'blue': '#444444'
    }
    top = DictProperty({'right_one': [1, 1, 1, 1], 'right_two': [0, 0, 0, 0], 'right_three': [0, 0, 0, 0]})
    test = DictProperty({'park': 0})

    def build(self):
        nav = NavigationBar()
        Clock.schedule_interval(nav.update_time, 1)
        # setup_colors(self.colors_hex)
        return nav

if __name__ == "__main__":
    for font in KIVY_FONTS:
        LabelBase.register(**font)
    DashUIApp().run()


