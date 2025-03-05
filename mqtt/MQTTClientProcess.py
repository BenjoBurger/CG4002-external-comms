from mqtt.MQTTClient import MQTTClient
from utilities.Colour import Colour
import logging

logging.basicConfig(filename="mqttclient.log", level=logging.DEBUG, format="%(asctime)s - %(message)s")

def mqtt_client_process(ai_to_visualiser_queue, eval_to_visualiser_queue):
    mqtt_client = MQTTClient()
    while True:
        # get message from ai process and send to visualiser
        try:
            while True:
                if not ai_to_visualiser_queue.empty():
                    message = ai_to_visualiser_queue.get()
                    mqtt_client.send_action(message)
                    logging.info(f"Sent message to visualiser: {message}")
                if not eval_to_visualiser_queue.empty():
                    message = eval_to_visualiser_queue.get()
                    mqtt_client.send_game_state(message)
                    logging.info(f"Sent game state to visualiser: {message}")
        except KeyboardInterrupt:
            print(f"{Colour.PINK}Exiting MQTT Client Process{Colour.RESET}", end="\n\n")
            break
        except Exception as e:
            print(f"Error: {e}")
            break