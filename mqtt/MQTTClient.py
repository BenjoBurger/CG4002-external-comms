import sys
import paho.mqtt.client as paho
import traceback
import json
from utilities.Colour import Colour

class MQTTClient:
    def __init__(self):
        self.client = paho.Client("mqtt_client")
        # self.client.on_message = self.message_handling

        if self.client.connect("localhost", 1883, 300) != 0:
            print(f"{Colour.RED}Could not connect to MQTT broker!{Colour.RESET}", end="\n\n")
            sys.exit(1)
        print(f"{Colour.PINK}Client Connected to MQTT broker{Colour.RESET}", end="\n\n")
        self.client.subscribe("cg4002_b15", 0)

    def run(self, ai_message):
        try:
            message = {
                "topic": "client/visualiser",
                "message": ai_message["action"],
            }
            json_message = json.dumps(message)
            print(f"{Colour.PINK}Sending message to MQTT Server: {json_message}{Colour.RESET}", end="\n\n")
            self.send_mqtt_message(json_message)
        except Exception:
            print(f"{Colour.RED}Caught an Exception:{Colour.RESET}")
            traceback.print_exc()

    def send_mqtt_message(self, user_input):
        self.client.publish("cg4002_b15", user_input)
            
    def message_handling(self, client, userdata, message):
        print(f"{Colour.PINK}MQTT Client Received message '{message.topic}: {message.payload.decode()}'{Colour.RESET}", end="\n\n")