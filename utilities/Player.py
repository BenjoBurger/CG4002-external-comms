class Player:
    def __init__(self, id):
        self.id = id

        self.max_bombs          = 2
        self.max_shields        = 3
        self.hp_bullet          = 5
        self.hp_AI              = 10
        self.hp_bomb            = 5
        self.hp_rain            = 5
        self.max_shield_health  = 30
        self.max_bullets        = 6
        self.max_hp             = 100

        self.hp = 100
        self.num_bullets = 6
        self.num_bombs = 2
        self.hp_shield = 0
        self.num_deaths = 0
        self.num_shield = 3

    def get_dict(self):
        data = dict()
        data['hp']              = self.hp
        data['bullets']         = self.num_bullets
        data['bombs']           = self.num_bombs
        data['shield_hp']       = self.hp_shield
        data['deaths']          = self.num_deaths
        data['shields']         = self.num_shield
        return data
    
    def set_dict(self, data):
        self.hp          = data['hp']
        self.num_bullets = data['bullets']
        self.num_bombs   = data['bombs']
        self.hp_shield   = data['shield_hp']
        self.num_deaths  = data['deaths']
        self.num_shield  = data['shields']

    def shoot(self, opponent, visible):
        if self.num_bullets > 0:
            self.num_bullets -= 1
            if visible:
                opponent.take_damage(self.hp_bullet)
            return "Player shot!"
        else:
            self.reload()

    def reload(self):
        self.bullets = 6
        return "Player reloaded!"

    def bomb(self, opponent, visible):
        if self.num_bombs > 0:
            self.num_bombs -= 1
            if visible:
                opponent.take_damage(self.hp_bomb)
            return "Player bombed!"
        else:
            return "Player has no bombs!"

    def shield(self):
        if self.num_shield > 0 and self.hp_shield != 30:
            self.num_shield -= 1
            self.hp_shield = 30
            return "Player shielded!"
        else:
            return "Player has no shields!"

    def badminton(self, opponent, visible):
        if visible:
            opponent.take_damage(self.hp_AI)
        return "Player used badminton!"

    def boxing(self, opponent, visible):
        if visible:
            opponent.take_damage(self.hp_AI)
        return "Player used boxing!"

    def fencing(self, opponent, visible):
        if visible:
            opponent.take_damage(self.hp_AI)
        return "Player used fencing"

    def golf(self, opponent, visible):
        if visible:
            opponent.take_damage(self.hp_AI)
        return "Player used golf!"

    def take_damage(self, damage):
        if self.hp_shield > 0:
            self.hp_shield -= damage
            if self.hp_shield < 0:
                self.hp += self.hp_shield
                self.shield_hp = 0
        else:
            self.hp -= damage
            if self.hp <= 0:
                # if we die, we spawn immediately
                self.num_deaths += 1

                # initialize all the states
                self.hp             = self.max_hp
                self.num_bullets    = self.max_bullets
                self.num_bombs      = self.max_bombs
                self.hp_shield      = 0
                self.num_shield     = self.max_shields