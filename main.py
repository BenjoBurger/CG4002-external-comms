import sys
import json
from eval_client.EvaluationClientProcess import eval_client_process
from mqtt.MQTTClientProcess import mqtt_client_process
from mqtt.MQTTServerProcess import mqtt_server_process
from relay_node.RelayServerProcess import relay_server_process
from ai.AIProcess import ai_process
from utilities.Action import shield_command, gun_command, reload_command, bomb_command, badminton_command, boxing_command, fencing_command, golf_command
from multiprocessing import Process, Queue

# threadLock = threading.Lock()

def main():
    try:
        # Create queues
        p1_to_relay_queue = Queue()
        p2_to_relay_queue = Queue()

        relay_to_eval_queue = Queue()

        relay_to_ai_queue = Queue()
        ai_to_eval_queue = Queue()

        eval_client_to_server_queue =  Queue()

        eval_to_visualiser_queue = Queue()
        visualiser_to_eval_queue = Queue()
        eval_to_hardware_queue = Queue()

        # Create threads
        relay_thread = Process(target=relay_server_process, args=(8000, p1_to_relay_queue, p2_to_relay_queue, relay_to_ai_queue))
        # ai_thread = Process(target=ai_process, args=(relay_to_ai_queue, ai_to_eval_queue))
        # eval_thread = Process(target=eval_client_process, args=(ai_to_eval_queue, eval_to_visualiser_queue, eval_to_hardware_queue, eval_client_to_server_queue))
        # eval_to_visualiser_thread = Process(target=mqtt_client_process, args=(eval_to_visualiser_queue))
        # visualiser_to_eval_thread = Process(target=mqtt_server_process, args=(visualiser_to_eval_queue))

        # # Start threads
        relay_thread.start()
        # ai_thread.start()
        # eval_thread.start()
        # eval_to_visualiser_thread.start()
        # visualiser_to_eval_thread.start()

        relay_thread.join()
        # ai_thread.join()
        # eval_thread.join()
        # eval_to_visualiser_thread.join()
        # visualiser_to_eval_thread.join()
    except KeyboardInterrupt:
        print("Exiting")
        relay_thread.terminate()
        # ai_thread.terminate()
        # eval_thread.terminate()
        # eval_to_visualiser_thread.terminate()
        # visualiser_to_eval_thread.terminate()
        sys.exit()

def relay_to_eval(eval_client, client_game_state, player1, player2):
    while True:
        user_action = input("> ")
        action = ""
        if user_action == eval_client.DISCONNECT_MESSAGE:
            eval_client.client.close()
            break
        if user_action == "shi":
            shield_command(player1)
            action = "shield"
        elif user_action == "gun":
            gun_command(player1, player2)
            action = "gun"
        elif user_action == "rel":
            reload_command(player1)
            action = "reload"
        elif user_action == "bomb":
            bomb_command(player1, player2)
            action = "bomb"
        elif user_action == "bad":
            badminton_command(player1, player2)
            action = "badminton"
        elif user_action == "box":
            boxing_command(player1, player2)
            action = "boxing"
        elif user_action == "fen":
            fencing_command(player1, player2)
            action = "fencing"
        elif user_action == "golf":
            golf_command(player1, player2)
            action = "golf"
        elif user_action == "logout":
            action = "logout"
            print("Logging out")
            break
        else:
            print("Invalid command")
            continue
        eval_client.send_server(create_message(action, player1, player2))
        data = eval_client.recv_message()
        print("data received:", data)
        client_game_state.update_game_state(json.loads(data))
        
def create_message(action, curr_player, opponent):

    message = {
        "player_id": curr_player.get_id(),
        "action": action,
        "game_state": {
            "p1": curr_player.get_dict(),
            "p2": opponent.get_dict()
        }
    }
    return json.dumps(message).encode("utf-8")

if __name__ == "__main__":
    main()