import sys
import paho.mqtt.client as paho

class MQTTClient:
    def __init__(self):
        self.client = paho.Client("mqtt_client")
        self.client.on_message = self.message_handling

        if self.client.connect("localhost", 1883, 60) != 0:
            print("Could not connect to MQTT broker!")
            sys.exit(1)

    def message_handling(self, client, userdata, message):
        print("Received message '" + str(message.payload.decode()) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))
        self.publish("game", "Received message from client!")

    def publish(self, topic, message):
        self.client.publish(topic, message, 0)

    def subscribe(self, topic):
        self.client.subscribe(topic, 0)

    def loop_forever(self):
        try:
            print("Listening for messages...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Disconnecting from MQTT broker...")
            self.client.disconnect()
            sys.exit(0)