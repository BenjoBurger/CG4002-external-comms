from relay_node.RelayServer import RelayServer
import json

def relay_server_process(server_port, p1_to_relay_queue, p2_to_relay_queue, relay_to_ai_queue):
    try:
        relay_node_server = RelayServer(server_port)
        while True:
            conn_socket, client_addr = relay_node_server.client.accept()
            handler(relay_to_ai_queue, relay_node_server, conn_socket, client_addr)
    except Exception as e:
        print(f"Error in relay_server_process: {e}")
        raise e
    finally:
        relay_node_server.client.close()
        print("Relay Server Closed")

def handler(relay_to_ai_queue, relay_node_server, conn_socket, client_addr):
    while True:
        try:
            while True:
                data = relay_node_server.recv_message(conn_socket)
                message = json.loads(data)
                print(f"Received message: {message}")
                relay_to_ai_queue.put(message)
                relay_node_server.send_message(json.dumps(message), conn_socket)
        except Exception as e:
            print(f"Error in relay server handler: {e}")
            raise e
        finally:
            conn_socket.close()
            print(f"Connection closed: {client_addr}")
            break
