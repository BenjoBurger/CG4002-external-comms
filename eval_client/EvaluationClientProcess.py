from eval_client.EvaluationClient import EvaluationClient

def eval_client_process(ai_to_eval_queue, eval_to_visualiser_queue, eval_to_hardware_queue, eval_client_to_server_queue):
    server_name = input("Enter the server name: ")
    server_port = int(input("Enter the server port: "))
    eval_client = EvaluationClient(server_name, server_port)

    while True:
        pass