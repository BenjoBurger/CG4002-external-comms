import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from RelayClient import RelayClient 
from multiprocessing import Process, Queue

def relay_client_process(server_ip, beetle_to_relay_queue, relay_to_beetle_queue):
    relay_client = RelayClient(server_ip, 8000)
    print(f"Relay Client Connected", end="\n\n")
    try:
        while True:
            data = beetle_to_relay_queue.get()
            relay_client.send_message(data)
            try:
                recv_data = relay_client.recv_message()
                print(f"Data received: {recv_data}", end="\n\n")
                json_data = json.loads(recv_data)
                if json_data["p1"] == "logout":
                    print(f"Player 1 has logged out", end="\n\n")
                if json_data["p2"] == "logout":
                    print(f"Player 2 has logged out", end="\n\n")
                relay_to_beetle_queue.put(json_data)
            except TimeoutError:
                print(f"Timeout: No response received within {relay_client.timeout} seconds", end="\n\n")
                continue
            except Exception as e:
                print(f"Error in relay_client_process: {e}", end="\n\n")
                raise e
    except Exception as e:
        print(f"Error in relay_client_process: {e}", end="\n\n")
        raise e

if __name__ == "__main__":
    num_players = int(input("Enter the number of players: "))
    server_ip = input("Enter the server ip: ")
    if server_ip == "u96":
        server_ip = "172.26.190.163"
    try:
        beetle_to_relay_queue = Queue()
        relay_to_beetle_queue = Queue()
        relay_client_thread = Process(target=relay_client_process, args=(server_ip, beetle_to_relay_queue, relay_to_beetle_queue))
        relay_client_thread.start()
        relay_client_thread.join()

    except KeyboardInterrupt:
        print("Exiting")
        relay_client_thread.terminate()
        sys.exit()