import sys
import json
import paho.mqtt.client as paho
from utilities.Colour import Colour

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "cg4002_b15"
MQTT_PORT = 1883

class MQTTServer:
    def __init__(self, action_queue):
        self.queue = action_queue
        self.client = paho.Client("mqtt_server")
        self.client.on_message = self.message_handling

        if self.client.connect(MQTT_BROKER, MQTT_PORT, 300) != 0:
            print(f"{Colour.RED}Could not connect to MQTT broker!{Colour.RESET}", end="\n\n")
            sys.exit(1)
        print(f"{Colour.PINK}Server Connected to MQTT broker{Colour.RESET}", end="\n\n")
        self.client.subscribe(MQTT_TOPIC, 0)
        
    def message_handling(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        topic = message.topic
        # only handle messages from visualiser
        if msg["topic"] == "visualiser/mqtt_server":
            data = {
                "player_id": msg["playerId"],
                "action": msg["action"],
                "see_opponent": msg["seeOpponent"]
            }
            self.queue.put(data)
            print(f"{Colour.PINK}MQTT Server Received message '{topic}: {msg}'{Colour.RESET}", end="\n\n")