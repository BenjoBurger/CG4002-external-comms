import sys
import paho.mqtt.client as paho
import traceback
import json
from utilities.Colour import Colour

MQTT_BROKER = "localhost"
MQTT_TOPIC = "cg4002_b15"
MQTT_PORT = 1883

class MQTTClient:
    def __init__(self):
        self.client = paho.Client('publish-mqtt-client')

        if self.client.connect(MQTT_BROKER, MQTT_PORT, 300) != 0:
            print(f"{Colour.RED}Could not connect to MQTT broker!{Colour.RESET}", end="\n\n")
            sys.exit(1)
        print(f"{Colour.PINK}Client Connected to MQTT broker{Colour.RESET}", end="\n\n")
        
        self.client.subscribe(MQTT_TOPIC, 0)

    def send_action(self, ai_message):
        try:
            message = {
                "topic": "client/visualiser",
                "message": ai_message["action"],
            }
            self.send_mqtt_message(message)
        except Exception:
            print(f"{Colour.RED}Caught an Exception:{Colour.RESET}")
            traceback.print_exc()
    
    def send_game_state(self, game_state):
        try:
            message = {
                "topic": "client/visualiser",
                "message": game_state,
            }
            self.send_mqtt_message(message)
        except Exception:
            print(f"{Colour.RED}Caught an Exception:{Colour.RESET}")
            traceback.print_exc()

    def send_mqtt_message(self, message):
        json_message = json.dumps(message)
        print(f"{Colour.PINK}Sending Message to Visualiser: {json_message}{Colour.RESET}", end="\n\n")
        status = self.client.publish(MQTT_TOPIC, json_message)
        # if status == 0:
        #     print(f"{Colour.PINK}Sending Message to visualiser `{user_input}` to topic `{MQTT_TOPIC}`{Colour.RESET}", end="\n\n")
        # else:
        #     print(f"{Colour.RED}Failed to send message to topic {MQTT_TOPIC}{Colour.RESET}")
            
    def message_handling(self, client, userdata, message):
        print(f"{Colour.PINK}MQTT Client Received Message '{message.topic}: {message.payload.decode()}'{Colour.RESET}", end="\n\n")