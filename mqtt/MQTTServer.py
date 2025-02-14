import sys
import traceback
import paho.mqtt.client as paho
import json

class MQTTServer:
    def __init__(self, action_queue):
        self.queue = action_queue
        self.client = paho.Client("mqtt_server")
        self.client.on_message = self.message_handling

        if self.client.connect("localhost", 1883) != 0:
            print("Could not connect to MQTT broker!")
            sys.exit(1)
        
        self.client.subscribe("cg4002_b15", 0)
        
    def run(self):
        try:
            print("Press CTRL+C to exit...")
            self.client.loop_forever()
        except Exception:
            print("Caught an Exception:")
            traceback.print_exc()
        finally:
            print("Disconnecting from the MQTT broker")
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
            print(f"MQTT Server Received message '{topic}: {msg}'")