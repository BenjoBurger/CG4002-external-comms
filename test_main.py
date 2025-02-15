from multiprocessing import Process, Queue
from eval_client.EvaluationClient import EvaluationClient
from eval_client.ClientGameState import ClientGameState
from eval_client.EvaluationClientProcess import relay_to_eval

def main(server_name, server_port):
    eval_client = EvaluationClient(server_name, server_port)
    client_game_state = ClientGameState()
    while True:
        action = input("Enter action: ")
        message = {
            "player_id": 1,
            "action": action,
            "see_opponent": 1
        }
        relay_to_eval(message, eval_client, client_game_state)

if __name__ == "__main__":
    server_port = int(input("Enter the server port: "))
    main("localhost", server_port)