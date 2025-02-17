from relay_node.RelayServer import RelayServer
import json
from utilities.Colour import Colour

def relay_server_process(server_port, relay_to_ai_queue, eval_to_relay_queue):
    try:
        relay_node_server = RelayServer(server_port)
        while True:
            conn_socket, client_addr = relay_node_server.client.accept()
            handler(relay_to_ai_queue, eval_to_relay_queue, relay_node_server, conn_socket, client_addr)
    except Exception as e:
        print(f"{Colour.RED}Error in relay_server_process: {e}{Colour.RESET}", end="\n\n")
        raise e
    finally:
        relay_node_server.client.close()
        print(f"{Colour.CYAN}Relay Server Closed{Colour.RESET}", end="\n\n")

def handler(relay_to_ai_queue, eval_to_relay_queue, relay_node_server, conn_socket, client_addr):
    while True:
        try:
            while True:
                data = relay_node_server.recv_message(conn_socket) # receive message from relay client
                message = json.loads(data)
                print(f"{Colour.CYAN}Received message from Relay Client: {message}{Colour.RESET}", end="\n\n")
                relay_to_ai_queue.put(message) # send message to ai client
                # relay_node_server.send_message(json.dumps(message), conn_socket)
                try:
                    game_state = eval_to_relay_queue.get() # receive game state from eval client
                    if game_state is not None:
                        print(f"{Colour.CYAN}Sending game state to Relay Client: {game_state}{Colour.RESET}", end="\n\n")
                        relay_node_server.send_message(json.dumps(game_state), conn_socket) # send game state to relay client
                except Exception as e:
                    print(f"{Colour.RED} Error in relay server handler: {e} {Colour.RESET}", end="\n\n")
                    break
        finally:
            conn_socket.close()
            print(f"{Colour.CYAN}Connection closed: {client_addr}{Colour.RESET}", end="\n\n")
            break
