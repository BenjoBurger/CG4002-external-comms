import sys
import json
from eval_client.EvaluationClientProcess import eval_client_process
from mqtt.MQTTClientProcess import mqtt_client_process
from mqtt.MQTTServerProcess import mqtt_server_process
from relay_node.RelayServerProcess import relay_server_process
from ai.AIProcess import ai_process
from utilities.Action import shield_command, gun_command, reload_command, bomb_command, badminton_command, boxing_command, fencing_command, golf_command
from multiprocessing import Process, Queue

def main():
    server_port = int(input("Enter the server port: "))
    try:
        # Create queues
        p1_to_relay_queue = Queue()
        p2_to_relay_queue = Queue()

        relay_to_ai_queue = Queue()
        ai_to_visualiser_queue = Queue()
        action_queue = Queue()

        eval_client_to_server_queue =  Queue()
        eval_to_visualiser_queue = Queue()
        eval_to_hardware_queue = Queue()

        # Create threads
        relay_thread = Process(target=relay_server_process, args=(8000, p1_to_relay_queue, p2_to_relay_queue, relay_to_ai_queue))
        ai_thread = Process(target=ai_process, args=(relay_to_ai_queue, ai_to_visualiser_queue, action_queue))
        to_visualiser_thread = Process(target=mqtt_client_process, args=(ai_to_visualiser_queue,))
        from_visualiser_thread = Process(target=mqtt_server_process, args=(action_queue,))
        eval_thread = Process(target=eval_client_process, args=("127.0.0.1", server_port, action_queue, eval_client_to_server_queue, eval_to_visualiser_queue, eval_to_hardware_queue))

        # # Start threads
        relay_thread.start()
        ai_thread.start()
        from_visualiser_thread.start()
        to_visualiser_thread.start()
        eval_thread.start()

        relay_thread.join()
        ai_thread.join()
        to_visualiser_thread.join()
        from_visualiser_thread.join()
        eval_thread.join()

    except KeyboardInterrupt:
        print("Exiting")
        relay_thread.terminate()
        ai_thread.terminate()
        to_visualiser_thread.terminate()
        from_visualiser_thread.terminate()
        eval_thread.terminate()
        sys.exit()

def relay_to_eval(ai_action, eval_client, client_game_state, player1, player2):
    while True:
        if ai_action == eval_client.DISCONNECT_MESSAGE:
            eval_client.client.close()
            break
        if ai_action == "shield":
            shield_command(player1)
            # action = "shield"
        elif ai_action == "gun":
            gun_command(player1, player2)
            # action = "gun"
        elif ai_action == "reload":
            reload_command(player1)
            # action = "reload"
        elif ai_action == "bomb":
            bomb_command(player1, player2)
            # action = "bomb"
        elif ai_action == "badminton":
            badminton_command(player1, player2)
            # action = "badminton"
        elif ai_action == "boxing":
            boxing_command(player1, player2)
            # action = "boxing"
        elif ai_action == "fencing":
            fencing_command(player1, player2)
            # action = "fencing"
        elif ai_action == "golf":
            golf_command(player1, player2)
            # action = "golf"
        elif ai_action == "logout":
            # action = "logout"
            print("Logging out")
            break
        else:
            print("Invalid command")
            continue
        eval_client.send_server(create_message(ai_action, player1, player2))
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