import sys
import traceback
import paho.mqtt.client as paho

class MQTTServer:
    def __init__(self, visualiser_to_eval_queue):
        self.client = paho.Client("mqtt_server")
        self.client.on_message = self.message_handling
        self.queue = visualiser_to_eval_queue

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
        self.queue.put(message.payload.decode())
        print(f"Received message '{message.topic}: {message.payload.decode()}'")


def main():
    server = MQTTServer()
    server.run()

if __name__ == "__main__":
    main()