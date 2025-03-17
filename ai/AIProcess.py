from relay_node.RelayClient import RelayClient
from utilities.Action import Action
from utilities.Colour import Colour
import json
import time

GUN_IDX = 9

def ai_process(relay_to_ai_queue, ai_to_visualiser_queue, action_queue, eval_to_relay_queue, is_ai_client_connected):
    ai_client = None

    while True:
        try:
            ai_client = RelayClient("localhost", 9010)
            print(f"{Colour.CYAN}AI Client Connected{Colour.RESET}", end="\n\n")
            with is_ai_client_connected.get_lock():
                is_ai_client_connected.value = True
            break
        except ConnectionRefusedError as e:
            print(f"{Colour.RED}Retrying Connection to AI Server...", end="\n\n")
            time.sleep(1)
    try:
        while True:
            message = relay_to_ai_queue.get() # receive message from relay client
            print(f"{Colour.GREEN}AI Process received message{Colour.RESET}", end="\n\n")
            curr_action = None
            if message["gun_fired"] is True:
                data = {
                    "player_id": message["player_id"],
                    "action": Action.values()[GUN_IDX],
                    "see_opponent": 1 if message["IR_Sensor"] == True else 0
                }
                # action_queue.put(data)
                curr_action = Action.values()[GUN_IDX]
            else:
                imu_data = str(message["imu_data"])
                print(f"{Colour.GREEN}AI Process sending message to AI Server", end="\n\n")
                ai_client.send_message(imu_data) # send message to ai server
                try:
                    response = ai_client.recv_message() # receive message from ai server
                    print(f"{Colour.GREEN}AI Process received message from AI Server", end="\n\n")
                except Exception as e:
                    print(f"{Colour.RED}Error in AI Process: {e}{Colour.RESET}", end="\n\n")
                    raise e
                curr_action = Action.values()[int(response)]
                
            if curr_action == "logout" or curr_action == "none":
                data = {
                    "p1": "",
                    "p2": "",
                }
                if message["player_id"] == 1:
                    data["p1"] = curr_action
                else:
                    data["p2"] = curr_action
                eval_to_relay_queue.put(data)
            else:
                data = {
                    "player_id": message["player_id"],
                    "action": curr_action,
                    "see_opponent": 1 if message["IR_Sensor"] == True else 0
                }
                print(f"{Colour.GREEN}AI Process sending message to Visualiser", end="\n\n")
                ai_to_visualiser_queue.put(data) # send message to visualiser to query
    except Exception as e:
        print(f"{Colour.RED}Error in ai_process: {e}{Colour.RESET}", end="\n\n")
        raise e
    finally:
        ai_client.close()
        print(f"{Colour.CYAN}AI Client Closed{Colour.RESET}", end="\n\n")