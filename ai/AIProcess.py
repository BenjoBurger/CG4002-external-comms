from random import Random
from utilities.Action import Action
from utilities.Colour import Colour
import logging

logging.basicConfig(filename="ai.log", level=logging.DEBUG, format="%(asctime)s - %(message)s")

action_list = [Action.shield, Action.shoot, Action.bomb, Action.reload, Action.badminton, Action.golf, Action.fencing, Action.boxing]

def ai_process(relay_to_ai_queue, ai_to_visualiser_queue, action_queue):
    while True:
        msg = relay_to_ai_queue.get() # receive message from relay client
        print(f"{Colour.GREEN}AI Process received message: {msg}{Colour.RESET}", end="\n\n")
        logging.info(f"AI Process received message: {msg}")
        data = {
            "player_id": msg["player_id"],
            "action": msg["action"],
            "see_opponent": msg["ir_data"]
        }
        if msg["action"] != "bomb":
            print(f"{Colour.GREEN}AI Process sending message to Eval Client: {data}{Colour.RESET}", end="\n\n")
            logging.info(f"AI Process sending message to Eval Client: {data}")
            action_queue.put(data) # send message to eval client immediately
        else:
            print(f"{Colour.GREEN}AI Process sending message to Visualiser: {data}{Colour.RESET}", end="\n\n")
            logging.info(f"AI Process sending message to Visualiser: {data}")
            ai_to_visualiser_queue.put(data) # send message to visualiser to query