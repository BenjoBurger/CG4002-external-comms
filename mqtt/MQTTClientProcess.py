from multiprocessing import Queue
from mqtt.MQTTClient import MQTTClient

def mqtt_client_process(ai_to_visualiser_queue):
    mqtt_client = MQTTClient()
    while True:
        if not ai_to_visualiser_queue.empty():
            message = ai_to_visualiser_queue.get()
            mqtt_client.run(message)
    # except KeyboardInterrupt:
    #     print("MQTT Client Process Exiting")
    #     mqtt_client.client.disconnect()


dummy_data1 = {
    "player_id": "p1",
    "action": "shoot",
    "see_opponent": False
}

dummy_data2 = {
    "player_id": "p1",
    "action": "bomb",
    "see_opponent": True
}

if __name__ == "__main__":
    queue = Queue()
    queue.put(dummy_data1)
    queue.put(dummy_data2)
    mqtt_client_process(queue)