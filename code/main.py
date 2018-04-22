from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from datetime import datetime
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from threading import Thread
import socket
import json
import socket
import os
import sys



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
        self.time = datetime.now().strftime('%H:%M:%S')

    def update_screen(self, current_screen):
        print(current_screen)
        image = StringProperty('./static/close.png')
        # set previous screen - (Settings - Main, Error, Dev, Raw-Data)
        if current_screen != 'settings_screen_name':
            self.previous_screen = current_screen
            self.ids.generate_btn.selected = True
            self.ids.screen_management.current = 'settings_screen_name'
        else:
            self.ids.screen_management.current = self.previous_screen
            self.ids.generate_btn.selected = False

class MainScreen(Screen):
    def __init__(self, **kwargs):   
        super(MainScreen, self).__init__(**kwargs)
        self.server_address = "/tmp/mySocket"
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        Thread(target=self.connect).start()
    def connect(self):
        try:
            self.sock.connect(self.server_address)
        except socket.error as msg:
            print(msg, file=sys.stderr)
        try:
            while True:
                data = self.sock.recv(4096)
                self.update(data)
        finally:
            print('closing socket', file=sys.stderr)
            self.sock.close()

    def update(self, data):
        self.manager.raw_data_screen.populate(data)
        self.manager.dev_screen.update(data)




class ErrorScreen(Screen, RecycleView):
    pass




class DevScreen(Screen):
    list = ListProperty([])
    def update(self, data):
        print(data)
        list[0].append(data)




class RawDataScreen(Screen):
    data = ListProperty()
    def __init__(self, **kwargs):
        super(RawDataScreen, self).__init__(**kwargs)
    def populate(self, data):
        self.ids.rv.data = [{'value': str(x) + " : " + str(y)} for x, y in sorted(data.items())]


class SettingsScreen(Screen):

    pass


class DashUIApp(App):
    def build(self):
        nav = NavigationBar()
        Clock.schedule_interval(nav.update_time, 1)
        return nav

if __name__ == "__main__":
    DashUIApp().run()