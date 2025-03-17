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

def gun_command(curr_player, opponent, opponent_hit):
    curr_player.shoot(opponent, opponent_hit)

def reload_command(curr_player):
    curr_player.reload()

def bomb_command(curr_player, opponent, opponent_hit):
    curr_player.bomb(opponent, opponent_hit)

def badminton_command(curr_player, opponent, opponent_hit):
    curr_player.badminton(opponent, opponent_hit)

def boxing_command(curr_player, opponent, opponent_hit):
    curr_player.boxing(opponent, opponent_hit)

def fencing_command(curr_player, opponent, opponent_hit):
    curr_player.fencing(opponent, opponent_hit)

def golf_command(curr_player, opponent, opponent_hit):
    curr_player.golf(opponent, opponent_hit)

def snow_detection(curr_player, opponent, opponent_hit):
    curr_player.snowball_detection(opponent, opponent_hit)