import sys
import paho.mqtt.client as paho

class MQTTServer:
    def __init__(self):
        self.client = paho.Client("mqtt_server")
        self.topic = "game"
        if self.client.connect("localhost", 1883) != 0:
            print("Could not connect to MQTT broker!")
            sys.exit(1)

    def publish(self, message):
        self.client.publish(self.topic, message, 0)

    def disconnect(self):
        self.client.disconnect()