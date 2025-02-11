import sys
import json
from EvaluationClient import EvaluationClient
# from MQTTClient import MQTTClient
# from MQTTServer import MQTTServer
from ClientGameState import ClientGameState
from Action import shield_command, gun_command, reload_command, bomb_command, badminton_command, boxing_command, fencing_command, golf_command
# from queue import Queue
# import threading

# threadLock = threading.Lock()

def main():
    server_name = ""
    server_port = 0

    if len(sys.argv) < 3:
        server_name = "127.0.0.1"
        server_port = 8888
    else:    
        server_name = sys.argv[1]
        server_port = int(sys.argv[2])

    eval_client = EvaluationClient(server_name, server_port)

    # mqtt_client = MQTTClient()
    # mqtt_server = MQTTServer()

    client_game_state = ClientGameState()
    player1 = client_game_state.player1
    player2 = client_game_state.player2

    # eval_server_queue =  Queue()
    # visualiser_queue = Queue()
    # hardware_queue = Queue()

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
        
def create_message(action, player1, player2):
    message = {
        "player_id": "1",
        "action": action,
        "game_state": {
            "p1": player1.get_dict(),
            "p2": player2.get_dict()
        }
    }
    return json.dumps(message).encode("utf-8")

if __name__ == "__main__":
    main()