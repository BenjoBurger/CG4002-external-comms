import json
import os
import sys
import time
from random import Random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from relay_node.RelayClient import RelayClient 
from utilities.Colour import Colour
from utilities.Action import Action
from multiprocessing import Process, Queue, Value

# P1_PORT = 8000
# P2_PORT = 8002
SEND_PORT = 8000
RECV_PORT = 8080
user_action = [["shoot", "shot", "bomb", "badminton", "boxing", "fencing", "golf"],
                ["golf", "shoot", "bomb", "badminton", "boxing", "fencing", "golf"]]

def relay_client_process(server_ip, port_number, queue=None, check_client=None):
    if port_number == SEND_PORT:
        send_to_relay(server_ip, port_number, queue, check_client)
    else:
        recv_from_relay(server_ip, port_number, queue, check_client)

def send_to_relay(server_ip, port_number, action_queue, sending_client):
    relay_client = RelayClient(server_ip, port_number)
    print(f"{Colour.CYAN}Sending Relay Client Connected{Colour.RESET}", end="\n\n")
    if sending_client is not None:
        with sending_client.get_lock():
            sending_client.value = True
    try:
        while True:
            # Action data from internal comms
            data = action_queue.get()
            # print("Data: ", data)
            if data is not None:
                relay_client.send_message(json.dumps(data))
    except BrokenPipeError:
        while True:
            try:
                relay_client = RelayClient(server_ip, port_number)
                print(f"{Colour.CYAN}Relay Client Connected{Colour.RESET}", end="\n\n")
                break
            except Exception as e:
                print(f"{Colour.RED}Error in reconnecting: {e}{Colour.RESET}", end="\n\n")
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"{Colour.CYAN}Exiting Relay Client Process{Colour.RESET}", end="\n\n")
        relay_client.close()
    except Exception as e:
        print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
        raise e

def recv_from_relay(server_ip, port_number, queue, receiving_client):
    relay_client = RelayClient(server_ip, port_number)
    print(f"{Colour.CYAN}Receiving Relay Client Connected{Colour.RESET}", end="\n\n")
    if receiving_client is not None:
        with receiving_client.get_lock():
            receiving_client.value = True
    time.sleep(10)
    try:
        while True:
            try:
                # Receive data from relay server
                recv_data = relay_client.recv_message()
                if recv_data == "" or recv_data == "ping":
                    continue
                # print(f"{Colour.CYAN}Data received: {recv_data}{Colour.RESET}", end="\n\n")
                queue.put(recv_data)
            except Exception as e:
                print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
                raise e
    except BrokenPipeError:
        while True:
            try:
                relay_client = RelayClient(server_ip, port_number)
                print(f"{Colour.CYAN}Relay Client Connected{Colour.RESET}", end="\n\n")
                break
            except Exception as e:
                print(f"{Colour.RED}Error in reconnecting: {e}{Colour.RESET}", end="\n\n")
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"{Colour.CYAN}Exiting Relay Client Process{Colour.RESET}", end="\n\n")
        relay_client.close()
    except Exception as e:
        print(f"{Colour.RED}Error in relay_client_process: {e}{Colour.RESET}", end="\n\n")
        raise e
    
def action_input(beetle_to_relay, sending_client, receiving_client):
    while True:
        if sending_client.value and receiving_client.value:
            print(f"{Colour.GREEN}Relay Clients Connected{Colour.RESET}", end="\n\n")
            break
    time.sleep(10)
    while True:
        # continue
        for i in range(len(user_action[0])):
            for j in [1,2]:
                data = {
                    "player_id": j,
                    "gun_fired": False,
                    "IR_Sensor": 0,
                    "imu_data": user_action[j-1][i]
                    # "imu_data": [[4888, 64200, 4968, 33113, 64625, 32768, 17120, 1288, 812, 10854, 6295, 63663, 60928, 49856, 65124, 2087, 63210, 1867], [4888, 64200, 4968, 33113, 64625, 32768, 16952, 1428, 152, 6196, 5784, 64160, 62508, 50508, 1208, 3351, 63481, 63818], [4888, 64200, 4968, 33113, 64625, 32768, 16952, 1428, 152, 6196, 5784, 64160, 65260, 48596, 120, 62255, 3681, 61796], [59952, 50920, 57864, 58472, 554, 1473, 16072, 764, 576, 4635, 4638, 64474, 65260, 48596, 120, 62255, 3681, 61796], [60964, 49232, 58520, 59024, 1627, 5606, 16072, 764, 576, 4635, 4638, 64474, 65260, 48596, 120, 62255, 3681, 61796], [60964, 49232, 58520, 59024, 1627, 5606, 16072, 764, 576, 4635, 4638, 64474, 65260, 48596, 120, 62255, 3681, 61796], [61060, 47600, 59440, 63049, 2640, 7340, 14388, 2976, 2688, 62934, 61956, 3658, 65260, 48596, 120, 62255, 3681, 61796], [61092, 47680, 60044, 3092, 3844, 6550, 17472, 1324, 3000, 48263, 58593, 4855, 65260, 48596, 120, 62255, 3681, 61796], [61092, 47680, 60044, 3092, 3844, 6550, 17472, 1324, 3000, 48263, 58593, 4855, 63368, 48588, 3708, 60184, 56746, 64535], [59992, 50332, 61320, 7105, 4095, 5722, 16896, 63160, 600, 56525, 2198, 1616, 63368, 48588, 3708, 60184, 56746, 64535], [59088, 53196, 62004, 6845, 3123, 5526, 17164, 62700, 888, 5515, 8682, 63270, 63368, 48588, 3708, 60184, 56746, 64535], [61340, 53864, 61340, 4275, 3230, 3416, 17164, 62700, 888, 5515, 8682, 63270, 63368, 48588, 3708, 60184, 56746, 64535], [61340, 53864, 61340, 4275, 3230, 3416, 14864, 64880, 65452, 18883, 10209, 58926, 63368, 48588, 3708, 60184, 56746, 64535], [61540, 53476, 62056, 2002, 3464, 252, 13896, 884, 1088, 20584, 7592, 58932, 63368, 48588, 3708, 60184, 56746, 64535], [61424, 53032, 62392, 559, 3178, 64503, 13972, 2712, 2456, 12970, 2075, 62590, 63368, 48588, 3708, 60184, 56746, 64535], [61424, 53032, 62392, 559, 3178, 64503, 13972, 2712, 2456, 12970, 2075, 62590, 63368, 48588, 3708, 60184, 56746, 64535], [61424, 53032, 62392, 559, 3178, 64503, 16160, 1540, 1344, 5401, 1729, 136, 63368, 48588, 3708, 60184, 56746, 64535], [61964, 52304, 62608, 63082, 2067, 62584, 16992, 248, 1576, 7360, 1377, 65500, 63368, 48588, 3708, 60184, 56746, 64535], [61964, 52304, 62608, 63082, 2067, 62584, 16992, 248, 1576, 7360, 1377, 65500, 63368, 48588, 3708, 60184, 56746, 64535], [63184, 51384, 62444, 60658, 603, 60712, 16612, 220, 1868, 8547, 63800, 65523, 64968, 50672, 4564, 63519, 56459, 63165], [63536, 51296, 62176, 60909, 659, 60892, 16004, 1536, 2580, 5747, 63336, 1620, 64968, 50672, 4564, 63519, 56459, 63165], [63940, 51008, 62684, 61096, 901, 61289, 16004, 1536, 2580, 5747, 63336, 1620, 308, 50152, 4404, 64584, 56687, 62984], [63940, 51008, 62684, 61096, 901, 61289, 16004, 1536, 2580, 5747, 63336, 1620, 2800, 49384, 2024, 160, 60259, 62488], [64608, 50868, 61988, 62180, 1848, 61730, 17872, 2452, 2568, 1656, 61933, 10789, 2800, 49384, 2024, 160, 60259, 62488], [65256, 50744, 61172, 62022, 3224, 61322, 17872, 2452, 2568, 1656, 61933, 10789, 65512, 49384, 3780, 121, 7369, 65409], [65256, 50744, 61172, 62022, 3224, 61322, 18132, 2328, 2684, 1476, 61931, 11538, 65512, 49384, 3780, 121, 7369, 65409], [4, 47884, 59792, 64283, 5260, 61537, 17948, 4380, 1920, 64719, 62025, 13359, 65512, 49384, 3780, 121, 7369, 65409], [65088, 47640, 59448, 642, 5553, 62144, 17552, 3612, 960, 62682, 64171, 5686, 65512, 49384, 3780, 121, 7369, 65409], [65088, 47640, 59448, 642, 5553, 62144, 17552, 3612, 960, 62682, 64171, 5686, 65512, 49384, 3780, 121, 7369, 65409], [64788, 49284, 60504, 64672, 5337, 64671, 17392, 3296, 768, 62437, 64739, 4008, 65512, 49384, 3780, 121, 7369, 65409], [65200, 47872, 59784, 63770, 5370, 64997, 16896, 2788, 65472, 62951, 3155, 63626, 380, 50344, 1300, 65064, 2273, 65347], [65200, 47872, 59784, 63770, 5370, 64997, 16896, 2788, 65472, 62951, 3155, 63626, 1008, 50032, 1784, 65241, 3098, 272], [65200, 47872, 59784, 63770, 5370, 64997, 15780, 4268, 784, 56487, 1801, 65157, 1008, 50032, 1784, 65241, 3098, 272], [63228, 55636, 65068, 8697, 7486, 2381, 15956, 3596, 65336, 49554, 166, 549, 1008, 50032, 1784, 65241, 3098, 272], [63228, 55636, 65068, 8697, 7486, 2381, 15956, 3596, 65336, 49554, 166, 549, 828, 49568, 1476, 64461, 3437, 706], [63936, 57352, 65292, 1310, 10130, 62566, 16040, 1968, 64988, 50185, 65155, 314, 828, 49568, 1476, 64461, 3437, 706], [64780, 53940, 63616, 51234, 13521, 50792, 17392, 1748, 65088, 54316, 430, 64643, 932, 49624, 1720, 64517, 3379, 726], [3328, 43172, 56116, 61653, 17061, 47882, 17392, 1748, 65088, 54316, 430, 64643, 932, 49624, 1720, 64517, 3379, 726], [3328, 43172, 56116, 61653, 17061, 47882, 17816, 1912, 65208, 59386, 1056, 62342, 932, 49624, 1720, 64517, 3379, 726], [3328, 43172, 56116, 61653, 17061, 47882, 18216, 2000, 64736, 63230, 2648, 59839, 932, 49624, 1720, 64517, 3379, 726], [6968, 52752, 52464, 59721, 1798, 56496, 17936, 1960, 64412, 63649, 2503, 59366, 932, 49624, 1720, 64517, 3379, 726], [6968, 52752, 52464, 59721, 1798, 56496, 17936, 1960, 64412, 63649, 2503, 59366, 932, 49624, 1720, 64517, 3379, 726], [2160, 45876, 48488, 43179, 46866, 60823, 16760, 2212, 65048, 62722, 622, 58129, 932, 49624, 1720, 64517, 3379, 726], [64396, 50740, 52120, 39550, 35116, 3150, 16656, 2188, 65024, 62307, 388, 58041, 932, 49624, 1720, 64517, 3379, 726], [64396, 50740, 52120, 39550, 35116, 3150, 16656, 2188, 65024, 62307, 388, 58041, 1320, 48980, 60, 64357, 5718, 64382], [57688, 55576, 52252, 45845, 36073, 63840, 16024, 1236, 64808, 58456, 455, 59318, 788, 48968, 65528, 64726, 5324, 64547], [55352, 60632, 55888, 49381, 32768, 65052, 15660, 808, 64840, 57062, 65082, 61934, 788, 48968, 65528, 64726, 5324, 64547], [64276, 45536, 64572, 60092, 43384, 49486, 15660, 808, 64840, 57062, 65082, 61934, 788, 48968, 65528, 64726, 5324, 64547], [64276, 45536, 64572, 60092, 43384, 49486, 15324, 800, 160, 56844, 62145, 132, 788, 48968, 65528, 64726, 5324, 64547], [3028, 60276, 64828, 18154, 17287, 51660, 16532, 1520, 836, 56509, 59615, 4952, 788, 48968, 65528, 64726, 5324, 64547], [7136, 43332, 46044, 48610, 32767, 57276, 17732, 2188, 1160, 54946, 60004, 7836, 65384, 50568, 1056, 2778, 65413, 2469], [7136, 43332, 46044, 48610, 32767, 57276, 17732, 2188, 1160, 54946, 60004, 7836, 65384, 50568, 1056, 2778, 65413, 2469], [63328, 48180, 41928, 17263, 46392, 11833, 18628, 1892, 312, 54466, 63537, 6899, 65384, 50568, 1056, 2778, 65413, 2469], [64872, 53308, 43540, 15062, 41938, 15387, 18628, 1892, 312, 54466, 63537, 6899, 65384, 50568, 1056, 2778, 65413, 2469], [176, 53168, 61412, 59987, 52693, 11625, 18628, 1892, 312, 54466, 63537, 6899, 65384, 50568, 1056, 2778, 65413, 2469], [176, 53168, 61412, 59987, 52693, 11625, 18512, 64896, 64384, 9569, 4785, 63989, 2368, 46848, 664, 1005, 63014, 333], [1768, 58056, 468, 2574, 11190, 5056, 17144, 1544, 64784, 15641, 2337, 170, 2328, 46772, 660, 1228, 63111, 206], [2616, 58116, 55712, 6445, 32065, 60787, 17144, 1544, 64784, 15641, 2337, 170, 2328, 46772, 660, 1228, 63111, 206], [2616, 58116, 55712, 6445, 32065, 60787, 17144, 1544, 64784, 15641, 2337, 170, 2328, 46772, 660, 1228, 63111, 206], [62240, 49340, 48292, 13739, 20448, 63235, 17004, 2628, 176, 2638, 65211, 1563, 2328, 46772, 660, 1228, 63111, 206], [64624, 57492, 51732, 62624, 3862, 1823, 17172, 2392, 1392, 3076, 9752, 62172, 2328, 46772, 660, 1228, 63111, 206], [64624, 57492, 51732, 62624, 3862, 1823, 17172, 2392, 1392, 3076, 9752, 62172, 2328, 46772, 660, 1228, 63111, 206], [64900, 56788, 52292, 59909, 3405, 2411, 16796, 2276, 2004, 8393, 12612, 58365, 2328, 46772, 660, 1228, 63111, 206], [1264, 53412, 53768, 8691, 13664, 1207, 16752, 2488, 2400, 9094, 13442, 57796, 2328, 46772, 660, 1228, 63111, 206]],
                }
                print("user_action: ", user_action[j-1][i])
                if user_action[j-1][i] == "shoot":
                    data["gun_fired"] = True
                elif user_action[j-1][i] == "shot":
                    data["IR_Sensor"] = 1
                beetle_to_relay.put(data)
                time.sleep(1)
            time.sleep(1)

if __name__ == "__main__":
    try:
        server_ip = input("Enter the server ip: ")
        if server_ip == "u96":
            server_ip = "172.26.191.109"
        if server_ip == "":
            server_ip = "localhost"
        
        beetle_to_relay = Queue()
        relay_to_beetle = Queue()

        sending_client = Value('b', True)
        receiving_client = Value('b', False)

        send_process = Process(target=relay_client_process, args=(server_ip, SEND_PORT, beetle_to_relay, sending_client))
        recv_process = Process(target=relay_client_process, args=(server_ip, RECV_PORT, relay_to_beetle, receiving_client))
        input_process = Process(target=action_input, args=(beetle_to_relay, sending_client, receiving_client))

        send_process.start()
        recv_process.start()
        input_process.start()
        # action_input(action_queue, sending_client, receiving_client)
        
        send_process.join()
        recv_process.join()
        input_process.join()

    except KeyboardInterrupt:
        print("Exiting")
        send_process.terminate()
        recv_process.terminate()
        input_process.terminate()
        sys.exit()