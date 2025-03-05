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
import paho.mqtt.client as paho
import paho.mqtt.subscribe as subscribe
from paho import mqtt

MQTT_BROKER = "x112e872.ala.asia-southeast1.emqxsl.com"

# callback to print a message once it arrives
def print_msg(client, userdata, message):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )

        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param message: the message with topic and payload
    """
    print("%s : %s" % (message.topic, message.payload))

client = paho.Client("mqtt_server")
client.on_message = print_msg
sslSettings = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
sslSettings.check_hostname = False
sslSettings.verify_mode = ssl.CERT_NONE
client.tls_set_context(sslSettings)
auth = {'username': "test_server", 'password': "Password123"}
client.username_pw_set("test_server", "Password123")
client.connect(MQTT_BROKER, 8883, 300)
client.subscribe("test_topic", qos=1)
client.loop_forever()