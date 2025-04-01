import json
from eval_client.EvaluationClient import EvaluationClient
from utilities.Action import shield_command, gun_command, reload_command, bomb_command, badminton_command, boxing_command, fencing_command, golf_command, snow_detection
from eval_client.ClientGameState import ClientGameState
from utilities.Colour import Colour

def eval_client_process(server_name, server_port, action_queue, eval_to_visualiser_queue, eval_to_relay_queue, is_relay_client_1_connected, is_relay_client_2_connected, is_ai_client_connected, is_mqtt_client_connected, is_mqtt_server_connected, num_players):
    while True:
        if is_relay_client_1_connected.value and is_relay_client_2_connected and is_ai_client_connected.value and is_mqtt_client_connected.value and is_mqtt_server_connected.value:
            print(f"{Colour.ORANGE}All Clients Connected{Colour.RESET}", end="\n\n")
            break
    eval_client = EvaluationClient(server_name, server_port)
    client_game_state = ClientGameState()
    handler(eval_client, client_game_state, action_queue, eval_to_visualiser_queue, eval_to_relay_queue, num_players)

def handler(eval_client, client_game_state, action_queue, eval_to_visualiser_queue, eval_to_relay_queue, num_players):
    p1_action = None
    p2_action = None if num_players == 2 else "Completed"
    while True:
        try:
            while True:
                # Process new action
                message = action_queue.get()
                print(f"{Colour.ORANGE}Eval Client received message{Colour.RESET}", end="\n\n")
                if message["player_id"] == 1 and p1_action is not None:
                    # print(f"{Colour.RED}Player 1 has completed their action{Colour.RESET}", end="\n\n")
                    continue
                if message["player_id"] == 2 and p2_action is not None:
                    # print(f"{Colour.RED}Player 2 has completed their action{Colour.RESET}", end="\n\n")
                    continue

                # Update game state and send to eval server
                action_completed = relay_to_eval(message, eval_client, client_game_state)

                # Check if player actions are completed
                if action_completed != -1:
                    if action_completed == 1:
                        p1_action = message["action"]
                    else:
                        p2_action = message["action"]

                    # Send game state to visualiser and relay
                    eval_to_visualiser_queue.put(client_game_state.get_dict())
                    eval_to_relay_queue.put(client_game_state.get_dict())

                    # Check if both players have completed their actions
                    if p1_action is not None and p2_action is not None:
                        p1_action = None
                        p2_action = None if num_players == 2 else "Completed"
                        clear_queue(action_queue)
                        
        except TimeoutError:
            print(f"{Colour.RED}eval_client_process: No response received within {eval_client.timeout} seconds{Colour.RESET}", end="\n\n")
            continue
        except Exception as e:
            print(f"{Colour.RED}Error in eval_client_process: {e}{Colour.RESET}", end="\n\n")
            raise e
        finally:           
            eval_client.client.close()
            print(f"{Colour.ORANGE}Eval Client Closed{Colour.RESET}", end="\n\n")

def clear_queue(queue):
    while not queue.empty():
        queue.get()

def relay_to_eval(packet, eval_client, client_game_state):
    curr_player_id = packet["player_id"]
    curr_player = None
    opponent = None
    
    if curr_player_id == 1:
        curr_player = client_game_state.player1
        opponent = client_game_state.player2
    else:
        curr_player = client_game_state.player2
        opponent = client_game_state.player1
    
    logout = do_action(packet, curr_player, opponent)
    
    message = create_message(packet["action"], curr_player_id, client_game_state)
    # print(f"{Colour.ORANGE}Sending Data to Eval Server{Colour.RESET}", end="\n\n")
    eval_client.send_server(message) # send game state to eval server
    try:
        data = eval_client.recv_message() # receive game state from eval server
        # print(f"{Colour.ORANGE}Data received from Eval Server{Colour.RESET}", end="\n\n")
        client_game_state.update_game_state(json.loads(data))
        if logout:
            # print(f"{Colour.ORANGE}Logout action{Colour.RESET}", end="\n\n")
            eval_client.client.close()
            return
        return curr_player_id
    except Exception as e:
        print(f"{Colour.RED}Error in relay_to_eval: {e}{Colour.RESET}", end="\n\n")
        return -1
    # except TimeoutError:
    #     print(f"{Colour.RED}eval_client_process: No response received within {eval_client.timeout} seconds{Colour.RESET}", end="\n\n")
    #     return -1

def do_action(packet, curr_player, opponent):
    ai_action = packet["action"]
    is_active = packet["is_active"]
    is_visible = packet["is_visible"]

    logout = False
    # print(f"{Colour.ORANGE}Performing action: {ai_action}{Colour.RESET}", end="\n\n")
    if ai_action == "shield":
        shield_command(curr_player)
    elif ai_action == "gun":
        gun_command(curr_player, opponent, is_visible)
    elif ai_action == "reload":
        reload_command(curr_player)
    elif ai_action == "bomb":
        bomb_command(curr_player, opponent, is_visible)
    elif ai_action == "badminton":
        badminton_command(curr_player, opponent, is_visible)
    elif ai_action == "boxing":
        boxing_command(curr_player, opponent, is_visible)
    elif ai_action == "fencing":
        fencing_command(curr_player, opponent, is_visible)
    elif ai_action == "golf":
        golf_command(curr_player, opponent, is_visible)
    elif ai_action == "logout":
        logout = True # logout action or invalid action
    if ai_action != "bomb":
        snow_detection(curr_player, opponent, is_active)
    return logout

def create_message(action, curr_player_id, client_game_state):
    message = {
        "player_id": curr_player_id,
        "action": action,
        "game_state": {
            "p1": client_game_state.player1.get_dict(),
            "p2": client_game_state.player2.get_dict()
        }
    }
    return json.dumps(message)