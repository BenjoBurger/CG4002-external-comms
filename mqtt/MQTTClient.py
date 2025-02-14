import sys
import paho.mqtt.client as paho
import traceback
import json

class MQTTClient:
    def __init__(self):
        self.client = paho.Client("mqtt_client")
        # self.client.on_message = self.message_handling

        if self.client.connect("localhost", 1883, 60) != 0:
            print("Could not connect to MQTT broker!")
            sys.exit(1)

        self.client.subscribe("cg4002_b15", 0)

    def run(self, ai_message):
        try:
            message = {
                "topic": "client/visualiser",
                "message": ai_message["action"],
            }
            json_message = json.dumps(message)
            self.send_mqtt_message(json_message)
        except Exception:
            print("Caught an Exception:")
            traceback.print_exc()

    def send_mqtt_message(self, user_input):
        self.client.publish("cg4002_b15", user_input)
            
    def message_handling(self, client, userdata, message):
        print(f"MQTT Client Received message '{message.topic}: {message.payload.decode()}'")