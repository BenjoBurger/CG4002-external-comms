import sys
from eval_client.EvaluationClientProcess import eval_client_process
from mqtt.MQTTClientProcess import mqtt_client_process
from mqtt.MQTTServerProcess import mqtt_server_process
from relay_node.RelayServerProcess import relay_server_process
from ai.AIProcess import ai_process
from multiprocessing import Process, Queue

RELAY_PORT = 8000
AI_PORT = 9010

def main():
    server_port = int(input("Enter the server port: "))
    
    try:
        # Create queues
        relay_to_ai_queue = Queue()
        ai_to_visualiser_queue = Queue()
        action_queue = Queue()
        eval_to_visualiser_queue = Queue()
        eval_to_relay_queue = Queue()

        # Create threads
        relay_thread = Process(target=relay_server_process, args=(RELAY_PORT, relay_to_ai_queue, eval_to_relay_queue))
        ai_thread = Process(target=ai_process, args=(relay_to_ai_queue, ai_to_visualiser_queue, action_queue))
        to_visualiser_thread = Process(target=mqtt_client_process, args=(ai_to_visualiser_queue, eval_to_visualiser_queue))
        from_visualiser_thread = Process(target=mqtt_server_process, args=(action_queue,))
        eval_thread = Process(target=eval_client_process, args=("localhost", server_port, action_queue, eval_to_visualiser_queue, eval_to_relay_queue))

        # Start threads
        relay_thread.start()
        ai_thread.start()
        from_visualiser_thread.start()
        to_visualiser_thread.start()
        eval_thread.start()

        relay_thread.join()
        ai_thread.join()
        to_visualiser_thread.join()
        from_visualiser_thread.join()
        eval_thread.join()

    except KeyboardInterrupt:
        print("Exiting")
        relay_thread.terminate()
        ai_thread.terminate()
        to_visualiser_thread.terminate()
        from_visualiser_thread.terminate()
        eval_thread.terminate()
        sys.exit()

if __name__ == "__main__":
    main()