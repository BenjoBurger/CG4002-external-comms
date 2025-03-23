import sys
import json
import os
import socket
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.Colour import Colour
from mqtt.MQTTClient import MQTTClient

client = MQTTClient()
while True:
    try:
        message = input("Enter message: ")
        data = {
            "player_id": 1,
            "action": message,
            "see_opponent": 1
        }
        client.send_action(data)
        sleep(1)
    except KeyboardInterrupt:
        print(f"{Colour.PINK}Exiting MQTT Client Process{Colour.RESET}", end="\n\n")
        client.client.disconnect()
        break
    except Exception as e:
        print(f"{Colour.RED}Error in MQTT Client: {e}{Colour.RESET}")
        client.client.reconnect()