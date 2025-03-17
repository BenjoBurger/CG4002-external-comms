from mqtt.MQTTClient import MQTTClient
from utilities.Colour import Colour

def mqtt_client_process(ai_to_visualiser_queue, eval_to_visualiser_queue, is_mqtt_client_connected):
    mqtt_client = MQTTClient()
    with is_mqtt_client_connected.get_lock():
        is_mqtt_client_connected.value = True
    while True:
        # get message from ai process and send to visualiser
        try:
            while True:
                if not ai_to_visualiser_queue.empty():
                    message = ai_to_visualiser_queue.get()
                    mqtt_client.send_action(message)
                if not eval_to_visualiser_queue.empty():
                    message = eval_to_visualiser_queue.get()
                    mqtt_client.send_game_state(message)
        except KeyboardInterrupt:
            print(f"{Colour.PINK}Exiting MQTT Client Process{Colour.RESET}", end="\n\n")
            break
        except Exception as e:
            print(f"Error: {e}")
            break