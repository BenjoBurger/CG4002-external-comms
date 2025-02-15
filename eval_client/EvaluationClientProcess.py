from eval_client.EvaluationClient import EvaluationClient
import json
from utilities.Action import shield_command, gun_command, reload_command, bomb_command, badminton_command, boxing_command, fencing_command, golf_command
from eval_client.ClientGameState import ClientGameState
from utilities.Colour import Colour

def eval_client_process(server_name, server_port, action_queue, eval_to_visualiser_queue, eval_to_relay_queue):
    eval_client = EvaluationClient(server_name, server_port)
    client_game_state = ClientGameState()
    handle(eval_client, client_game_state, action_queue, eval_to_visualiser_queue, eval_to_relay_queue)

def handle(eval_client, client_game_state, action_queue, eval_to_visualiser_queue, eval_to_relay_queue):
    while True:
        try:
            while True:
                if not action_queue.empty():
                    message = action_queue.get()
                    print(f"{Colour.ORANGE}Eval Client received message: {message}{Colour.RESET}", end="\n\n")
                    relay_to_eval(message, eval_client, client_game_state,)
                    eval_to_visualiser_queue.put(client_game_state.get_dict())
                    eval_to_relay_queue.put(client_game_state.get_dict())
        except Exception as e:
            print(f"{Colour.RED}Error in eval_client_process: {e}{Colour.RESET}", end="\n\n")
            raise e
        finally:           
            eval_client.client.close()
            print(f"{Colour.ORANGE}Eval Client Closed{Colour.RESET}", end="\n\n")

def relay_to_eval(ai_packet, eval_client, client_game_state):
    player1 = client_game_state.player1
    player2 = client_game_state.player2
    success = do_action(ai_packet, player1, player2)
    if not success:
        print(f"{Colour.ORANGE}Logout action{Colour.RESET}", end="\n\n")
        eval_client.client.close()
        return
    print(f"{Colour.ORANGE}Sending data to Eval Server{Colour.RESET}", end="\n\n")
    eval_client.send_server(create_message(ai_packet["action"], player1, player2))
    data = eval_client.recv_message()
    print(f"{Colour.ORANGE}Data received from Eval Server: {data}{Colour.RESET}", end="\n\n")
    client_game_state.update_game_state(json.loads(data))

def do_action(ai_packet, player1, player2):
    ai_action = ai_packet["action"]
    see_opponent = ai_packet["see_opponent"]
    success = True
    print(f"{Colour.ORANGE}Performing action: {ai_action}{Colour.RESET}", end="\n\n")
    if ai_action == "shield":
        shield_command(player1)
        # action = "shield"
    elif ai_action == "gun":
        gun_command(player1, player2, see_opponent)
        # action = "gun"
    elif ai_action == "reload":
        reload_command(player1)
        # action = "reload"
    elif ai_action == "bomb":
        bomb_command(player1, player2, see_opponent)
        # action = "bomb"
    elif ai_action == "badminton":
        badminton_command(player1, player2, see_opponent)
        # action = "badminton"
    elif ai_action == "boxing":
        boxing_command(player1, player2, see_opponent)
        # action = "boxing"
    elif ai_action == "fencing":
        fencing_command(player1, player2, see_opponent)
        # action = "fencing"
    elif ai_action == "golf":
        golf_command(player1, player2, see_opponent)
        # action = "golf"
    else:
        success = False
    return success

def create_message(action, curr_player, opponent):
    message = {
        "player_id": curr_player.id,
        "action": action,
        "game_state": {
            "p1": curr_player.get_dict(),
            "p2": opponent.get_dict()
        }
    }
    return json.dumps(message)