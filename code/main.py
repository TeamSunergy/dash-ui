import os
import sys
import socket
from json import loads
from kivy.uix.recycleview import RecycleView
from threading import Thread
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.animation import Animation
from tools.convert_colors import percentColor
from tools.fonts import KIVY_FONTS
from dictionary.dictionary import dictionary
from kivy.storage.jsonstore import JsonStore
from range_key_dict import RangeKeyDict
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, DictProperty
from kivy.clock import Clock
from datetime import datetime
from kivy.uix.anchorlayout import AnchorLayout
import logging


class ScreenManagement(ScreenManager):
    main_screen = ObjectProperty(None)
    error_screen = ObjectProperty(None)
    dev_screen = ObjectProperty(None)
    raw_data_screen = ObjectProperty(None)
    settings_screen = ObjectProperty(None)
    splash_screen = ObjectProperty(None)
    user_profile = ObjectProperty(None)


class NavigationBar(AnchorLayout):
    time = StringProperty(0)
    current_screen = StringProperty(False)
    list = DictProperty(dictionary)
    previous_screen = 'main_screen_name'

    def __init__(self, **kwargs):
        super(NavigationBar, self).__init__(**kwargs)

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

    def update(self, data):
        self.list = data


class MainScreen(Screen):
    list = DictProperty(dictionary)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.motConVehicleVelocity = '0'
        self.server_address = "/tmp/mySocket"
        self.sock = socket.socket()
        self.data = {}
        self.left_turn_signal = True
        self.right_turn_signal = True
        self.light_one = Animation(color=[.92, .73, .44, 1]) + Animation(color=[.33, .33, .33, 1])
        self.light_one.repeat = True
        self.light_two = Animation(color=[.92, .73, .44, .75]) + Animation(color=[.33, .33, .33, 1])
        self.light_two.repeat = True
        self.light_three = Animation(color=[.92, .73, .44, .5]) + Animation(color=[.33, .33, .33, 1])
        self.light_three.repeat = True
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        logging.info("Kivy has finished loading.")
        logging.info("Starting thread to read from socket : " + self.server_address)
        Thread(target=self.main).start()

    def main(self):
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        # print ('connecting to %s' % server_address, file=sys.stderr)
        try:
            sock.connect(self.server_address)
            logging.info("Socket connected to: " + self.server_address)
        except socket.error as msg:
            logging.critical(msg)
            sys.exit(1)

        try:

            # Send data
            # message = b'This is the message.  It will be repeated.'
            # print ('sending "%s"' % message, file=sys.stderr)
            # sock.sendall(message)

            amount_received = 0
            # amount_expected = len(message)

            # while amount_received < amount_expected:
            while True:
                data = sock.recv(4096)
                # amount_received += len(data)
                try:
                    self.data = loads(data.decode())
                    self.list = self.data
                    self.update(self.data)
                except:
                    logging.critical("ERROR loading data")
        finally:
            # print ('closing socket', file=sys.stderr)
            sock.close()
            logging.info("Socket Closed" + self.server_address)
            # pass

    def animate_left_lights(self, data):

        self.left_turn_signal = False
        self.light_one.start(self.ids.left1)
        self.light_two.start(self.ids.left2)
        self.light_three.start(self.ids.left3)

    def animate_right_lights(self, data):

        self.right_turn_signal = False
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
        self.right_turn_signal = True

    def stop_animate_left_lights(self, data):

        self.light_one.cancel(self.ids.left1)
        self.light_two.cancel(self.ids.left2)
        self.light_three.cancel(self.ids.left3)
        self.ids.left1.color = [1, 1, 1, 1]
        self.ids.left2.color = [.92, .73, .44, 0]
        self.ids.left3.color = [.92, .73, .44, 0]
        self.left_turn_signal = True

    def set_lights(self, turn_signal):
        self.turn_signal = turn_signal

    net_gauge = ListProperty([1, 1, 1, 1])
    soc = ListProperty([1,1,1,1])

    def update(self, data):
        print(data)
        if self.data['gpio5'] == 1 and self.right_turn_signal:
            self.animate_right_lights(data)
        elif self.data['gpio5'] == 0:
            self.stop_animate_right_lights(data)
        if self.data['gpio6'] == 1 and self.left_turn_signal:
            self.animate_left_lights(data)
        elif self.data['gpio6'] == 0:
            self.stop_animate_left_lights(data)

        self.soc = self.soc_color(data['soc'])
        self.net_gauge = percentColor(self.data['netPower'])
        # ---------------------------------

        self.manager.raw_data_screen.populate(data)
        self.manager.dev_screen.update(data)
        App.get_running_app().update(data)

    def soc_color(self, num):
        range_key_dict = RangeKeyDict({
            (0, 26): [.99, .40, .34, 1],
            (26, 51): [.99, .71, .36, 1],
            (51, 76): [.99, .84, .21, 1],
            (76, 101): [.36, .83, .59, 1]
        })
        return range_key_dict[num]

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

#TODO:
class ErrorScreen(Screen, RecycleView):
    pass


class DevScreen(Screen):
    list = DictProperty(dictionary)

    def __init__(self, **kwargs):
        super(DevScreen, self).__init__(**kwargs)

    def update(self, data):
        self.list = data

#Display a python dictionary in sorted, key : value pairs
class RawDataScreen(Screen):
    data = ListProperty()

    def __init__(self, **kwargs):
        super(RawDataScreen, self).__init__(**kwargs)

    def populate(self, data):
        self.ids.rv.data = [{'key': str(x), 'value': str(y)} for x, y in sorted(data.items())]

#TODO:
class SettingsScreen(Screen):
    pass

#The start of the applicaiton opens a splash screen with the team's logo.
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.change_screen, 3)

    def change_screen(self, *args):
        if self.manager.current == 'splash_screen_name':
            self.manager.current = 'main_screen_name'

    def on_touch_down(self, touch):
        self.manager.current = 'main_screen_name'


#TODO:
class UserProfile(Screen):
    def __init__(self, **kwargs):
        super(UserProfile, self).__init__(**kwargs)
        store = JsonStore('user-profile.json')
        self.users = store.get('users')


class DashUIApp(App):
    list = DictProperty(dictionary)

    def update(self, data):
        self.list = data

    def build(self):
        nav = NavigationBar()
        Clock.schedule_interval(nav.update_time, 1)
        return nav


if __name__ == "__main__":
    # Register fonts - KIVY_FONTS
    for font in KIVY_FONTS:
        LabelBase.register(**font)
    logging.info("Attempting to start Kivy")
    try:
        DashUIApp().run()
    except:
        logging.critical("Kivy failed to started.")


