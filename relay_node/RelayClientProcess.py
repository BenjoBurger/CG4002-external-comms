import json
import os
import sys
from random import Random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from relay_node.RelayClient import RelayClient 
from utilities.Colour import Colour
from utilities.Action import Action

def relay_client_process(num_players=1, server_ip="localhost"):
    relay_client = RelayClient(server_ip, 8000)
    if num_players == 1:
        players_list = [1]
    else:
        players_list = [1, 2]
    try:
        while True:
            for player in players_list:
                while True:
                    user_action = input("> ")
                    if user_action in Action.values(): # check if the action is valid
                        break
                    print(f"{Colour.RED}Invalid action{Colour.RESET}")
                    
                # create dummy data
                data = {
                    "player_id": player,
                    "action": user_action,
                    "ir_data": 1,
                    "gyro_data": 
                    {
                        "x": Random().randint(0, 100),
                        "y": Random().randint(0, 100),
                        "z": Random().randint(0, 100),
                    },
                    "accel_data": 
                    {
                        "x": Random().randint(0, 100),
                        "y": Random().randint(0, 100),
                        "z": Random().randint(0, 100),
                    },
                }
                relay_client.send_message(json.dumps(data))
                recv_data = relay_client.recv_message()
                print(f"{Colour.CYAN}data received: {recv_data}{Colour.RESET}", end="\n\n")
                if user_action == Action.logout:
                    relay_client.close()
                    return
    except Exception as e:
        print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
        raise e

if __name__ == "__main__":
    num_players = int(input("Enter the number of players: "))
    server_ip = input("Enter the server ip: ")
    relay_client_process(num_players, server_ip)