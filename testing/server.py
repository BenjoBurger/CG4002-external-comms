import sys
import ssl
import paho.mqtt.client as paho

MQTT_BROKER = "broker.emqx.io"

def message_handling(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")


client = paho.Client("mqtt_server")
sslSettings = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
sslSettings.check_hostname = False
sslSettings.verify_mode = ssl.CERT_NONE
client.tls_set_context(sslSettings)
client.on_message = message_handling

if client.connect(MQTT_BROKER, 8883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)

client.subscribe("cg4002_b15")

try:
    print("Press CTRL+C to exit...")
    client.loop_forever()
except Exception:
    print("Caught an Exception, something went wrong...")
finally:
    print("Disconnecting from the MQTT broker")
    client.disconnect()