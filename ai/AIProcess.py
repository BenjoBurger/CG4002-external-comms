from queue import Empty
import traceback
from relay_node.RelayClient import RelayClient
from utilities.Action import Action
from utilities.Colour import Colour
import time

GUN_IDX = 9
AI_PORT = 9010
GUN_TIMEOUT = 2
P1_LOGOUT_COUNT = 0
P2_LOGOUT_COUNT = 0

def ai_process(relay_to_ai_queue, ai_to_visualiser_queue, eval_to_relay_queue, p1_shot_queue, p2_shot_queue, is_ai_client_connected):
    ai_client = None
    global P1_LOGOUT_COUNT, P2_LOGOUT_COUNT

    while True:
        # Connect to AI Server
        try:
            ai_client = RelayClient("localhost", AI_PORT)
            ai_client.client.settimeout(5)
            print(f"{Colour.GREEN}AI Client Connected{Colour.RESET}", end="\n\n")
            with is_ai_client_connected.get_lock():
                is_ai_client_connected.value = True
            break
        except ConnectionRefusedError as e:
            print(f"{Colour.RED}Retrying Connection to AI Server...", end="\n\n")
            time.sleep(1)
    while True:
        try:
            while True:
                # Receive message from relay client
                message = relay_to_ai_queue.get()
                # print(f"{Colour.GREEN}AI Process received message{Colour.RESET}", end="\n\n")

                # Get the action from the message
                curr_action = None
                visibility = 0
                if message["gun_fired"] is True:
                    curr_action = Action.values()[GUN_IDX]
                    try:
                        if message["player_id"] == 2:
                            _ = p1_shot_queue.get(timeout=GUN_TIMEOUT)
                            print(f"{Colour.GREEN}AI Process received message from P1 Shot Queue{Colour.RESET}", end="\n\n")
                            visibility = 1
                        elif message["player_id"] == 1:
                            _ = p2_shot_queue.get(timeout=GUN_TIMEOUT)
                            print(f"{Colour.GREEN}AI Process received message from P2 Shot Queue{Colour.RESET}", end="\n\n")
                            visibility = 1
                    except Empty:
                        print(f"{Colour.RED}{message['player_id']} did not get shot{Colour.RESET}", end="\n\n")
                        pass
                else:
                    # Send message to AI Server
                    imu_data = str(message["imu_data"])
                    # print(f"{Colour.GREEN}AI Process sending message to AI Server", end="\n\n")
                    ai_client.send_message(imu_data)
                    try:
                        # Receive message from AI Server
                        response = ai_client.recv_message()
                        curr_action = Action.values()[int(response)]
                        print(f"{Colour.GREEN}AI Process received message from AI Server", end="\n\n")
                    except Exception as e:
                        print(f"{Colour.RED}Error in receiving message from AI Server: {e}{Colour.RESET}", end="\n\n")
                        continue
                print(f"{Colour.GREEN}Player {message['player_id']} Current Action: {curr_action}{Colour.RESET}", end="\n\n")
                # Process the logout action
                if curr_action == "logout":
                    if message["player_id"] == 1:
                        P1_LOGOUT_COUNT += 1
                    if message["player_id"] == 2:
                        P2_LOGOUT_COUNT += 1
                    if P1_LOGOUT_COUNT > 0 and P2_LOGOUT_COUNT > 0:
                        p1_visualiser_data = {
                            "player_id": 1,
                            "action": curr_action
                        }
                        p2_visualiser_data = {
                            "player_id": 2,
                            "action": curr_action
                        }
                        ai_to_visualiser_queue.put(p1_visualiser_data)
                        ai_to_visualiser_queue.put(p2_visualiser_data)

                # Process the invalid action
                elif curr_action == "none":
                    data = {
                        "p1": "",
                        "p2": "",
                    }
                    if message["player_id"] == 1:
                        data["p1"] = curr_action
                    else:
                        data["p2"] = curr_action
                    # eval_to_relay_queue.put(data)

                # Process the other actions
                else:                    
                    P1_LOGOUT_COUNT = 0
                    P2_LOGOUT_COUNT = 0
                    
                    visualiser_data = {
                        "player_id": message["player_id"],
                        "action": curr_action,
                        "visibility": visibility,
                    }

                    # print(f"{Colour.GREEN}AI Process sending message to Visualiser", end="\n\n")
                    ai_to_visualiser_queue.put(visualiser_data)

        except BrokenPipeError:
            while True:
                try:
                    ai_client = RelayClient("localhost", 9010)
                    print(f"{Colour.GREEN}AI Client Connected{Colour.RESET}", end="\n\n")
                    break
                except Exception as e:
                    print(f"{Colour.RED}Error in reconnecting: {e}{Colour.RESET}", end="\n\n")
                    time.sleep(1)
        except Exception as e:
            print(f"{Colour.RED}Error in ai_process: {e}{Colour.RESET}", end="\n\n")
            traceback.print_exc()
            continue
        except KeyboardInterrupt:
            print(f"{Colour.GREEN}Exiting AI Process{Colour.RESET}", end="\n\n")
            ai_client.close()