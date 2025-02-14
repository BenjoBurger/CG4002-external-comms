from random import Random
from utilities.Action import Action

action_list = [Action.shield, Action.shoot, Action.bomb, Action.reload, Action.badminton, Action.golf, Action.fencing, Action.boxing]

def ai_process(eval_to_ai_queue, ai_to_visualiser_queue, action_queue):
    while True:
        msg = eval_to_ai_queue.get()
        print(f"AI Process received message: {msg}")
        idx = Random().randint(0, 7)
        data = {
            "player_id": msg["player_id"],
            "action": "bomb",
            "see_opponent": msg["ir_data"]
        }
        if data["action"] == Action.bomb:
            ai_to_visualiser_queue.put(data)
        else:
            action_queue.put(data)