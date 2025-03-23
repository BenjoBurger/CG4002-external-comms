from mqtt.MQTTServer import MQTTServer
from multiprocessing import Queue
from utilities.Colour import Colour
import traceback

def mqtt_server_process(action_queue, is_mqtt_server_connected):
    mqtt_server = MQTTServer(action_queue)
    with is_mqtt_server_connected.get_lock():
        is_mqtt_server_connected.value = True
    while True:
        try:
            mqtt_server.client.loop_forever()
        except KeyboardInterrupt:
            print(f"{Colour.PINK}Exiting MQTT Server Process{Colour.RESET}", end="\n\n")
            mqtt_server.client.disconnect()
            break
        except Exception as e:
            print(f"{Colour.RED}Error in MQTT Server: {e}{Colour.RESET}")
            while True:
                try:
                    mqtt_server = MQTTServer(action_queue)
                    print(f"{Colour.PINK}Reconnected to MQTT Server{Colour.RESET}", end="\n\n")
                    break
                except Exception as e:
                    print(f"{Colour.RED}Reconnection failed: {e}{Colour.RESET}")
                    traceback.print_exc()
                    continue