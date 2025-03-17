from mqtt.MQTTServer import MQTTServer
from multiprocessing import Queue
from utilities.Colour import Colour
import traceback

def mqtt_server_process(action_queue, is_mqtt_server_connected):
    mqtt_server = MQTTServer(action_queue)
    with is_mqtt_server_connected.get_lock():
        is_mqtt_server_connected.value = True
    try:
        mqtt_server.client.loop_forever()
    except Exception:
        print(f"{Colour.RED}Caught an Exception:{Colour.RESET}")
        traceback.print_exc()
    finally:
        print(f"{Colour.PINK}Disconnecting from the MQTT broker{Colour.RESET}", end="\n\n")
        mqtt_server.client.disconnect()
