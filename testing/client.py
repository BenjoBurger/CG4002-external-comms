import sys
import json
import paho.mqtt.client as paho
import ssl
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from external_comms.relay_node import RelayClient

MQTT_BROKER = "broker.emqx.io"
# MQTT_BROKER = "172.26.190.163"
MQTT_TOPIC = "cg4002_b15"
MQTT_PORT = 8883

client = paho.Client()
sslSettings = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
sslSettings.check_hostname = False
sslSettings.verify_mode = ssl.CERT_NONE
client.tls_set_context(sslSettings)

# Connect to the broker
if client.connect(MQTT_BROKER, MQTT_PORT, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)

# Start the network loop
client.loop_start()

try:
    while True:
        msg = input("Enter message to publish: ")
        if msg == "exit":
            break
        
        message = {
            "topic": "client/visualiser/action",
            "message": {
                "hp": 100,
                "bullets": msg,
                "shieldHp": 30,
                "action": "snowball"
            }
        }
        json_message = json.dumps(message)
        status = client.publish(MQTT_TOPIC, json_message, 0)
        if status == 1:
            print(f"Sent message to visualiser: {json_message}")
        else:
            print("Failed to send message")

finally:
    # Properly clean up when done
    client.loop_stop()
    client.disconnect()


# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utilities.Action import Action

# message = {
#     "topic": "client/visualiser",
#     "message": "Hello",
# }

# if message.get("shot") is None:
#     print("Hello")
