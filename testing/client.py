#
# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import ssl
from paho import mqtt
import paho.mqtt.client as paho
import paho.mqtt.publish as publish

# MQTT_BROKER = "x112e872.ala.asia-southeast1.emqxsl.com"

# client = paho.Client("mqtt_client")
# sslSettings = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# sslSettings.check_hostname = False
# sslSettings.verify_mode = ssl.CERT_NONE
# client.tls_set_context(sslSettings)
# client.username_pw_set("test_client", "Password123")
# client.connect(MQTT_BROKER, 8883, 300)
# client.subscribe("test_topic", qos=1)

# while True:
#     msg = input("Enter message to publish: ")
#     if msg == "exit":
#         break
#     client.publish("test_topic", msg, qos=1)

import sys

import paho.mqtt.client as paho

client = paho.Client()

if client.connect("localhost", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)

while True:
    msg = input("Enter message to publish: ")
    if msg == "exit":
        break
    client.publish("cg4002_b15", "Hi, paho mqtt client works fine!", 0)
client.disconnect()