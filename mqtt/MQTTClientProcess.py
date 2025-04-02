from mqtt.MQTTClient import MQTTClient
from utilities.Colour import Colour

def mqtt_client_process(ai_to_visualiser_queue, eval_to_visualiser_queue, is_mqtt_client_connected):
    mqtt_client = MQTTClient()
    with is_mqtt_client_connected.get_lock():
        is_mqtt_client_connected.value = True
    while True:
        try:
            while True:
                # Send message to visualiser to query visibility
                message = ai_to_visualiser_queue.get()
                mqtt_client.send_action(message)

                # Send message to visualiser to update game state
                message = eval_to_visualiser_queue.get()
                mqtt_client.send_game_state(message)
        except KeyboardInterrupt:
            print(f"{Colour.PINK}Exiting MQTT Server Process{Colour.RESET}", end="\n\n")
            mqtt_client.client.disconnect()
            break
        except Exception as e:
            print(f"{Colour.RED}Error in MQTT Client: {e}{Colour.RESET}")
            try:
                mqtt_client = MQTTClient()
                print(f"{Colour.PINK}Reconnected to MQTT Server{Colour.RESET}", end="\n\n")
            except Exception as e:
                print(f"{Colour.RED}Reconnection failed: {e}{Colour.RESET}")
                continue