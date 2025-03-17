import sys
import ssl
import paho.mqtt.client as paho
import json

MQTT_BROKER = "broker.emqx.io"

def message_handling(client, userdata, msg):
    msg = json.loads(msg.payload.decode())
    if msg["topic"] == "visualiser/mqtt_server":
        data = {
            "player_id": msg["playerId"],
            "action": msg["action"],
            "is_active": int(msg["isActive"]),
            "is_visible": msg["isVisible"],
        }
        print(f"{msg.topic}: {data}")


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

# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from relay_node.RelayServer import RelayServer
# from utilities.Colour import Colour

# try:
#     relay_node_server = RelayServer(8000)
#     print(f"{Colour.CYAN}Relay Server Connected{Colour.RESET}", end="\n\n")
#     while True:
#         # Accept connection from relay client
#         conn_socket, client_addr = relay_node_server.client.accept()
#         print(f"{Colour.CYAN}Relay Client connected: {client_addr}{Colour.RESET}", end="\n\n")
# except Exception as e:
#     print(f"{Colour.RED}Error in relay_server_process: {e}{Colour.RESET}", end="\n\n")
#     raise e
# finally:
#     relay_node_server.client.close()
#     print(f"{Colour.CYAN}Relay Server Closed{Colour.RESET}", end="\n\n")

