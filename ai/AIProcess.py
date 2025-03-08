from relay_node.RelayClient import RelayClient
from utilities.Action import Action
from utilities.Colour import Colour
import json
import time

action_list = [Action.shield, Action.shoot, Action.bomb, Action.reload, Action.badminton, Action.golf, Action.fencing, Action.boxing]

def ai_process(relay_to_ai_queue, ai_to_visualiser_queue, action_queue):
    ai_client = None

    while True:
        try:
            ai_client = RelayClient("localhost", 9010)
            print(f"{Colour.CYAN}AI Client Connected{Colour.RESET}", end="\n\n")
            break
        except ConnectionRefusedError as e:
            print(f"{Colour.RED}Retrying Connection to AI Server...", end="\n\n")
            time.sleep(1)
    try:
        while True:
            message = relay_to_ai_queue.get() # receive message from relay client
            print(f"{Colour.GREEN}AI Process received message: {message}{Colour.RESET}", end="\n\n")
            ai_client.send_message(message)
            try:
                response = ai_client.recv_message()
                response_msg = json.loads(response)
            except Exception as e:
                print(f"{Colour.RED}Error in AI Process: {e}{Colour.RESET}", end="\n\n")
                raise e
            """
            AI logic goes here
            """
            data = {
                "player_id": response_msg["player_id"],
                "action": response_msg["action"],
                "see_opponent": response_msg["ir_data"]
            }
            if response_msg["action"] == "bomb":
                print(f"{Colour.GREEN}AI Process sending message to Visualiser: {data}{Colour.RESET}", end="\n\n")
                ai_to_visualiser_queue.put(data) # send message to visualiser to query
            else:
                print(f"{Colour.GREEN}AI Process sending message to Eval Client: {data}{Colour.RESET}", end="\n\n")
                action_queue.put(data) # send message to eval client immediately
    except Exception as e:
        print(f"{Colour.RED}Error in ai_process: {e}{Colour.RESET}", end="\n\n")
        raise e
    finally:
        ai_client.close()
        print(f"{Colour.CYAN}AI Client Closed{Colour.RESET}", end="\n\n")