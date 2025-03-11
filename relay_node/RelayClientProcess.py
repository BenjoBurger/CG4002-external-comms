import json
import os
import sys
from random import Random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from relay_node.RelayClient import RelayClient 
from utilities.Colour import Colour
from utilities.Action import Action
from utilities.Dummy import dummy_packet_list

def relay_client_process(num_players=1, server_ip="localhost"):
    relay_client = RelayClient(server_ip, 8000)
    print(f"{Colour.CYAN}Relay Client Connected{Colour.RESET}", end="\n\n")
    if num_players == 1:
        players_list = [1]
    else:
        players_list = [1, 2]
    try:
        while True:
            for player in players_list:
                data = None
                user_action = input("> ")
                # while True:
                #     user_action = input("> ")
                #     if user_action == "dummy":
                #         data = dummy_packet_list[Random().randint(0, len(dummy_packet_list) - 1)]
                #         break
                #     if user_action in Action.values(): # check if the action is valid
                #         break
                #     print(f"{Colour.RED}Invalid action{Colour.RESET}")
                # if data is None:
                    # create dummy data
                data = {
                    "player_id": player,
                    "gun_fired": False,
                    "IR_Sensor": False,
                    "imu_data": [1264, 53412, 53768, 8691, 13664, 1207, 16752, 2488, 2400, 9094, 13442, 57796, 2328, 46772, 660, 1228, 63111, 206],
                }
                relay_client.send_message(json.dumps(data))
                try:
                    recv_data = relay_client.recv_message()
                    print(f"{Colour.CYAN}Data received: {recv_data}{Colour.RESET}", end="\n\n")
                    if user_action == Action.logout:
                        relay_client.close()
                        return
                except TimeoutError:
                    print(f"{Colour.RED}Timeout: No response received within {relay_client.timeout} seconds{Colour.RESET}", end="\n\n")
                    continue
                except Exception as e:
                    print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
                    raise e
    except Exception as e:
        print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
        raise e

if __name__ == "__main__":
    num_players = int(input("Enter the number of players: "))
    server_ip = input("Enter the server ip: ")
    if server_ip == "u96":
        server_ip = "172.26.190.163"
    relay_client_process(num_players, server_ip)