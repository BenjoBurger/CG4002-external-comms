from random import Random
from utilities.Action import Action


dummy_packet1 = {
    "player_id": 1,
    "action": Action.shoot,
    "ir_data": 1,
    "gyro_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
    "accel_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
}

dummy_packet2 = {
    "player_id": 1,
    "action": Action.shield,
    "ir_data": 1,
    "gyro_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
    "accel_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
}

dummy_packet3 = {
    "player_id": 1,
    "action": Action.bomb,
    "ir_data": 1,
    "gyro_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
    "accel_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
}

dummy_packet4 = {
    "player_id": 1,
    "action": Action.badminton,
    "ir_data": 1,
    "gyro_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
    "accel_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
}

dummy_packet5 = {
    "player_id": 1,
    "action": Action.reload,
    "ir_data": 1,
    "gyro_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
    "accel_data": 
    {
        "x": Random().randint(0, 100),
        "y": Random().randint(0, 100),
        "z": Random().randint(0, 100),
    },
}

dummy_packet_list = [dummy_packet1, dummy_packet2, dummy_packet3, dummy_packet4, dummy_packet5]