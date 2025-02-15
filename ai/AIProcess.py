from random import Random
from utilities.Action import Action
from utilities.Colour import Colour

action_list = [Action.shield, Action.shoot, Action.bomb, Action.reload, Action.badminton, Action.golf, Action.fencing, Action.boxing]

def ai_process(eval_to_ai_queue, ai_to_visualiser_queue, action_queue):
    while True:
        msg = eval_to_ai_queue.get()
        print(f"{Colour.GREEN}AI Process received message: {msg}{Colour.RESET}", end="\n\n")
        data = {
            "player_id": msg["player_id"],
            "action": "bomb",
            "see_opponent": msg["ir_data"]
        }
        if msg["action"] != "bomb":
            idx = Random().randint(0, 7)
            data["action"] = action_list[idx]
            action_queue.put(data)
        else:
            print(f"{Colour.GREEN}AI Process sending message: {data}{Colour.RESET}", end="\n\n")
            ai_to_visualiser_queue.put(data)