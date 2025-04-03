import queue
import traceback
from relay_node.RelayServer import RelayServer
import json
from utilities.Colour import Colour

SERVER_PORT = 8000
P1_ACTION_DONE = False
P2_ACTION_DONE = False

def relay_server_process(server_port, relay_to_ai_queue, eval_to_relay_queue, p1_shot_queue, p2_shot_queue, is_relay_client_connected, num_players):
    global P2_ACTION_DONE
    P2_ACTION_DONE = False if num_players == 2 else True
    if server_port == SERVER_PORT:
        recv_from_client(server_port, relay_to_ai_queue, p1_shot_queue, p2_shot_queue, is_relay_client_connected)
    else:
        send_to_client(server_port, eval_to_relay_queue, is_relay_client_connected, num_players)

def recv_from_client(server_port, relay_to_ai_queue, p1_shot_queue, p2_shot_queue, is_relay_client_connected):
    # relay_server = None
    try:
        while True:
            # Create a relay server
            try:
                relay_server = RelayServer(server_port)
                break
            except OSError as e:
                print(f"{Colour.RED}Error in connecting relay server: {e} {Colour.RESET}", end="\n\n")
                server_port += 1
                print(f"{Colour.RED}Trying to connect to Relay Server at PORT {server_port}...{Colour.RESET}", end="\n\n")
                continue
        print(f"{Colour.CYAN}Relay Server at PORT {server_port} Connected{Colour.RESET}", end="\n\n")

        while True:
            # Accept connection from relay client
            print(f"{Colour.CYAN}Waiting for Sending Relay Client to connect...{Colour.RESET}", end="\n\n")
            conn_socket, client_addr = relay_server.client.accept()
            
            print(f"{Colour.CYAN}Sending Relay Client connected{Colour.RESET}", end="\n\n")
            with is_relay_client_connected.get_lock():
                is_relay_client_connected.value = True
            
            while relay_server.is_socket_connected(conn_socket):
                try:
                    # receive message from relay client
                    data = relay_server.recv_message(conn_socket)
                    print(f"{Colour.CYAN}Received message from Relay Client{Colour.RESET}", end="\n\n")
                    # send message to ai client
                    message = json.loads(data)
                    if P1_ACTION_DONE is True and message["player_id"] == 1:
                        print(f"{Colour.RED}P1 already performed action{Colour.RESET}", end="\n\n")
                        continue
                    if P2_ACTION_DONE is True and message["player_id"] == 2:
                        print(f"{Colour.RED}P2 already performed action{Colour.RESET}", end="\n\n")
                        continue
                    
                    if message["IR_Sensor"] == 1:
                        if message["player_id"] == 1:
                            p1_shot_queue.put(message)
                        elif message["player_id"] == 2:
                            p2_shot_queue.put(message)
                        continue
                    else:
                        relay_to_ai_queue.put(message)
                    # relay_to_ai_queue.put(message)
                except Exception as e:
                    print(f"{Colour.RED}Error in receiving message: {e} {Colour.RESET}", end="\n\n")
                    break
    except Exception as e:
        print(f"{Colour.RED}Error in relay server process: {e} {Colour.RESET}", end="\n\n")
    finally:
        print(f"{Colour.CYAN}Exiting Relay Server Process{Colour.RESET}", end="\n\n")
        if relay_server is not None:
            relay_server.client.close()
            print(f"{Colour.CYAN}Relay Server {server_port} Closed{Colour.RESET}", end="\n\n")
        
def send_to_client(server_port, eval_to_relay_queue, is_relay_client_connected, num_players):
    relay_server = None
    try:
        # Create a relay server
        while True:
            try:
                relay_server = RelayServer(server_port)
                break
            except OSError as e:
                print(f"{Colour.RED}Error in connecting relay server: {e} {Colour.RESET}", end="\n\n")
                server_port += 1
                print(f"{Colour.RED}Trying to connect to Relay Server at PORT {server_port}...{Colour.RESET}", end="\n\n")
                continue
        print(f"{Colour.CYAN}Relay Server at PORT {server_port} Connected{Colour.RESET}", end="\n\n")
        
        while True:
            # Accept connection from relay client
            print(f"{Colour.CYAN}Waiting for Receiving Relay Client to connect...{Colour.RESET}", end="\n\n")
            conn_socket, client_addr = relay_server.client.accept()
            
            print(f"{Colour.CYAN}Receiving Relay Client connected{Colour.RESET}", end="\n\n")
            with is_relay_client_connected.get_lock():
                is_relay_client_connected.value = True
            
            while relay_server.is_socket_connected(conn_socket):
                try:
                    # Receive game state from eval client
                    message = eval_to_relay_queue.get(block=False, timeout=0.1)
                    # print(f"{Colour.CYAN}Received Game State from Eval Client{Colour.RESET}", end="\n\n")
                    if message is not None:
                        game_state = message["game_state"]
                        # print(f"{Colour.CYAN}Sending Game State to Relay Client{Colour.RESET}", end="\n\n")
                        if game_state["p1"] == "logout" and game_state["p2"] == "logout":
                            print(f"{Colour.CYAN}Logout action{Colour.RESET}", end="\n\n")
                            conn_socket.close()
                        else:
                            if message["player_id"] == 1:
                                global P1_ACTION_DONE
                                P1_ACTION_DONE = True
                            elif message["player_id"] == 2:
                                global P2_ACTION_DONE
                                P2_ACTION_DONE = True
                            if P1_ACTION_DONE is True and P2_ACTION_DONE is True:
                                print(f"{Colour.CYAN}Both players have completed their actions{Colour.RESET}", end="\n\n")
                                P1_ACTION_DONE = False
                                P2_ACTION_DONE = False if num_players == 2 else True
                            relay_server.send_message(json.dumps(game_state), conn_socket)
                        
                except queue.Empty:
                    # print(f"{Colour.CYAN}No Game State from Eval Client{Colour.RESET}", end="\n\n")
                    continue
                except Exception as e:
                    print(f"{Colour.RED}Error in sending relay server: {e} {Colour.RESET}", end="\n\n")
                    traceback.print_exc()
                    break
                # finally:
                #     conn_socket.close()
                #     print(f"{Colour.CYAN}Connection Sending Relay closed: {client_addr}{Colour.RESET}", end="\n\n")
                #     break
    finally:
        print(f"{Colour.CYAN}Exiting Relay Server Process{Colour.RESET}", end="\n\n")
        if relay_server is not None:
            relay_server.client.close()
            print(f"{Colour.CYAN}Relay Server {server_port} Closed{Colour.RESET}", end="\n\n")