import sys
import traceback
import paho.mqtt.client as paho
import json
from utilities.Colour import Colour

class MQTTServer:
    def __init__(self, action_queue):
        self.queue = action_queue
        self.client = paho.Client("mqtt_server")
        self.client.on_message = self.message_handling

        if self.client.connect("localhost", 1883) != 0:
            print(f"{Colour.RED}Could not connect to MQTT broker!{Colour.RESET}", end="\n\n")
            sys.exit(1)
        print(f"{Colour.PINK}Server Connected to MQTT broker{Colour.RESET}", end="\n\n")
        self.client.subscribe("cg4002_b15", 0)
        
    def run(self):
        try:
            self.client.loop_forever()
        except Exception:
            print(f"{Colour.RED}Caught an Exception:{Colour.RESET}")
            traceback.print_exc()
        finally:
            print(f"{Colour.PINK}Disconnecting from the MQTT broker{Colour.RESET}", end="\n\n")
            self.client.disconnect()
        
    def message_handling(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        topic = message.topic
        if msg["topic"] == "visualiser/mqtt_server":
            data = {
                "player_id": msg["playerId"],
                "action": msg["action"],
                "see_opponent": msg["seeOpponent"]
            }
            self.queue.put(data)
            print(f"{Colour.PINK}MQTT Server Received message '{topic}: {msg}'{Colour.RESET}", end="\n\n")