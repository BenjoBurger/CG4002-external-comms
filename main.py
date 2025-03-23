import sys
from eval_client.EvaluationClientProcess import eval_client_process
from mqtt.MQTTClientProcess import mqtt_client_process
from mqtt.MQTTServerProcess import mqtt_server_process
from relay_node.RelayServerProcess import relay_server_process
from ai.AIProcess import ai_process
from multiprocessing import Process, Queue, Value

# P1_RELAY_PORT = 8000
# P2_RELAY_PORT = 8002
RECV_PORT = 8000
SEND_PORT = 8010
AI_PORT = 9010
SERVER_ADDR = "localhost"

def main():
    server_port = int(input("Enter the server port: "))
    num_players = int(input("Enter the number of players: "))
    
    try:
        # Create queues
        relay_to_ai_queue = Queue()
        ai_to_visualiser_queue = Queue()
        action_queue = Queue()
        eval_to_visualiser_queue = Queue()
        eval_to_relay_queue = Queue()
        # eval_to_relay_1_queue.get(block=False, timeout=0.1)

        # Create flags for checking client connections
        is_relay_client_1_connected = Value('b', False)
        is_relay_client_2_connected = Value('b', False)
        is_ai_client_connected = Value('b', False)
        is_mqtt_client_connected = Value('b', False)
        is_mqtt_server_connected = Value('b', False)

        # Create threads
        from_relay_client_thread = Process(target=relay_server_process, args=(RECV_PORT, relay_to_ai_queue, eval_to_relay_queue, is_relay_client_1_connected))
        to_relay_client_thread = Process(target=relay_server_process, args=(SEND_PORT, relay_to_ai_queue, eval_to_relay_queue, is_relay_client_2_connected))
        ai_thread = Process(target=ai_process, args=(relay_to_ai_queue, ai_to_visualiser_queue, action_queue, eval_to_relay_queue, is_ai_client_connected))
        to_visualiser_thread = Process(target=mqtt_client_process, args=(ai_to_visualiser_queue, eval_to_visualiser_queue, is_mqtt_client_connected))
        from_visualiser_thread = Process(target=mqtt_server_process, args=(action_queue, is_mqtt_server_connected))
        eval_thread = Process(target=eval_client_process, args=(SERVER_ADDR, server_port, action_queue, eval_to_visualiser_queue, eval_to_relay_queue, is_relay_client_1_connected, is_relay_client_2_connected, is_ai_client_connected, is_mqtt_client_connected, is_mqtt_server_connected, num_players))

        # Start threads
        from_relay_client_thread.start()
        to_relay_client_thread.start()
        ai_thread.start()
        from_visualiser_thread.start()
        to_visualiser_thread.start()
        eval_thread.start()

        from_relay_client_thread.join()
        to_relay_client_thread.join()
        ai_thread.join()
        to_visualiser_thread.join()
        from_visualiser_thread.join()
        eval_thread.join()

    except KeyboardInterrupt:
        print("Exiting")
        from_relay_client_thread.terminate()
        to_relay_client_thread.terminate()
        ai_thread.terminate()
        to_visualiser_thread.terminate()
        from_visualiser_thread.terminate()
        eval_thread.terminate()
        sys.exit()

if __name__ == "__main__":
    main()