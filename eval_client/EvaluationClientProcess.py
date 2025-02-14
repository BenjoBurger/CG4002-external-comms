from eval_client.EvaluationClient import EvaluationClient

def eval_client_process(server_name, server_port, action_queue, eval_client_to_server_queue, eval_to_visualiser_queue, eval_to_hardware_queue):
    message = action_queue.get()
    print(f"Eval Client received message: {message}")
    # eval_client = EvaluationClient(server_name, server_port)
    # handle(eval_client, action_queue, eval_client_to_server_queue, eval_to_visualiser_queue, eval_to_hardware_queue)

def handle(eval_client, action_queue, eval_client_to_server_queue, eval_to_visualiser_queue, eval_to_hardware_queue):
    while True:
        try:
            message = action_queue.get()
            print(f"Eval Client received message: {message}")
            # eval_client.send_message(message)
            # recv_data = eval_client.recv_message()
            # print(f"Data received: {recv_data}")
            # eval_to_visualiser_queue.put(recv_data)
            # eval_to_hardware_queue.put(recv_data)
        except Exception as e:
            print(f"Error in eval_client_process: {e}")
            raise e
        finally:
            if message == eval_client.DISCONNECT_MESSAGE:
                eval_client.client.close()
                break
    print("Eval Client Closed")