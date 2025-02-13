from RelayClient import RelayClient 
from queue import Queue
import json

def relay_client_process():
    relay_client = RelayClient("localhost", 8000)
    try:
        while True:
            for player in ["p1", "p2"]:
                user_action = input("> ")
                data = {
                    "player_id": player,
                    "action": user_action
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
    relay_client_process()