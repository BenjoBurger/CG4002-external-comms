from mqtt.MQTTServer import MQTTServer
from multiprocessing import Queue
from utilities.Colour import Colour
import traceback

def mqtt_server_process(action_queue):
    mqtt_server = MQTTServer(action_queue)
    try:
        mqtt_server.client.loop_forever()
    except Exception:
        print(f"{Colour.RED}Caught an Exception:{Colour.RESET}")
        traceback.print_exc()
    finally:
        print(f"{Colour.PINK}Disconnecting from the MQTT broker{Colour.RESET}", end="\n\n")
        mqtt_server.client.disconnect()
