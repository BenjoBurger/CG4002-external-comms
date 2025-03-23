import sys
import ssl
import paho.mqtt.client as paho
import json
import os
from multiprocessing import Queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.Colour import Colour
from mqtt.MQTTServer import MQTTServer

queue = Queue()
server = MQTTServer(queue)
while True:
    try:
        server.client.loop_forever()
    except KeyboardInterrupt:
        print(f"{Colour.PINK}Exiting MQTT Server Process{Colour.RESET}", end="\n\n")
        server.client.disconnect()
        break
    except Exception as e:
        print(f"{Colour.RED}Error in MQTT Server: {e}{Colour.RESET}")
        while True:
            try:
                server = MQTTServer(queue)
                print(f"{Colour.ORANGE}Reconnected to MQTT Server{Colour.RESET}", end="\n\n")            
                break
            except Exception as e:
                print(f"{Colour.RED}Reconnection failed: {e}{Colour.RESET}")