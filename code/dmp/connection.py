#utilizing tcp
import socket
from threading import Thread
import json

datavar = {}
class Client:
    def get_data(self):
        return self.data
    def __init__(self, host='127.0.0.1', port=25000):
        self.host = host
        self.port = port
        self.s = socket.socket()
        self.data = {}
        print('Initialized')

    def connect(self):
        print('Attempting to Connect...')
        self.s.connect((self.host, self.port))
        while True:
            data = self.s.recv(1)
            if not data:
                break
            self.data = json.loads(data.decode())
            global datavar
            datavar = self.data
            #print(datavar)


    def __str__(self):
        return "Host: %s Port %s" % (self.host, self.port)

    def close(self):
        self.s.close()
def run():
    try:
        display = Client()
        display.__str__()
        display.connect()

    except ConnectionRefusedError as e:
        print ("%s \nErrorNo:[%s] \n%s" %
               ("Connection Refused Error", e.errno, "Solution: Ensure the server is listening"))

