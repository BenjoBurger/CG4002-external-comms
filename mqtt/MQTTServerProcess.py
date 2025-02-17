from mqtt.MQTTServer import MQTTServer
from multiprocessing import Queue

def mqtt_server_process(action_queue):
    mqtt_server = MQTTServer(action_queue)
    mqtt_server.run()
