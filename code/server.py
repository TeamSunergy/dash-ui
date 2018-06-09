from socket import *
from ex_json import json_ex
from datetime import datetime
import json
import asyncio
import random
import select
import time
import os
from socket import *
import datetime
import json
import os
import time
import sys
import socket
import select

async def echo_server(address, loop, sleep_seconds):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(1)
    print("Server started. Host: %s Port: %s " % (address[0],address[1]))
    # client is a new socket object usable to send and receive data on the connection,
    # address is the address bound to the socket on the other end of the connection
    sock.setblocking(False)
    while True:
        client, address = await loop.sock_accept(sock)
        print('Connection from: ', address)
        loop.create_task(echo_handler(client,loop,sleep_seconds))


async def echo_handler(client, loop, sleep_seconds):
    while True:
        json_ex["motConVehicleVelocity"] += 1
        if json_ex["motConVehicleVelocity"] == 100:
            json_ex["motConVehicleVelocity"] = 1
        json_ex['netPower'] = random.randint(-200, 200)
        json_ex['highestCellTemperature'] = random.randint(1, 75)
        json_ex['batteryPackInstantaneousVoltage'] = random.randint(1,75)
        json_ex['gpio5'] = 1
        json_ex['gpio12'] = 1
        json_ex['soc'] = random.randint(0, 100)
        json_ex['bpsHighVoltage'] = random.randint(100, 200)
        json_ex['mpptTotalNetPower'] = random.randint(100, 200)
        json_ex['mppt1UnitTemperature'] = random.randint(100, 200)
        json_ex['mppt2UnitTemperature'] = random.randint(100, 200)
        json_ex['mppt3UnitTemperature'] = random.randint(100, 200)
        json_ex['internalBPSTemperature'] = random.randint(100, 200)
        json_ex['motConOdometer'] = random.randint(100, 200)



        await asyncio.sleep(sleep_seconds)
        await loop.sock_sendall(client,json.dumps(json_ex).encode())
        print("Send user JSON @", datetime.now())
server_address = "/tmp/mySocket"

from socket import *
from ex_json import json_ex
from datetime import datetime
import json
import asyncio
import random
import select
import time
import os
from socket import *
import datetime
import json
import os
import time
import sys
import socket
import select

server_address = "/tmp/mySocket"

def toDash(server_address, refresh_rate):
    try:
                os.unlink(server_address)
    except OSError:
        if os.path.exists(server_address):
            raise
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Bind the socket to the port
    print('starting up on %s' % server_address, file=sys.stderr)
    sock.bind(server_address)
    sock.setblocking(False)
    # Listen for incoming connections
    sock.listen(1)
    while True:
        # Wait for a connection
        print('waiting for a connection',  file=sys.stderr)
        ready = select.select([sock], [], [], 5)[0]
        if not ready:
            continue
        connection, client_address = sock.accept()
        try:
            print('connection from', server_address,
                  file=sys.stderr)  # server_address is hacky
            # Receive the data in small chunks and retransmit it
            while True:
                json_ex["motConVehicleVelocity"] += 1
                if json_ex["motConVehicleVelocity"] == 100:
                    json_ex["motConVehicleVelocity"] = 1
                json_ex['netPower'] = random.randint(-200, 200)
                json_ex['highestCellTemperature'] = random.randint(1, 75)
                json_ex['batteryPackInstantaneousVoltage'] = random.randint(1, 75)
                json_ex['gpio5'] = 1
                json_ex['gpio12'] = 1
                json_ex['soc'] = random.randint(0, 100)
                json_ex['bpsHighVoltage'] = random.randint(100, 200)
                json_ex['mpptTotalNetPower'] = random.randint(100, 200)
                json_ex['mppt1UnitTemperature'] = random.randint(100, 200)
                json_ex['mppt2UnitTemperature'] = random.randint(100, 200)
                json_ex['mppt3UnitTemperature'] = random.randint(100, 200)
                json_ex['internalBPSTemperature'] = random.randint(100, 200)
                json_ex['motConOdometer'] = random.randint(100, 200)
                dict_data = json.dumps(dict(json_ex))
                connection.sendall(dict_data.encode())
                time.sleep(refresh_rate)
        except:
            print("connection closed")


if __name__ == '__main__':
    toDash(server_address, .1)