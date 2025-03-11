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

    @classmethod
    def values(cls):
        return [cls.none, cls.badminton, cls.boxing, cls.bomb, cls.reload, cls.golf, cls.fencing, cls.shield, cls.logout, cls.shoot]
    
def shield_command(curr_player):
    curr_player.shield()

def gun_command(curr_player, opponent, see_opponent):
    curr_player.shoot(opponent, see_opponent)

def reload_command(curr_player):
    curr_player.reload()

def bomb_command(curr_player, opponent, see_opponent):
    curr_player.bomb(opponent, see_opponent)

def badminton_command(curr_player, opponent, see_opponent):
    curr_player.badminton(opponent, see_opponent)

def boxing_command(curr_player, opponent, see_opponent):
    curr_player.boxing(opponent, see_opponent)

def fencing_command(curr_player, opponent, see_opponent):
    curr_player.fencing(opponent, see_opponent)

def golf_command(curr_player, opponent, see_opponent):
    curr_player.golf(opponent, see_opponent)