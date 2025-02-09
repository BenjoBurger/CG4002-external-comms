import asyncio
import sys
import json
import socket
from EvaluationClient import EvaluationClient
from MQTTClient import MQTTClient
from MQTTServer import MQTTServer
from ClientGameState import ClientGameState

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <server_name> <server_port>")
        sys.exit(1)
    
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    eval_client = EvaluationClient(server_name, server_port)

    mqtt_client = MQTTClient()
    mqtt_client.subscribe("game")
    mqtt_server = MQTTServer()
    mqtt_server.publish("Hello from client!")

    client_game_state = ClientGameState()
    player1 = client_game_state.player1
    player2 = client_game_state.player2

    while True:
        user_input = input("> ")
        if user_input == eval_client.DISCONNECT_MESSAGE:
            eval_client.client.close()
            break
        if user_input == "she":
            send_shield(eval_client, player1, player2)
        elif user_input == "gun":
            send_gun(eval_client, player1, player2)
        elif user_input == "r":
            send_reload(eval_client, player1, player2)
        elif user_input == "bomb":
            send_bomb(eval_client, player1, player2)
        elif user_input == "bado":
            send_badminton(eval_client, player1, player2)
        elif user_input == "box":
            send_boxing(eval_client, player1, player2)
        elif user_input == "fen":
            send_fencing(eval_client, player1, player2)
        elif user_input == "golf":
            send_golf(eval_client, player1, player2)
        elif user_input == "logout":
            print("Logging out")
            break
        else:
            print("Invalid command")
            continue
        data = eval_client.recv_server()
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

def send_shield(client, curr_player, opponent):
    curr_player.shield()
    client.send_server(create_message("shield", curr_player, opponent))

def send_gun(client, curr_player, opponent):
    curr_player.shoot(opponent, True)
    client.send_server(create_message("gun", curr_player, opponent))

def send_reload(client, curr_player, opponent):
    curr_player.reload()
    client.send_server(create_message("reload", curr_player, opponent))

def send_bomb(client, curr_player, opponent):
    curr_player.bomb(opponent, True)
    client.send_server(create_message("bomb", curr_player, opponent))

def send_badminton(client, curr_player, opponent):
    curr_player.badminton(opponent, True)
    client.send_server(create_message("badminton", curr_player, opponent))

def send_boxing(client, curr_player, opponent):
    curr_player.boxing(opponent, True)
    client.send_server(create_message("boxing", curr_player, opponent))

def send_fencing(client, curr_player, opponent):
    curr_player.fencing(opponent, True)
    client.send_server(create_message("fencing", curr_player, opponent))

def send_golf(client, curr_player, opponent):
    curr_player.golf(opponent, True)
    client.send_server(create_message("golf", curr_player, opponent))

if __name__ == "__main__":
    main()