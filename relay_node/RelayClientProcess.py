from RelayClient import RelayClient 
from queue import Queue
import json
from random import Random

def relay_client_process(num_players=1):
    relay_client = RelayClient("localhost", 8000)
    if num_players == 1:
        players_list = ["p1"]
    else:
        players_list = ["p1", "p2"]
    try:
        while True:
            for player in players_list:
                user_action = input("> ")
                data = {
                    "player_id": player,
                    "action": user_action,
                    "ir_data": Random().randint(0, 1),
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
                if user_action == "logout":
                    break
                relay_client.send_message(json.dumps(data))
                recv_data = relay_client.recv_message()
                print("data received:", recv_data)
    except Exception as e:
        print(f"Error in relay_client_process: {e}")
        raise e

if __name__ == "__main__":
    num_players = int(input("Enter the number of players: "))
    relay_client_process(num_players)