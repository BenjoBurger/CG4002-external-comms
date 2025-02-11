class Action:
    none        = "none"
    shoot       = "gun"
    shield      = "shield"
    bomb        = "bomb"
    reload      = "reload"
    badminton   = "badminton"
    golf        = "golf"
    fencing     = "fencing"
    boxing      = "boxing"
    logout      = "logout"

def shield_command(curr_player):
    curr_player.shield()

def gun_command(curr_player, opponent):
    curr_player.shoot(opponent, True)

def reload_command(curr_player):
    curr_player.reload()

def bomb_command(curr_player, opponent):
    curr_player.bomb(opponent, True)

def badminton_command(curr_player, opponent):
    curr_player.badminton(opponent, True)

def boxing_command(curr_player, opponent):
    curr_player.boxing(opponent, True)

def fencing_command(curr_player, opponent):
    curr_player.fencing(opponent, True)

def golf_command(curr_player, opponent):
    curr_player.golf(opponent, True)