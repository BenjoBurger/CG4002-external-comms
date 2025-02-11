from Player import Player

class ClientGameState:
    def __init__(self):
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
    
    def __str__(self):
        return str(self.get_dict())

    def get_dict(self):
        data = {'p1': self.player1.get_dict(), 'p2': self.player2.get_dict()}
        return data

    def update_game_state(self, data):
        self.player1.set_dict(data['p1'])
        self.player2.set_dict(data['p2'])

