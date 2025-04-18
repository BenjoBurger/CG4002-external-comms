import json
import os
import sys
import time
from random import Random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from relay_node.RelayClient import RelayClient 
from utilities.Colour import Colour
from utilities.Action import Action
from multiprocessing import Process, Queue, Value

# P1_PORT = 8000
# P2_PORT = 8002
SEND_PORT = 8000
RECV_PORT = 8080

def relay_client_process(server_ip, port_number, queue=None, check_client=None):
    if port_number == SEND_PORT:
        send_to_relay(server_ip, port_number, queue, check_client)
    else:
        recv_from_relay(server_ip, port_number, queue, check_client)

def send_to_relay(server_ip, port_number, action_queue, sending_client):
    relay_client = RelayClient(server_ip, port_number)
    print(f"{Colour.CYAN}Sending Relay Client Connected{Colour.RESET}", end="\n\n")
    if sending_client is not None:
        with sending_client.get_lock():
            sending_client.value = True
    try:
        while True:
            # Action data from internal comms
            data = action_queue.get()
            # print("Data: ", data)
            if data is not None:
                relay_client.send_message(json.dumps(data))
    except BrokenPipeError:
        while True:
            try:
                relay_client = RelayClient(server_ip, port_number)
                print(f"{Colour.CYAN}Relay Client Connected{Colour.RESET}", end="\n\n")
                break
            except Exception as e:
                print(f"{Colour.RED}Error in reconnecting: {e}{Colour.RESET}", end="\n\n")
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"{Colour.CYAN}Exiting Sending Relay Client Process{Colour.RESET}", end="\n\n")
        relay_client.close()
    except Exception as e:
        print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
        raise e

def recv_from_relay(server_ip, port_number, queue, receiving_client):
    relay_client = RelayClient(server_ip, port_number)
    print(f"{Colour.CYAN}Receiving Relay Client Connected{Colour.RESET}", end="\n\n")
    if receiving_client is not None:
        with receiving_client.get_lock():
            receiving_client.value = True
    time.sleep(10)
    try:
        while True:
            try:
                # Receive data from relay server
                recv_data = relay_client.recv_message()
                if recv_data == "" or recv_data == "ping":
                    continue
                # print(f"{Colour.CYAN}Data received: {recv_data}{Colour.RESET}", end="\n\n")
                queue.put(recv_data)
            except Exception as e:
                print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
                raise e
    except BrokenPipeError:
        while True:
            try:
                relay_client = RelayClient(server_ip, port_number)
                print(f"{Colour.CYAN}Relay Client Connected{Colour.RESET}", end="\n\n")
                break
            except Exception as e:
                print(f"{Colour.RED}Error in reconnecting: {e}{Colour.RESET}", end="\n\n")
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"{Colour.CYAN}Exiting Receiving Relay Client Process{Colour.RESET}", end="\n\n")
        relay_client.close()
    except Exception as e:
        print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
        raise e
    
def action_input(beetle_to_relay, sending_client, receiving_client):
    while True:
        if sending_client.value and receiving_client.value:
            print(f"{Colour.GREEN}Relay Clients Connected{Colour.RESET}", end="\n\n")
            break
    time.sleep(10)
    user_action =   [["shield", "badminton", "boxing", "fencing", "golf"],
                    ["shield", "badminton", "boxing", "fencing", "golf"]]
    count = 0
    while True:
        # data = {
        #         "player_id": 1,
        #         "gun_fired": False,
        #         "IR_Sensor": 0,
        #         "imu_data": "badminton",
        #     }
            # print("user_action: ", user_action[j-1][i])
            # if user_action[j-1][i] == "shoot":
            #     data["gun_fired"] = True
            # elif user_action[j-1][i] == "shot":
            #     data["IR_Sensor"] = 1
        # beetle_to_relay.put(data)
        # time.sleep(5)
        for i in range(len(user_action[0])):
            for j in [1, 2]:
                data = {
                    "player_id": j,
                    "gun_fired": False,
                    "IR_Sensor": 0,
                    "imu_data": user_action[j-1][i],
                }
                print(f"player {j}: {user_action[j-1][i]}")
                if user_action[j-1][i] == "shoot":
                    data["gun_fired"] = True
                elif user_action[j-1][i] == "shot":
                    data["IR_Sensor"] = 1
                beetle_to_relay.put(data)
            time.sleep(5)

if __name__ == "__main__":
    try:
        server_ip = input("Enter the server ip: ")
        if server_ip == "u96":
            server_ip = "172.26.191.109"
        if server_ip == "":
            server_ip = "localhost"
        
        beetle_to_relay = Queue()
        relay_to_beetle = Queue()

        sending_client = Value('b', True)
        receiving_client = Value('b', False)

        send_process = Process(target=relay_client_process, args=(server_ip, SEND_PORT, beetle_to_relay, sending_client))
        recv_process = Process(target=relay_client_process, args=(server_ip, RECV_PORT, relay_to_beetle, receiving_client))
        input_process = Process(target=action_input, args=(beetle_to_relay, sending_client, receiving_client))

        send_process.start()
        recv_process.start()
        input_process.start()
        # action_input(action_queue, sending_client, receiving_client)
        
        send_process.join()
        recv_process.join()
        input_process.join()

    except KeyboardInterrupt:
        print("Exiting")
        send_process.terminate()
        recv_process.terminate()
        input_process.terminate()
        sys.exit()