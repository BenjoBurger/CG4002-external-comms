import json
from relay_node.RelayServer import RelayServer
from utilities.Colour import Colour

def ai_server_process():
    try:
        ai_server = RelayServer(9010)
        print(f"{Colour.CYAN}AI Server Connected{Colour.RESET}", end="\n\n")
        while True:
            conn_socket, client_addr = ai_server.client.accept()
            print(f"{Colour.CYAN}AI Client connected: {client_addr}{Colour.RESET}", end="\n\n")
            while True:
                try:
                    print(f"{Colour.CYAN}Waiting for message from AI Client{Colour.RESET}", end="\n\n")
                    data = ai_server.recv_message(conn_socket)
                    message = json.loads(data)
                    # AI logic goes here
                    ai_server.send_message(message, conn_socket)
                    print(f"{Colour.CYAN}Received message from AI Client: {data}{Colour.RESET}", end="\n\n")
                except Exception as e:
                    print(f"{Colour.RED}Error in AI Server: {e}{Colour.RESET}", end="\n\n")
                    break
    except Exception as e:
        print(f"{Colour.RED}Error in relay_server_process: {e}{Colour.RESET}", end="\n\n")
        raise e
    finally:
        ai_server.client.close()
        print(f"{Colour.CYAN}Relay Server Closed{Colour.RESET}", end="\n\n")

if __name__ == "__main__":
    ai_server_process()