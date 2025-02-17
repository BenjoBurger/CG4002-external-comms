# python 3.11

import random
import time

from paho.mqtt import client as mqtt_client
import json


broker = 'broker.emqx.io'
port = 1883
topic = "cg4002_b15"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg):
    time.sleep(1)
    message = {
        "topic": "client/visualiser",
        "message": msg["action"],
    }
    json_message = json.dumps(message)
    result = client.publish(topic, json_message)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{json_message}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run(msg):
    client = connect_mqtt()
    client.loop_start()
    publish(client, msg)
    client.loop_stop()


if __name__ == '__main__':
    run()
