from multiprocessing import Queue
from mqtt.MQTTClient import MQTTClient

def mqtt_client_process(ai_to_visualiser_queue):
    mqtt_client = MQTTClient()
    while True:
        # get message from ai process and send to visualiser
        if not ai_to_visualiser_queue.empty():
            message = ai_to_visualiser_queue.get()
            mqtt_client.run(message) 